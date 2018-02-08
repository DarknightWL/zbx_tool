# coding: utf-8
from modules.utils import f_str2int


def get_item_dict(value_list):
    """
    返回item域的节点名称及值的字典
    """
    node_dict = {'name': value_list[0], 'type': 7, 'multiplier': 0, 'snmp_oid': None, 'key': value_list[1],
                     'delay': 3600, 'history': 15, 'trends': 365, 'status': 0, 'value_type': 3, 'allowed_hosts': None,
                     'units': 'B', 'delta': 0, 'snmpv3_tontexname': None, 'snmpv3_securityname': None,
                     'snmpv3_securitylevel': 0, 'snmpv3_authprotocol': 0, 'snmpv3_authpassphrase': None,
                     'snmpv3_privprotocol': 0, 'snmpv3_privpassphrase': None, 'formula': 1, 'delay_flex': None,
                     'params': None, 'ipmi_sensor': None, 'data_type': 0, 'authtype': 0, 'username': None,
                     'password': None, 'publickey': None, 'privatekey': None, 'port': None, 'description': None,
                     'inventory_link': 0, 'applications': value_list[2], 'valuemap': None}
    return node_dict


def get_common_trigger_dict(template_name, trigger_type, set_value, lower, upper, dependency=True):
    """
    :param template_name: 模板名称
    :param trigger_type: 触发器类型
    :param set_value: 阈值
    :param lower: 较低阈值
    :param upper: 较高阈值
    :param dependency: 是否存在依赖项
    :return: trigger域节点名称及值的字典
    """
    node_dict = dict()
    priority_level = 0
    if set_value == lower:
        priority_level = 2
    elif set_value == upper:
        priority_level = 4

    if trigger_type == 'CPU':
        node_dict = {'expression': '{%s:system.cpu.util[all,avg1].min(#3)}&gt;%s' % (template_name, set_value),
                     'name': '{HOST.NAME}:CPU使用率超过%s%%' % set_value,
                     'url': None, 'status': 0, 'priority': priority_level,
                     'description': 'CPU使用率连续三次超过%s%%' % set_value, 'type': 0,
                     'dependencies': '{%s:system.cpu.util[all,avg1].min(#3)}&gt;%d' %(template_name, upper)
                    }
    elif trigger_type == 'MEM':
        node_dict = {'expression': '{%s:vm.memory.size[pused].min(#3)}&gt;%s' % (template_name, set_value),
                     'name': '{HOST.NAME}:内存使用率超过%s%%' % set_value,
                     'url': None, 'status': 0, 'priority': priority_level,
                     'description': '内存使用率连续三次超过%s%%' % set_value, 'type': 0,
                     'dependencies': '{%s:vm.memory.size[pused].min(#3)}&gt;%d' % (template_name, upper)
                    }

    if not dependency:
        node_dict['dependencies'] = None
    return node_dict


def get_trigger_dict(expression, name, priority=4):
    """
    :param expression: 触发器表达式
    :param name: 触发器名称
    :param priority: 告警级别
    :return: trigger域节点名称及值的字典
    """
    node_dict = {'expression': expression, 'name': name, 'url': None, 'status': 0, 'priority': priority,
                 'description': None, 'type': 1, 'dependencies': None
                 }
    return node_dict


def get_host_dicts(value_list):
    host_dict = {'host': value_list[1], 'name': value_list[1], 'proxy': value_list[5], 'status': 0,
                 'ipmi_authtype': -1, 'ipmi_privilege': 2, 'ipmi_username': None, 'ipmi_password': None,
                 'templates': value_list[4], 'groups': value_list[0], 'interfaces': True, 'applications': None,
                 'items': None, 'discovery_rules': None, 'macros': None, 'inventory': None}

    interface_dict = {'default': 1, 'type': 1, 'useip': 1, 'ip': value_list[2],
                      'dns': None, 'port': f_str2int(value_list[3]), 'interface_ref': 'if1'}
    return host_dict, interface_dict
