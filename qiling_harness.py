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
crash_info=""
env_name_list=[]

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
        index=f.read()
    #TODO auto get path
    path = globals.fuzz_out_dir_path+'/info/total_crashes/'+index+'.txt'
    with open(path, 'a') as f:
        f.write(crash_info)
    with open(globals.crash_index_path, 'w') as f:
        f.write(str(int(index)+1))
    crash_info=""

def main(input_file, enable_trace=False):

    # globals.data=[NAME_1, MUST_1, ELE_CNT_1, ELE_LIST_1, NAME_2, ...]
    globals.init()
    # TODO auto got
    with open(globals.stack_chk_fail_file_path,'r') as f:
        stack_chk_fail_address=f.read()


    #init crash_info
    with open(globals.crash_index_path, 'w') as f:
        f.write("1")

    env_vars = {}
    for i in range(0, len(globals.data), 4):
        if globals.data[i+1] == 'T':
            env_vars[globals.data[i]] = globals.data[i+3][0] +b'\x00'.decode()+"A"*0x1000
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
    ql = Qiling([globals.target_path], globals.target_rootfs_path,
                verbose=QL_VERBOSE.DEBUG, env=env_vars,
                console=True if enable_trace else False)
    # mock_stdin=pipe.SimpleInStream(sys.stdin.fileno())
    # ql = Qiling([globals.target_path], globals.target_rootfs_path,
    #         verbose=QL_VERBOSE.DEBUG,
    #         stdin=mock_stdin,
    #         console=True if enable_trace else False)
    # ql.os.stdin = StringBuffer()

    ql.target_addr = {}
    address_total = 0
    for i in range(0, len(globals.data), 4):
        env_name=globals.data[i]
        env_name_list.append(env_name)
        addr = ql.mem.search(env_name.encode()+("=").encode())
        ql.target_addr[address_total] = addr[0]
        address_total = address_total+1


    def place_input_callback(uc, input, _, data):
        global crash_info
        # buf = "GET /admin/network.cgi?iptype="+"zyw"*10 +" HTTP/1.1\r\n" #test
        # #buf = "GET /admin/network.cgi?iptype="+"zyw"*10 +" HTTP/1.1\r\n" #crash
        # buf+="Accept-Encoding: " + "zyw"*1000 + "\r\n"
        # #buf+= "Host: 192.168.10.30\n"
        # #buf+="Proxy-Connection: keep-alive\r\n"
        # buf+="Authorization: Basic YWRtaW46YWRtaW4=\r\n\r\n" #admin admin
        # length=ql.os.stdin.write(buf.encode())
        # addr1 = ql.mem.search("CONTENT_LENGTH=".encode())
        # ql.c_l_addr = addr1[0]
        # ql.mem.write(ql.c_l_addr, ("CONTENT_LENGTH=").encode() +
        #              str(length).encode()+b"\x00")
        # reset_value()
        # print("HI")
        for i in range(address_total):
            random.seed()
            wrint_in_mem_l=(globals.data[4*i]).encode()+("=").encode()
            choose_ele=globals.data[(4*i)+3][random.randint(0, globals.data[(4*i)+2]-1)]
            wrint_in_mem_r=choose_ele.encode()
            change_index=choose_ele.find("@@")
            if i < address_total-1:
                crash_info=crash_info+wrint_in_mem_l.decode()+wrint_in_mem_r.decode()+'\n'
            else:
                crash_info=crash_info+wrint_in_mem_l.decode()+wrint_in_mem_r.decode()
            if change_index != -1:
                wrint_in_mem_r=choose_ele[:change_index].encode()+input+choose_ele[change_index+2:].encode()
            # print(wrint_in_mem_l+wrint_in_mem_r+b"\x00")
            ql.mem.write(ql.target_addr[i], wrint_in_mem_l+wrint_in_mem_r+b"\x00")


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
    if stack_chk_fail_address!='-1':
        ql.hook_address(callback=abort_func,address=ba+int(stack_chk_fail_address,16))
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
