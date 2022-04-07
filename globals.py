from xml.etree import ElementTree as ET
import os
import configparser

wufuzz_path = '/home/wulearn/Desktop/My-fuzz'

config = configparser.ConfigParser()
config.read(wufuzz_path + '/config/' + 'wufuzz.cfg')


target_rootfs_path = config.get('PATH', 'target_rootfs_path')
target_path = config.get('PATH', 'target_path')

base_folder_path = config.get('PATH', 'base_folder_path')
xml_file_path = base_folder_path + '/' + config.get('PATH', 'xml_file_name')
stack_chk_fail_file_path = base_folder_path + '/' + config.get('PATH', 'stack_chk_fail_file_name')
crash_index_path = base_folder_path + '/' + config.get('PATH', 'crash_index_name')

fuzz_out_dir_path = config.get('PATH', 'fuzz_out_dir_path')
data=[]

def init():
    global data
    global target_path
    global target_rootfs_path
    global xml_file_path
    global crash_index_path
    global fuzz_out_dir_path
    global stack_chk_fail_file_path
    data=parse_xml_init(xml_file_path)


def parse_xml_init(xml_file):
    xml_data=[]
    content=ET.parse(xml_file)
    root=content.getroot()
    for parameter in root.findall('PARAMETER'):
        ele_l=[]
        ele_cnt=0
        for ele in parameter.findall('ELEMENT'):
            ele_l.append(ele.text)
            ele_cnt+=1
        xml_data.append(parameter.find('NAME').text)
        xml_data.append(parameter.find('MUST').text)
        xml_data.append(ele_cnt)
        xml_data.append(ele_l)

    # for parameter in root.findall('PARAMETER'):
    #     ele_l=[]
    #     ele_cnt=0
    #     for ele_g in parameter.findall('ELEMENT_GROUP'):
    #         ele_g_data=[]
    #         for ele in ele_g.findall('ELEMENT'):
    #             ele_g_data.append(ele.text)
    #         ele_l.append(ele_g_data)
    #         ele_cnt+=1

    #     for ele in parameter.findall('ELEMENT'):
    #         ele_l.append(ele.text)
    #         ele_cnt+=1
    #     xml_data.append(parameter.find('NAME').text)
    #     xml_data.append(parameter.find('MUST').text)
    #     xml_data.append(ele_cnt)
    #     xml_data.append(ele_l)    

    return xml_data
