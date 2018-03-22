# coding: utf-8
import re
import os
from modules.utils import f_str2int


BASEDIR = os.path.dirname(os.path.dirname(__file__))

xml_dir = '模板文件'
xml_path = os.path.join(BASEDIR, xml_dir)


def get_item_dict(item_type, value_list):
    """
    :param item_type: item类型
    :param value_list: item值列表
    :return: item各个节点名称及值的字典
    """
    node_dict = {'name': value_list[0], 'type': 7, 'multiplier': 0, 'snmp_oid': None, 'key': None,
                 'delay': 3600, 'history': 15, 'trends': 365, 'status': 0, 'value_type': 3, 'allowed_hosts': None,
                 'units': None, 'delta': 0, 'snmpv3_tontexname': None, 'snmpv3_securityname': None,
                 'snmpv3_securitylevel': 0, 'snmpv3_authprotocol': 0, 'snmpv3_authpassphrase': None,
                 'snmpv3_privprotocol': 0, 'snmpv3_privpassphrase': None, 'formula': 1, 'delay_flex': None,
                 'params': None, 'ipmi_sensor': None, 'data_type': 0, 'authtype': 0, 'username': None,
                 'password': None, 'publickey': None, 'privatekey': None, 'port': None, 'description': None,
                 'inventory_link': 0, 'applications': None, 'valuemap': None}
    if item_type == 'log':
        node_dict['name'] = value_list[0] + "警告日志"
        node_dict['key'] = 'log[&quot;{0}&quot;,&quot;{1}&quot;]'.format(value_list[-2], value_list[-1])
        node_dict['value_type'] = '2'
    elif item_type == 'process':
        node_dict['name'] = value_list[0] + "服务进程"
        node_dict['key'] = 'proc.num[{0},,,{1}]'.format(value_list[1], value_list[2])
    return node_dict


def get_trigger_dict(trigger_type, value_list, priority):
    """
    :param trigger_type: trigger关联的item类型
    :param value_list: trigger各节点的值
    :param priority: 告警级别
    :return: trigger各个节点名称及值的字典
    """
    node_dict = {'expression': None, 'name': None, 'url': None, 'status': 0, 'priority': priority,
                 'description': None, 'type': 1, 'dependencies': None
                 }
    if trigger_type == 'log':
        node_dict['expression'] = '(({{{0}:log[&quot;{1}&quot;,&quot;{2}&quot;].regexp(.*)}})#0)'.format(
            value_list[0], value_list[-2], value_list[-1]
        )
        node_dict['name'] = '{}服务发生警告日志'.format(value_list[3])
    elif trigger_type == 'process':
        node_dict['expression'] = '{{{0}:proc.num[{1},,,{2}].last()}}=0'.format(
            value_list[0], value_list[4], value_list[5]
        )
        node_dict['name'] = '{}服务进程不存在'.format(value_list[3])
    return node_dict


def get_host_dicts(value_list):
    host_dict = {'host': value_list[1]+'-'+value_list[3], 'name': value_list[1]+'-'+value_list[3],
                 'proxy': value_list[5], 'status': 0, 'ipmi_authtype': -1, 'ipmi_privilege': 2,
                 'ipmi_username': None, 'ipmi_password': None, 'templates': value_list[-1].split(';'),
                 'groups': value_list[0], 'interfaces': True, 'applications': None,
                 'items': None, 'discovery_rules': None, 'macros': None, 'inventory': None}
    interface_dict = {'default': 1, 'type': 1, 'useip': 1, 'ip': value_list[2],
                      'dns': None, 'port': f_str2int(value_list[4]), 'interface_ref': 'if1'}

    if value_list[6] == '应用':
        if value_list[3].strip():
            template_name = 'Template {0} {1}'.format(value_list[3], re.split('\d{2}', value_list[1])[0])
        else:
            template_name = 'Template {0} {1}'.format('ALL', re.split('\d{2}', value_list[1])[0])
        host_dict['templates'] = [template_name]
    return host_dict, interface_dict
