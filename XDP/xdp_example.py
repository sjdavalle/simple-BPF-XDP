from bcc import BPF
import pyroute2
import time
import sys
import ctypes as ct
from time import sleep

def usage():
    print("Usage: {0} <in ifdev> <out ifdev>".format(sys.argv[0]))
    print("e.g.: {0} eth0 eth1\n".format(sys.argv[0]))
    exit(1)

def example(in_if: str, out_if: str) -> None:
    flags = 0
    ip = pyroute2.IPRoute()
    out_idx = ip.link_lookup(ifname=out_if)[0]

    try:
        bpf = BPF(src_file="xdp_example.c", cflags=["-w"])
        tx_port = bpf.get_table("tx_port")
        tx_port[0] = ct.c_int(out_idx)

        in_fn = bpf.load_func("xdp_redirect_map", BPF.XDP)
        out_fn = bpf.load_func("xdp_dummy", BPF.XDP)

        bpf.attach_xdp(in_if, in_fn, flags)
        bpf.attach_xdp(out_if, out_fn, flags)


        rxcnt = bpf.get_table("rxcnt")
        prev = 0
        print("Printing redirected packets, hit CTRL+C to stop")
        while 1:
            try:
                val = rxcnt.sum(0).value
                if val:
                    delta = val - prev
                    prev = val
                    print("{} pkt/s".format(delta))
                time.sleep(1)
            except KeyboardInterrupt:
                print("Removing filter from device")
                break
        bpf.remove_xdp(in_if, flags)
        bpf.remove_xdp(out_if, flags)

    except Exception as ex:
        print(f"Exception while load XDP code: pformat{ex}")
        sleep(10)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()

    in_if = sys.argv[1]
    out_if = sys.argv[2]
    example(in_if, out_if)
