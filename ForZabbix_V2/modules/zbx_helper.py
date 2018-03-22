# coding: utf-8
import re
import xml.etree.cElementTree as ET
from modules.excel_parse import AnalySheet
from modules.utils import int2str
from modules import conf


def create_common_node(parent_node, new_node_name, *sub_node_value):
    """
    common类型节点：
    1、parent_node节点名称是new_node节点名称的复数
    2、new_node节点下仅有一个子节点name
    """
    for item in sub_node_value:
        new_node = ET.SubElement(parent_node, new_node_name)
        sub_node = ET.SubElement(new_node, 'name')
        sub_node.text = item
    return


class CreateGroupsZone(object):
    """
    创建zabbix主机模板中的groups域
    """
    def __init__(self, xml_node, sheet_obj):
        self.xml_node = xml_node
        self.sheet_obj = AnalySheet(sheet_obj)

    def __get_group_names(self):
        temp = set(self.sheet_obj.get_col_values(1, 2))
        names_temp = list(filter(lambda x: x, temp))
        group_names = []
        for item in names_temp:
            group_names.extend(item.split(';'))
        group_names = list(set(group_names))
        return group_names

    def create_groups(self):
        group_names = self.__get_group_names()
        create_common_node(self.xml_node, 'group', *group_names)
        return


class CreateHostsZone(object):
    """
    创建zabbix主机模板中的hosts域
    """
    def __init__(self, xml_node, sheet_obj):
        self.xml_node = xml_node
        self.sheet_obj = AnalySheet(sheet_obj)

    def __get_host_values(self, nrow, start_colx, end_colx):
        """
        :param nrow: 行号
        :param start_colx: 起始列
        :param end_colx: 结束列
        :return: host信息
        """
        return self.sheet_obj.get_row_values(nrow, start_colx, end_colx)

    def __get_hosts_values(self):
        hosts_values_dict = dict()
        group_name = ''
        service_type = ''
        used_template = ''
        for item in range(2, self.sheet_obj.sheet_nrow):
            temp = self.__get_host_values(item, 1, 9)
            temp[0], group_name = (group_name, group_name) if not temp[0] else (temp[0], temp[0])
            temp[-2], service_type = (service_type, service_type) if not temp[-2] else (temp[-2], temp[-2])
            temp[-1], used_template = (used_template, used_template) if not temp[-1] else (temp[-1], temp[-1])

            if hosts_values_dict.get(temp[1], None) is None:
                hosts_values_dict[temp[1]] = temp
        return hosts_values_dict

    @staticmethod
    def create_interface(parent_node, interface_info_dict):
        cur_node = ET.SubElement(parent_node, 'interface')
        for k, v in interface_info_dict.items():
            child_node = ET.SubElement(cur_node, k)
            child_node.text = int2str(v)

    def create_host(self, parent_node, host_values):
        host_info_dict, interface_info_dict = conf.get_host_dicts(host_values)
        for k, v in host_info_dict.items():
            if k == 'proxy':
                proxy_node = ET.SubElement(parent_node, k)
                if not v.strip():
                    continue
                name_node = ET.SubElement(proxy_node, 'name')
                name_node.text = int2str(v)
            elif k == 'templates':
                templates_node = ET.SubElement(parent_node, k)
                for i in v:
                    i = i.strip()
                    create_common_node(templates_node, 'template', int2str(i))
            elif k == 'groups':
                groups_node = ET.SubElement(parent_node, k)
                if not v.strip():
                    continue
                v_list = v.split(';')
                for group_name in v_list:
                    create_common_node(groups_node, 'group', int2str(group_name))
            elif k == 'interfaces':
                interfaces_node = ET.SubElement(parent_node, k)
                self.create_interface(interfaces_node, interface_info_dict)
            else:
                child_node = ET.SubElement(parent_node, k)
                child_node.text = int2str(v)
        return

    def create_hosts(self):
        hosts_values_dict = self.__get_hosts_values()
        for host_values in hosts_values_dict.values():
            cur_node = ET.SubElement(self.xml_node, 'host')
            self.create_host(cur_node, host_values)
        return


class CreateTemplatesZone(object):
    """
    创建zabbix模板中的templates域
    """
    def __init__(self, xml_node, sheet_obj):
        self.xml_node = xml_node
        self.sheet_obj = AnalySheet(sheet_obj)

    def get_templates_values(self):
        all_values = []
        service_type = ''
        used_templates = ''
        for i in range(2, self.sheet_obj.sheet_nrow):
            # 获取值并处理
            values = self.sheet_obj.get_row_values(i, 7)
            if values[0] == '中间件':
                continue
            elif values.count('') == 7:
                continue
            values[0], service_type = (service_type, service_type) if not values[0] else (values[0], values[0])
            values[1], used_templates = (used_templates, used_templates) if not values[1] else (values[1], values[1])
            if values[3] == '' and values[4] == '':
                raise Exception('第{}行进程类型和进程关键字不能同时为空'.format(i+1))
            host_suffix = self.sheet_obj.get_cell_value(i, 4)
            if host_suffix.strip():
                template_name = 'Template {0} {1}'.format(self.sheet_obj.get_cell_value(i, 4),
                                                          re.split('\d{2}', self.sheet_obj.get_cell_value(i, 2))[0])
            else:
                template_name = 'Template {0} {1}'.format('ALL',
                                                          re.split('\d{2}', self.sheet_obj.get_cell_value(i, 2))[0])
            values.insert(0, template_name)
            all_values.append(values)
        return all_values

    def create_template(self, template_values):
        """
        根据sheet页创建模板
        :param template_values: template各节点的值
        """
        parent_node = ET.SubElement(self.xml_node, 'template')
        # template节点
        template_node = ET.SubElement(parent_node, 'template')
        template_node.text = template_values[0]
        # name节点
        name_node = ET.SubElement(parent_node, 'name')
        name_node.text = template_values[0]
        # groups节点
        groups_node = ET.SubElement(parent_node, 'groups')
        create_common_node(groups_node, 'group', 'template')
        # applications节点
        applications_node = ET.SubElement(parent_node, 'applications')
        # items节点
        items_node = ET.SubElement(parent_node, 'items')
        items = CreateItem(items_node, template_values[3:])
        items.create_items()
        # 其他无值节点
        discovery_rules_node = ET.SubElement(parent_node, 'discovery_rules')
        macros_node = ET.SubElement(parent_node, 'macros')
        # 父模版节点
        parent_template_values_temp = template_values[2].split(';')
        parent_template_values = [x.strip() for x in parent_template_values_temp]
        templates_node = ET.SubElement(parent_node, 'templates')
        if len(parent_template_values_temp) == 1 and parent_template_values_temp[0] == '':
            pass
        else:
            create_common_node(templates_node, 'template', *parent_template_values)
        screens_node = ET.SubElement(parent_node, 'screens')
        return

    def create_templates(self):
        templates_values = self.get_templates_values()
        for template_values in templates_values:
            self.create_template(template_values)


class CreateItem(object):
    def __init__(self, parent_node, item_values):
        """
        :param parent_node: 父节点
        :param item_values: item各节点的值
        """
        self.parent_node = parent_node
        self.item_values = item_values

    def create_items(self):
        if self.item_values[1] != '' or self.item_values[2] != '':
            self.create_item('process')
        if self.item_values[-2] != '':
            self.create_item('log')
        return

    def create_item(self, item_type):
        node_dict = conf.get_item_dict(item_type, self.item_values)
        new_node = ET.SubElement(self.parent_node, 'item')
        for k, v in node_dict.items():
            if k == 'applications':
                app_node = ET.SubElement(new_node, k)
            else:
                child_node = ET.SubElement(new_node, k)
                if type(v) is int:
                    v = str(v)
                child_node.text = v
        return


class CreateTriggersZone(CreateTemplatesZone):
    """
    创建zbbix模板中的trigger域
    """
    def __init__(self, xml_node, sheet_obj):
        super(CreateTriggersZone, self).__init__(xml_node, sheet_obj)

    def create_trigger(self, trigger_type, trigger_values, priority=4):
        trigger_node = ET.SubElement(self.xml_node, 'trigger')
        node_dict = conf.get_trigger_dict(trigger_type, trigger_values, priority)
        for node in node_dict.items():
            node_tag = ET.SubElement(trigger_node, node[0])
            value = int2str(node[1])
            node_tag.text = value
        return

    def create_triggers(self):
        triggers_values = self.get_templates_values()
        for trigger_values in triggers_values:
            if trigger_values[3] != '' or trigger_values[4] != '':
                self.create_trigger('process', trigger_values)
            if trigger_values[-2] != '':
                self.create_trigger('log', trigger_values)
        return
