# coding: utf-8
import sys
import argparse
import datetime
import xml.etree.cElementTree as ET

from modules.excel_parse import AnalyExcel
from modules.zbx_helper import CreateTemplatesZone, CreateTriggersZone, CreateGroupsZone, CreateHostsZone


def create_template_file(excel_name, template_file_name):
    # 解析Excel文件
    excel_object = AnalyExcel(excel_name)
    sheets = excel_object.get_sheet_names()[:-1]
    # 创建xml基本框架
    create_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    root = ET.Element('zabbix_export')
    top_level_version = ET.SubElement(root, 'version')
    top_level_version.text = '2.0'
    top_level_date = ET.SubElement(root, 'date')
    top_level_date.text = create_time
    top_level_names = ['groups', 'applications', 'templates', 'triggers']
    for tags_name in top_level_names:  # 创建一级标签
        ET.SubElement(root, tags_name)
    # 创建templates域、triggers域
    templates = root.find('templates')
    templates_obj = CreateTemplatesZone(templates, excel_object)
    triggers = root.find('triggers')
    triggers_obj = CreateTriggersZone(triggers, excel_object)
    for sheet_name in sheets:
        templates_obj.create_template(sheet_name)
        triggers_obj.create_common_trigger(sheet_name)
        triggers_obj.create_trigger(sheet_name)
    # 生成xml树并保存到文件中
    tree = ET.ElementTree(root)
    tree.write(template_file_name, encoding='utf-8', xml_declaration=True)
    print('Create Zabbix Template Successfully...')


def create_host_file(excel_name, host_file_name):
    # 解析Excel文件
    excel_object = AnalyExcel(excel_name)
    # 创建xml基本框架
    create_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    root = ET.Element('zabbix_export')
    top_level_version = ET.SubElement(root, 'version')
    top_level_version.text = '2.0'
    top_level_date = ET.SubElement(root, 'date')
    top_level_date.text = create_time
    top_level_names = ['groups', 'hosts']
    for tags_name in top_level_names:  # 创建一级标签
        ET.SubElement(root, tags_name)
    # 创建groups域
    groups_node = root.find('groups')
    groups_obj = CreateGroupsZone(groups_node, excel_object)
    groups_obj.create_groups()
    # 创建hosts域
    hosts_node = root.find('hosts')
    hosts = CreateHostsZone(hosts_node, excel_object)
    hosts.create_hosts()
    # 生成xml树并保存到文件中
    tree = ET.ElementTree(root)
    tree.write(host_file_name, encoding='utf-8', xml_declaration=True)
    print('Create Zabbix Hosts Template Successfully...')


def main():
    parser = argparse.ArgumentParser(description='该程序根据Excel文件生成zabbix模板xml文件。',
                                     usage='%(prog)s [-T Name] [-H Name] excel_name')
    parser.add_argument('excel_name', help='Excel文件名称')
    parser.add_argument('-T', '--template', help='zabbix模板文件名称')
    parser.add_argument('-H', '--host', help='zabbix主机模板文件名称')
    if len(sys.argv) == 1:
        print(parser.print_help())
        sys.exit(0)
    else:
        args = parser.parse_args()

    if args.template and not args.host:
        create_template_file(args.excel_name, args.template)
    elif args.host and not args.template:
        create_host_file(args.excel_name, args.host)
    elif args.template and args.host:
        create_template_file(args.excel_name, args.template)
        create_host_file(args.excel_name, args.host)


if __name__ == '__main__':
    main()