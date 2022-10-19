#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <linux/tcp.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>

#define MAC_ADDRESS_LEN 6
#define FALSE 0
#define TRUE 1

struct config_t {
    unsigned char target_mac[MAC_ADDRESS_LEN];
};

BPF_ARRAY(config, struct config_t, 1);
BPF_HISTOGRAM(tcp_packets_counter, __u64);

static __always_inline int monitor_mac(struct ethhdr* eth_header, unsigned char* target_mac)
{
    if(target_mac == NULL)
    {
        return FALSE;
    }
    unsigned char* current_mac = eth_header->h_source;

    for (int i = 0; i < MAC_ADDRESS_LEN; i++)
    {
        if (target_mac[i] != current_mac[i])
        {
            return FALSE;
        }
    }
    return TRUE;
}

int tcp_counter(struct xdp_md *ctx)
{
    struct iphdr* ip_header;
    struct udphdr* udp_header;
    struct tcphdr* tcp_header;
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    struct ethhdr *eth = data;

    // next header offset
    uint64_t nh_off = sizeof(struct ethhdr);

    // Protocol
    __u16 h_proto;

    // boundary check is mandatory by BPF verfier.
    if (data + nh_off  > data_end)
    {
        bpf_trace_printk("Invalid DATA!\n");
        return XDP_DROP;
    }
    else
    {
        h_proto = eth->h_proto;           
        if (h_proto == bpf_htons(ETH_P_IP))
        {
            ip_header = data + nh_off;
            if (ip_header + 1 > data_end)
            {
                bpf_trace_printk("IP header not found!\n");
                return XDP_DROP;
            }
            
            if (ip_header->protocol == IPPROTO_TCP)
            {
                // Boundary check for UDP
                nh_off += sizeof(struct iphdr);
                tcp_header = data + nh_off;

                if (tcp_header + 1 > data_end)
                {
                    bpf_trace_printk("Malformed TCP header\n");
                    return XDP_DROP;
                }
                else
                {
                    int index = 0;
                    struct config_t* current_config = config.lookup(&index);
                    if(monitor_mac(eth, current_config->target_mac))
                    {
                        const __u64 value = bpf_htons(tcp_header->dest);
                        tcp_packets_counter.increment(value);
                        bpf_trace_printk("packet arrived!\n");
                    }
                }
            }
        }
    }
    return XDP_PASS;
}