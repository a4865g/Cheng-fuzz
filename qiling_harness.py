#!/usr/bin/env python3

import os
import sys
import json
import globals
import random

import unicornafl
unicornafl.monkeypatch()

sys.path.append("/home/wulearn/qiling")
from qiling import *
from qiling.const import QL_VERBOSE
# from qiling.extensions import pipe


crash_info = ""
env_name_list = []
argc_value = 1

def change_argc(ql: Qiling):
    ql.reg.edi = argc_value

class StringBuffer:
    def __init__(self):
        self.buffer = b''

    def read(self, n):
        ret = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return ret

    def readline(self, end=b'\n'):
        ret = b''
        while True:
            c = self.read(1)
            ret += c
            if c == end:
                break
        return ret

    def write(self, string):
        self.buffer += string
        return len(string)

def update_crash_info():
    global crash_info
    with open(globals.crash_index_path,'r') as f:
        index = f.read()
    #TODO auto get path
    path = globals.fuzz_out_dir_path+'/info/total_crashes/'+index+'.txt'
    with open(path, 'a') as f:
        f.write(crash_info)
    with open(globals.crash_index_path, 'w') as f:
        f.write(str(int(index)+1))
    crash_info = ""

def main(input_file, enable_trace = False):

    # globals.argv_data=[MUST_1, ELE_CNT_1, ELE_LIST_1, NAME_2, ...]
    # globals.env_data=[NAME_1, MUST_1, ELE_CNT_1, ELE_LIST_1, NAME_2, ...]
    globals.init()
    
    with open(globals.stack_chk_fail_file_path,'r') as f:
        stack_chk_fail_address = f.read()

    with open(globals.target_main_file_path,'r') as f:
        target_main_address = f.read()

    #init crash_info
    with open(globals.crash_index_path, 'w') as f:
        f.write("1")

    argv_count_tmp = -1
    argv_vars = []
    argv_vars.append(globals.target_path)
    for i in range(0, len(globals.argv_data), 3):
        argv_count_tmp += 1
        if globals.argv_data[i] == 'true':
            argv_vars.append(b'\x00'.decode()+"VVuLeArn"+b'\x00'.decode()+"A"*100)
        else:
            argv_vars.append(b'\x00'.decode()+"VVuLeArn"+b'\x00'.decode()+"A"*100)
    
    env_vars = {}
    for i in range(0, len(globals.env_data), 4):
        if globals.env_data[i+1] == 'true':
            env_vars[globals.env_data[i]] = globals.env_data[i+3][0] +b'\x00'.decode()+"A"*0x1000
        else:
            env_vars[globals.env_data[i]] = b'\x00'.decode()+"A"*0x1000

    # env_vars = {
    #     "REQUEST_METHOD": "POST",
    #     "REQUEST_URI": "/hedwig.cgi",
    #     "CONTENT_TYPE": "application/x-www-form-urlencoded",
    #     "REMOTE_ADDR": "127.0.0.1",
    #     "HTTP_COOKIE": "uid=1234&password="+"A" * 0x0f,  # fill up
    #     # "CONTENT_LENGTH": "8", # no needed
    # }
    # env_vars = {
    # "REQUEST_METHOD": "GET",
    # "REQUEST_URI": "/admin/network.cgi?iptype="+"zyw"*2,
    # "CONTENT_TYPE": "application/x-www-form-urlencoded",
    # "Accept-Encoding":"zyw",
    # "Authorization": "Basic YWRtaW46YWRtaW4=\r\n\r\n",
    # # "CONTENT_LENGTH": "8", # no needed
    # }
    ql = Qiling(argv_vars, globals.target_rootfs_path,
                verbose=QL_VERBOSE.DEBUG, env=env_vars,
                console=True if enable_trace else False)
    # mock_stdin=pipe.SimpleInStream(sys.stdin.fileno())
    # ql = Qiling([globals.target_path], globals.target_rootfs_path,
    #         verbose=QL_VERBOSE.DEBUG,
    #         stdin=mock_stdin,
    #         console=True if enable_trace else False)
    # ql.os.stdin = StringBuffer()

    mem_argv = ql.mem.search(("VVuLeArn").encode())
    ql.argv_addr = {}
    argv_count = 0
    for i in range(argv_count_tmp, -1, -1):
        ql.argv_addr[argv_count] = mem_argv[i] - 1
        argv_count += 1

    ql.env_addr = {}
    env_count = 0
    for i in range(0, len(globals.env_data), 4):
        env_name=globals.env_data[i]
        env_name_list.append(env_name)
        addr = ql.mem.search(env_name.encode()+("=").encode())
        ql.env_addr[env_count] = addr[0]
        env_count += 1


    def place_input_callback(uc, input, _, data):
        global crash_info, argc_value

        for i in range(env_count):
            random.seed()
            wrint_in_mem_l=(globals.env_data[4*i]).encode()+("=").encode()
            choose_ele=globals.env_data[(4*i)+3][random.randint(0, globals.env_data[(4*i)+2]-1)]
            wrint_in_mem_r=choose_ele.encode()
            change_index=choose_ele.find("@@")
            if i < env_count-1:
                crash_info=crash_info+wrint_in_mem_l.decode()+wrint_in_mem_r.decode()+'\n'
            else:
                crash_info=crash_info+wrint_in_mem_l.decode()+wrint_in_mem_r.decode()
            if change_index != -1:
                wrint_in_mem_r=choose_ele[:change_index].encode()+input+choose_ele[change_index+2:].encode()
            # print(wrint_in_mem_l+wrint_in_mem_r+b"\x00")
            ql.mem.write(ql.env_addr[i], wrint_in_mem_l+wrint_in_mem_r+b"\x00")

        j = 0
        for i in range(argv_count):
            random.seed()
            if globals.argv_data[(3*i)] == 'false':
                if random.randint(0,1) == 0:
                    continue
            choose_ele = globals.argv_data[(3*i)+2][random.randint(0, globals.argv_data[(3*i)+1]-1)]
            crash_info = choose_ele + '\n'
            change_index = choose_ele.find("@@")
            if change_index != -1:
                in_mem = choose_ele[:change_index].encode()+(globals.fuzz_out_dir_path+"/.cur_input").encode()+choose_ele[change_index+2:].encode()
            else:
                in_mem = choose_ele.encode()
            ql.mem.write(ql.argv_addr[j], in_mem + b'\x00')
            j += 1
        argc_value = j + 1 # ./target
        #---------------------------------------------------------------
        
        # length = ql.os.stdin.write("A".encode())
        # print(length)
        # ql.mem.write(ql.c_l_addr, ("CONTENT_LENGTH=").encode() +
        #              str(length).encode()+b"\x00")
        # env_var = ("HTTP_COOKIE=uid=1234&password=").encode()
        # env_vars = env_var + input + b"\x00"
        # ql.mem.write(a, env_vars)
        #-----------------------------------------------------------------
    def abort_func(x):
        update_crash_info()
        os.abort()

    def place_crash_callback(uc, unicorn_result,input, _, data):
        update_crash_info()
        # global crash_info
        # path = '/home/wulearn/Desktop/crash.txt'
        # with open(path, 'a') as f:
        #     f.write(crash_info)
        # crash_info=""

    def start_afl(_ql: Qiling):
        """
        Callback from inside
        """
        # We start our AFL forkserver or run once if AFL is not available.
        # This will only return after the fuzzing stopped.
        try:
            print("Starting afl_fuzz().")
            if not _ql.uc.afl_fuzz(input_file=input_file,
                                   place_input_callback=place_input_callback,
                                   exits=[ql.os.exit_point],
                                   validate_crash_callback=place_crash_callback):
                print("Ran once without AFL attached.")
                os._exit(0)  # that's a looot faster than tidying up.
        except unicornafl.UcAflError as ex:
            # This hook trigers more than once in this example.
            # If this is the exception cause, we don't care.
            # TODO: Chose a better hook position :)
            if ex != unicornafl.UC_AFL_RET_CALLED_TWICE:
                raise
    main_addr = ql.os.elf_entry

    # get image base address
    ba = ql.loader.images[0].base

    # before main_address, EXEC start_afl
    ql.hook_address(callback=start_afl, address=main_addr)

    # hook stack_chk_fail
    if stack_chk_fail_address != '-1':
        ql.hook_address(callback = abort_func, address = ba + int(stack_chk_fail_address, 16))

    if target_main_address != '-1' and argv_count != 0:
        ql.hook_address(callback = change_argc, address = ba + int(target_main_address, 16)) #<=main address
    ql.add_fs_mapper("/home/wulearn/Desktop/My-fuzz/test_target/test_env/debug.txt","/home/wulearn/Desktop/My-fuzz/test_target/test_env/debug.txt")
    try:
        ql.run()
        os._exit(0)
    except:
        if enable_trace:
            print("\nFuzzer Went Shit")
        os._exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise ValueError("No input file provided.")

    if len(sys.argv) > 2 and sys.argv[1] == "-t":
        main(sys.argv[2], enable_trace=True)
    else:
        main(sys.argv[1])
