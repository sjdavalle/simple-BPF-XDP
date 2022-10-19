#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <linux/tcp.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>


BPF_HISTOGRAM(counter, __u64);

int udp_counter(struct xdp_md *ctx)
{
    struct iphdr* ip_header;
    struct udphdr* udp_header;
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
            
            if (ip_header->protocol == IPPROTO_UDP)
            {
                // Boundary check for UDP
                nh_off += sizeof(struct iphdr);

                if (data + nh_off + sizeof(struct udphdr) > data_end)
                {
                    bpf_trace_printk("Malformed UDP header\n");
                    return XDP_PASS;
                }
                else
                {
                    udp_header = data + nh_off;
                    __u64 value = bpf_htons(udp_header->dest);

                    unsigned char *payload = (unsigned char *)udp_header + sizeof(struct udphdr);
#ifdef UDP_PORT
                    if (value == UDP_PORT)
                    {
                        counter.increment(value);
                        bpf_trace_printk("UDP packet intercepted! -> payload= %s\n", payload);
        
                    }
#else
                    bpf_trace_printk("UDP port not defined!\n");
#endif
                }
            }
        }
    }
    return XDP_PASS;
}