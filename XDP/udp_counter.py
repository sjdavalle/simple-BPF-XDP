from bcc import BPF #1

def udp_counter():
    device = "lo" #2
    b = BPF(src_file="udp_counter.c", cflags=["-I/usr/include", "-DUDP_PORT=6900", "-Wno-compare-distinct-pointer-types"]) #3
    fn = b.load_func("udp_counter", BPF.XDP) #4
    b.attach_xdp(device, fn, 0) #5

    try:
        b.trace_print() #6
    except KeyboardInterrupt: #7

        dist = b.get_table("counter") #8
        for k, v in dist.items(): #9
            print(f"DEST_PORT : {k.value} COUNT : {v.value}") #10

    b.remove_xdp(device, 0) #11

if __name__ == "__main__":
    udp_counter()

"""
Steps explained:

1. Import the BPF python lib.
2. Specify which device you want your eBPF code to get attached to.
3. Create the BPF object and load the file.
4. Load the function.
5. Attach the function to the xdp hook of the device that was specified earlier.
6. Read the trace_pipe file so we can trace what's happening.
7. Catch the exit signal so we can exit gracefully.
8. Get the contents of the histogram.
9. Iterate over the content.
10. Print the results.
11. Deattach our code from the device.

Send some UDP to the NIC

nc -l -u 6900
nc -u localhost 6900

"""