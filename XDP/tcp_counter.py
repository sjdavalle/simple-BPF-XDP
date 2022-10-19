import binascii
from ctypes import create_string_buffer
from time import sleep
from bcc import BPF

def tcp_counter():
    # the NIC we are inspecting
    device = "enp0s3"
    # the mac address we want to filter/count packets from
    host_mac = "1c:1b:b5:7a:92:39" 
    
    b = BPF(src_file="tcp_counter.c", cflags=["-I/usr/include", "-Wno-compare-distinct-pointer-types"])
    fn = b.load_func("tcp_counter", BPF.XDP)
    b.attach_xdp(device, fn, 0)

    try:      
        config = b.get_table("config")
        config[0] = create_string_buffer(binascii.unhexlify(host_mac.replace(':', '')),6)
        # b.trace_print()

        while True:
            sleep(5)
            dist = b.get_table("tcp_packets_counter")
            for k, v in dist.items():
                # Get stats from kernel map.
                print(f"PORT : {k.value} COUNT : {v.value}") 

    except KeyboardInterrupt:
        print("DONE!")

    b.remove_xdp(device, 0) 

if __name__ == "__main__":
    tcp_counter()