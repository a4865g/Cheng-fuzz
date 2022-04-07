#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import globals
import r2pipe

def get_parser():
    parser = argparse.ArgumentParser(
        description='Convert out_decompiler_XXX.txt to xml')
    parser.add_argument('-i', '--input', type=str,
                        required=True, help='intput file')
    parser.add_argument('-o', '--output', type=str,
                        required=True, help='output directory')
    return parser


def parse_txt_getenv(input, output_dir):
    env_list = []
    with open(input) as temp_f:
        datafile = temp_f.readlines()
    index = 1
    print("--- Parse .txt ---")
    for line in datafile:
        if 'getenv' in line:
            if '"' in line:
                tmp = line[line.find('"')+1:]
                env_name = tmp[0:tmp.find('"')]
                env_list.append(env_name)
                print(str(index) + '.\nLine : ' + line +
                      'getenv Value = ' + env_name + '\n')
                index = index+1
    print("--- End Parse ---\n")
    env_list = list(set(env_list))
    print('ENV List:')
    print(env_list)
    print('\nENV Total: '+str(len(env_list)))

    if output_dir.rfind("/") != len(output_dir)-1:
        output_dir = output_dir+"/"
    output_dir = output_dir+"parse_" + \
        input[input.rfind('/')+1:input.rfind('.')]+".xml"

    out_f = open(output_dir, 'w')
    out_f.write("<root>\n")
    for value in env_list:
        out_f.write("  <PARAMETER>\n")
        out_f.write("    <NAME>"+value+"</NAME>\n")
        out_f.write("    <MUST>"+"T"+"</MUST>\n")
        out_f.write("    <ELEMENT>"+"default"+"</ELEMENT>\n")
        out_f.write("  </PARAMETER>\n")
    out_f.write("</root>\n")
    out_f.close()
    print("\nStored in "+output_dir+"\n\n")

def store_stack(output_dir):
    input=globals.target_path
    print("--- Parse stack_check_fail ---")
    r2 = r2pipe.open(input,flags=["-e","bin.cache=true"])
    r2.cmd("aa")
    cgi_func_list=r2.cmd("afl")
    print(cgi_func_list)
    r2.quit()

    def parse_stack():
        cgi_func = " ".join(cgi_func_list.splitlines())
        cgi_func_num=cgi_func.split()
        for i in range(0,len(cgi_func_num)):
            if "stack_chk_fail" in cgi_func_num[i]:
                print("Got "+ cgi_func_num[i] + " In:\n")
                for j in range(i,0,-1):
                    if "0x" in cgi_func_num[j]:
                        print(cgi_func_num[j]+"\n")
                        return cgi_func_num[j]
        print("Not got Stack_check_fail !!!\n")
        return "-1"

    store_data=parse_stack()

    if output_dir.rfind("/") != len(output_dir)-1:
        output_dir = output_dir+"/"
    output_dir = output_dir+"parse_stack_" + \
        input[input.rfind('/')+1:input.rfind('.')]+".txt"

    out_f = open(output_dir, 'w')
    out_f.write(store_data)
    out_f.close()
    print("--- End Parse ---\n")
    print("Stored in "+output_dir)
        

    

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    parse_txt_getenv(str(args.input), str(args.output))
    store_stack(str(args.output))
