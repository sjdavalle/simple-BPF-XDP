import os
from pprint import pformat
from bcc import BPF
from time import sleep

c_program_0 = """
    int infinite_loop(void* ctx)
    {
        while(1)
        {
            //Infinite Loop
        }
        return 0;
    }
"""
def bpf_example_infinite_loop(bpf_obj: BPF, event_name: str) -> None:
    print("This is not called, because the loading fails!!")
    bpf_obj.attach_kprobe(event=event_name, fn_name="infinite_loop")
    bpf_obj.trace_print()


c_program_1 = """
    int function_clone(void* ctx)
    {
        u64 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
        bpf_trace_printk("UserID: %d\\n", uid);
        return 0;
    }
"""
def bpf_example_clone_func(bpf_obj: BPF, event_name: str) -> None:
    bpf_obj.attach_kprobe(event=event_name, fn_name="function_clone")


c_program_2 = """

    BPF_HASH(users_table);

    int function_clone(void* ctx)
    {
        u64 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;

        u64* ptr_to_counter = users_table.lookup(&uid);

        u64 counter = ptr_to_counter != NULL ? ++(*ptr_to_counter) : 1;

        users_table.update(&uid, &counter);

        return 0;
    }
"""
def bpf_example_maps(bpf_obj: BPF, event_name: str) -> None:
    bpf_obj.attach_kprobe(event=event_name, fn_name="function_clone")
    try:
        while True:
            sleep(2)
            if bpf["users_table"].items():
                for user, count in bpf["users_table"].items():
                    print(f"ID: {user.value} - Count: {count.value}")
            else:
                print("Nothing yet!")
    except:
        pass


c_program_3 = """
    int function_clone(void* ctx)
    {
        #ifdef INCLUIT
            bpf_trace_printk("Value: %d\\n", VALUE);
        #else
            bpf_trace_printk("Hello!\\n");
        #endif
        return 0;
    }
"""
def bpf_example_cflags(bpf_obj: BPF, event_name: str) -> None:
    bpf_obj.attach_kprobe(event=event_name, fn_name="function_clone")
    bpf_obj.trace_print()



def bpf_task_switch() -> None:
    b = BPF(src_file="task_switch.c")

    event = "^finish_task_switch$|^finish_task_switch\.isra\.\d$"

    b.attach_kprobe(event_re=event,fn_name="count_sched")

    # generate many schedule events
    for i in range(0, 500): sleep(0.01)

    pid = os.getpid()

    for k, v in b["stats"].items():
        if pid == k.prev_pid or pid == k.curr_pid:
            print(f"-----------> task switch from our processs [{k.prev_pid}->{k.curr_pid}]={v.value}")
        else:
            print(f"task_switch[{k.prev_pid}->{k.curr_pid}]={v.value}")

    sleep(30)


if __name__ == "__main__":
    try:
        event_name = "__x64_sys_clone"
        # bpf = BPF(text=c_program_0)
        # bpf_example_infinite_loop(bpf, event_name)

        # bpf = BPF(text=c_program_1)
        # bpf_example_clone_func(bpf, event_name)

        # bpf = BPF(text=c_program_2)
        # bpf_example_maps(bpf, event_name)

        # bpf = BPF(text=c_program_3, cflags=["-DINCLUIT", "-DVALUE=123"])
        # bpf_example_cflags(bpf, event_name)

        bpf_task_switch()
    except KeyboardInterrupt:
        print("Interrupted!")
        #  bpf.detach_kprobe(event_name)
    except Exception as ex:
        print(pformat(ex))
        sleep(10)  # just to be able to see the error!.
