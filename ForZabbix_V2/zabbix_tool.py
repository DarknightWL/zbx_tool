# coding: utf-8
import os
import sys
import argparse
import datetime
import xml.etree.cElementTree as ET

from modules import conf
from modules.excel_parse import AnalyExcel
from modules.zbx_helper import create_common_node
from modules.zbx_helper import CreateTemplatesZone, CreateTriggersZone
from modules.zbx_helper import CreateHostsZone, CreateGroupsZone


def create_template_file(excel_name):
    # 解析Excel文件
    excel_object = AnalyExcel(excel_name)
    sheet_names = excel_object.get_sheet_names()
    for sheet_name in sheet_names:
        sheet = excel_object.get_sheet(sheet_name)
        # 创建xml基本框架
        create_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        root = ET.Element('zabbix_export')
        top_level_version = ET.SubElement(root, 'version')
        top_level_version.text = '2.0'
        top_level_date = ET.SubElement(root, 'date')
        top_level_date.text = create_time
        top_level_names = ['groups', 'templates', 'triggers']
        for tags_name in top_level_names:  # 创建一级标签
            ET.SubElement(root, tags_name)
        # groups节点
        groups_node = root.find('groups')
        create_common_node(groups_node, 'group', 'template')
        # 创建templates域
        templates_node = root.find('templates')
        templates_obj = CreateTemplatesZone(templates_node, sheet)
        templates_obj.create_templates()
        # 创建triggers域
        triggers_node = root.find('triggers')
        triggers_obj = CreateTriggersZone(triggers_node, sheet)
        triggers_obj.create_triggers()
        # 生成xml树并保存到文件中
        tree = ET.ElementTree(root)
        template_file_name = 'zbx_export_templates_{}.xml'.format(sheet_name)
        template_file_path = os.path.join(conf.xml_path, template_file_name)
        tree.write(template_file_path, encoding='utf-8', xml_declaration=True)
        print('Create {} Successfully...'.format(template_file_name))


def create_host_file(excel_name):
    # 解析Excel文件
    excel_object = AnalyExcel(excel_name)
    sheet_names = excel_object.get_sheet_names()
    for sheet_name in sheet_names:
        sheet = excel_object.get_sheet(sheet_name)
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
        groups_obj = CreateGroupsZone(groups_node, sheet)
        groups_obj.create_groups()
        # 创建hosts域
        hosts_node = root.find('hosts')
        hosts = CreateHostsZone(hosts_node, sheet)
        hosts.create_hosts()
        # 生成xml树并保存到文件中
        tree = ET.ElementTree(root)
        host_file_name = 'zbx_export_hosts_{}.xml'.format(sheet_name)
        host_file_path = os.path.join(conf.xml_path, host_file_name)
        tree.write(host_file_path, encoding='utf-8', xml_declaration=True)
        print('Create {} Successfully...'.format(host_file_name))


def main():
    parser = argparse.ArgumentParser(description='该程序根据Excel文件生成zabbix模板xml文件。',
                                     usage='%(prog)s excel_name')
    parser.add_argument('excel_name', help='Excel文件名称')
    if len(sys.argv) == 1:
        print(parser.print_help())
        sys.exit(0)
    else:
        args = parser.parse_args()
    create_host_file(args.excel_name)
    create_template_file(args.excel_name)


if __name__ == '__main__':
    main()
