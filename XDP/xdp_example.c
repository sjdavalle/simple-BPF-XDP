#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>

BPF_DEVMAP(tx_port, 1);
BPF_PERCPU_ARRAY(rxcnt, long, 1);

static inline void swap_src_dst_mac(void *data)
{
    unsigned short *p = data;
    unsigned short dst[3];
    dst[0] = p[0];
    dst[1] = p[1];
    dst[2] = p[2];
    p[0] = p[3];
    p[1] = p[4];
    p[2] = p[5];
    p[3] = dst[0];
    p[4] = dst[1];
    p[5] = dst[2];
}

int xdp_redirect_map(struct xdp_md *ctx)
{
    void* data_end = (void*)(long)ctx->data_end;
    void* data = (void*)(long)ctx->data;

    struct ethhdr *eth = data;
    uint32_t key = 0;
    long *value;

    // next header offset
    uint64_t nh_off = sizeof(struct ethhdr);

    // boundary check is mandatory by BPF verfier.
    if (data + nh_off  > data_end)
        return XDP_DROP;

    value = rxcnt.lookup(&key);

    if (value)
        *value += 1;

    swap_src_dst_mac(data);

    // This redirects the incoming packets based on the index entry.
    // If the map is BPF_DEVMAP, the packet will be sent to the transmit queue of the network interface that the entry points to.
    // If the packet is redirected successfully, the function will return XDP_REDIRECT.
    // Otherwise, it will return XDP_ABORTED to discard the packet.
    return tx_port.redirect_map(0, 0);
}

int xdp_dummy(struct xdp_md *ctx)
{
    return XDP_PASS;
}