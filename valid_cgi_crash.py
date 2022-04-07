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

def main(input_file, enable_trace=False):

    # globals.data=[NAME_1, MUST_1, ELE_CNT_1, ELE_LIST_1, NAME_2, ...]
    # globals.init()
    # TODO auto got
    with open(globals.stack_chk_fail_file_path,'r') as f:
        stack_chk_fail_address=f.read()
    env_vars={}
    with open("/home/wulearn/Desktop/test_config/default/info/crashes/id:000000,sig:06,src:000010,time:601717,execs:71060,op:havoc,rep:2") as f:
        env_file=f.read()
    env_vars_list=env_file.split('\n')
    for i in range(len(env_vars_list)):
        tmp=env_vars_list[i][(env_vars_list[i].find("=")+1):]
        if "@@" in tmp:
            input_locate=tmp
        env_vars[env_vars_list[i][:env_vars_list[i].find("=")]]=tmp+b'\x00'.decode()+"A"*0x1000

    ql = Qiling([globals.target_path], globals.target_rootfs_path,
                verbose=QL_VERBOSE.DEBUG, env=env_vars,
                console=True if enable_trace else False)
    # mock_stdin=pipe.SimpleInStream(sys.stdin.fileno())
    # ql = Qiling([globals.target_path], globals.target_rootfs_path,
    #         verbose=QL_VERBOSE.DEBUG,
    #         stdin=mock_stdin,
    #         console=True if enable_trace else False)
    # ql.os.stdin = StringBuffer()

    input_addr=ql.mem.search(input_locate.encode())
    def place_input_callback(uc, input, _, data):
        global crash_info
        change_index=input_locate.find("@@")
        wrint_in_mem=input_locate[:change_index].encode()+input+input_locate[change_index+2:].encode()
        ql.mem.write(input_addr[0], wrint_in_mem+b"\x00")

    def abort_func(x):
        print("stack_chk_fail!!!")
        os.abort()

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
                                   exits=[ql.os.exit_point]):
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
