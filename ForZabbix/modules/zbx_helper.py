# coding: utf-8
import xml.etree.cElementTree as et
from modules.excel_parse import AnalySheet, AnalyExcel
from modules.utils import int2str, f_str2int
from modules import conf


def create_type1_node(parent_node, new_node_name, *sub_node_value):
    """
    type1类型节点：
    1、parent_node节点名称是new_node节点名称的复数
    2、new_node节点下仅有一个子节点name
    """
    for item in sub_node_value:
        new_node = et.SubElement(parent_node, new_node_name)
        sub_node = et.SubElement(new_node, 'name')
        sub_node.text = item
    return


def create_dependency_node(parent_node, new_node_name, name, expression):
    new_node = et.SubElement(parent_node, new_node_name)
    name_node = et.SubElement(new_node, 'name')
    name_node.text = name
    expression_node = et.SubElement(new_node, 'expression')
    expression_node.text = expression
    return


class CreateGroupsZone(object):
    """
    创建zabbix主机模板中的groups域
    """
    def __init__(self, xml_node, excel_obj, sheet_name='hosts'):
        self.xml_node = xml_node
        self.sheet_obj = AnalySheet(excel_obj, sheet_name)

    def __get_group_names(self):
        temp = set(self.sheet_obj.get_col_values(2))
        group_names = list(filter(lambda x: x, temp))
        return group_names

    def create_groups(self):
        group_names = self.__get_group_names()
        create_type1_node(self.xml_node, 'group', *group_names)
        return


class CreateHostsZone(object):
    """
    创建zabbix主机模板中的hosts域
    """
    def __init__(self, xml_node, excel_obj, sheet_name='hosts'):
        self.xml_node = xml_node
        self.sheet_obj = AnalySheet(excel_obj, sheet_name)

    def __get_host_values(self, nrow):
        """
        :param nrow: 行号
        :return: host信息
        """
        return self.sheet_obj.get_row_values(nrow)

    def __get_hosts_values(self):
        hosts_values_dict = dict()
        bef_temp = list()
        for item in range(2, self.sheet_obj.sheet_nrow+1):
            temp = self.__get_host_values(item)[1:]
            if temp[0] == '':
                temp[0] = bef_temp[-1]
            else:
                bef_temp.append(temp[0])
            hosts_values_dict[temp[1]] = temp
        return hosts_values_dict

    def create_interface(self, parent_node, interface_info_dict):
        cur_node = et.SubElement(parent_node, 'interface')
        for k, v in interface_info_dict.items():
            child_node = et.SubElement(cur_node, k)
            child_node.text = int2str(v)

    def create_host(self,parent_node, host_values):
        host_info_dict, interface_info_dict = conf.get_host_dicts(host_values)
        for k, v in host_info_dict.items():
            if k == 'proxy':
                proxy_node = et.SubElement(parent_node, k)
                name_node = et.SubElement(proxy_node, 'name')
                name_node.text = int2str(v)
            elif k == 'templates':
                templates_node = et.SubElement(parent_node, k)
                create_type1_node(templates_node, 'template', int2str(v))
            elif k == 'groups':
                groups_node = et.SubElement(parent_node, k)
                create_type1_node(groups_node, 'group', int2str(v))
            elif k == 'interfaces':
                interfaces_node = et.SubElement(parent_node, k)
                self.create_interface(interfaces_node, interface_info_dict)
            else:
                child_node = et.SubElement(parent_node, k)
                child_node.text = int2str(v)
        return

    def create_hosts(self):
        hosts_values_dict = self.__get_hosts_values()
        for k, host_values in hosts_values_dict.items():
            cur_node = et.SubElement(self.xml_node, 'host')
            self.create_host(cur_node, host_values)
        return


class CreateTemplatesZone(object):
    """
    创建zabbix模板中的templates域
    """
    def __init__(self, xml_node, excel_obj):
        self.xml_node = xml_node
        self.excel_obj = excel_obj

    def create_template(self, template_name):
        """
        根据sheet页创建模板
        :param template_name: sheet页名称
        """
        sheet_obj = AnalySheet(self.excel_obj, template_name)
        parent_node = et.SubElement(self.xml_node, 'template')
        # template节点
        template_node = et.SubElement(parent_node, 'template')
        template_node.text = sheet_obj.get_cell_value(1, 2)
        # name节点
        name_node = et.SubElement(parent_node, 'name')
        name_node.text = sheet_obj.get_cell_value(1, 2)
        # groups节点
        groups_node = et.SubElement(parent_node, 'groups')
        create_type1_node(groups_node, 'group', 'template')
        # applications节点
        col3 = sheet_obj.get_col_values(3)
        col3 = list(set(col3))
        app_values = filter(lambda x: x, col3)
        applications_node = et.SubElement(parent_node, 'applications')
        create_type1_node(applications_node, 'application', *app_values)
        # items节点
        items_node = et.SubElement(parent_node, 'items')
        items = CreateItem(items_node, sheet_obj)
        items.create_item('log')
        items.create_item('process')
        items.create_item('system_status')
        # 其他无值节点
        discovery_rules_node = et.SubElement(parent_node, 'discovery_rules')
        macros_node = et.SubElement(parent_node, 'macros')
        # 父模版节点
        col1 = sheet_obj.get_col_values(1)
        col2 = sheet_obj.get_col_values(2)
        parent_template_index = col1.index('父类模板名称')
        system_alarm_index = col1.index('系统告警')
        parent_template_values = col2[parent_template_index: system_alarm_index]
        templates_node = et.SubElement(parent_node, 'templates')
        create_type1_node(templates_node, 'template', *parent_template_values)
        screens_node = et.SubElement(parent_node, 'screens')
        return


class CreateItem(object):
    def __init__(self, parent_node, sheet_obj):
        """
        :param parent_node: 父节点
        :param sheet_obj: 工作表对象
        """
        self.parent_node = parent_node
        self.sheet_obj = sheet_obj

    def get_group_border(self):
        col = self.sheet_obj.get_col_values(1)
        log_index = col.index('log')
        process_index = col.index('进程')
        system_status_index = col.index('系统状态')
        group_border_dic = dict()
        group_border_dic['log'] = (log_index+1, process_index)
        group_border_dic['process'] = (process_index+1, system_status_index)
        group_border_dic['system_status'] = (system_status_index+1, len(col))
        return group_border_dic

    def __get_name(self, item_type):
        """
        :param item_type: item类型
        :return: name节点的值
        """
        group_border_dic = self.get_group_border()
        col2 = self.sheet_obj.get_col_values(2)
        name_values = col2[group_border_dic[item_type][0]: group_border_dic[item_type][1]]
        return name_values

    def __get_key(self, item_type):
        """
        :param item_type: item类型
        :return: key节点的值
        """
        group_border_dic = self.get_group_border()
        col1 = self.sheet_obj.get_col_values(1)
        key_values = col1[group_border_dic[item_type][0]: group_border_dic[item_type][1]]
        return key_values

    def __get_app(self, item_type):
        """
        :param item_type: item类型
        :return: application节点的值
        """
        group_border_dic = self.get_group_border()
        col3 = self.sheet_obj.get_col_values(3)
        app_values = col3[group_border_dic[item_type][0]: group_border_dic[item_type][1]]
        return app_values

    def create_item(self, item_type):
        """
        :param item_type:item类型
        :return: item域
        """
        name_values = self.__get_name(item_type)
        key_values = self.__get_key(item_type)
        app_values = self.__get_app(item_type)
        temp = zip(name_values, key_values, app_values)

        for cell in temp:
            node_dict = conf.get_item_dict(cell)
            new_node = et.SubElement(self.parent_node, 'item')
            for k, v in node_dict.items():
                if k == 'applications':
                    app_node = et.SubElement(new_node, k)
                    create_type1_node(app_node, 'application', v)
                else:
                    child_node = et.SubElement(new_node, k)
                    child_node.text = int2str(v)
        return

    def create_log_type_item(self):
        name_values = self.__get_name('log')
        key_values = self.__get_key('log')
        app_values = self.__get_app('log')
        temp = zip(name_values, key_values, app_values)

        for cell in temp:
            node_dict = conf.get_item_dict(cell)
            new_node = et.SubElement(self.parent_node, 'item')
            for k, v in node_dict.items():
                if k == 'applications':
                    app_node = et.SubElement(new_node, k)
                    create_type1_node(app_node, 'application', v)
                else:
                    child_node = et.SubElement(new_node, k)
                    if type(v) is int:
                        v = str(v)
                    child_node.text = v
        return

    def create_process_type_item(self):
        name_values = self.__get_name('process')
        key_values = self.__get_key('process')
        app_values = self.__get_app('process')
        temp = zip(name_values, key_values, app_values)

        for cell in temp:
            node_dict = conf.get_item_dict(cell)
            new_node = et.SubElement(self.parent_node, 'item')
            for k, v in node_dict.items():
                if k == 'applications':
                    app_node = et.SubElement(new_node, k)
                    create_type1_node(app_node, 'application', v)
                else:
                    child_node = et.SubElement(new_node, k)
                    if type(v) is int:
                        v = str(v)
                    child_node.text = v
        return

    def create_system_type_item(self):
        name_values = self.__get_name('system_status')
        key_values = self.__get_key('system_status')
        app_values = self.__get_app('system_status')
        temp = zip(name_values, key_values, app_values)

        for cell in temp:
            node_dict = conf.get_item_dict(cell)
            new_node = et.SubElement(self.parent_node, 'item')
            for k, v in node_dict.items():
                if k == 'applications':
                    app_node = et.SubElement(new_node, k)
                    create_type1_node(app_node, 'application', v)
                else:
                    child_node = et.SubElement(new_node, k)
                    if type(v) is int:
                        v = str(v)
                    child_node.text = v
        return


class CreateTriggersZone(object):
    """
    创建zbbix模板中的trigger域
    """
    def __init__(self, xml_node, excel_obj):
        self.xml_node = xml_node
        self.excel_obj = excel_obj

    def __get_system_alarm_info(self, template_name):
        sheet_obj = AnalySheet(self.excel_obj, template_name)
        col1 = sheet_obj.get_col_values(1)
        trigger_index = col1.index('系统告警')
        log_index = col1.index('log')
        col2 = sheet_obj.get_col_values(2)
        info_dic = dict(zip(col1[trigger_index+1: log_index], col2[trigger_index+1: log_index]))
        return info_dic

    def __get_alarm_info(self, template_name):
        sheet_obj = AnalySheet(self.excel_obj, template_name)
        try:
            col4 = filter(lambda x: x, sheet_obj.get_col_values(4))  # ['', '', 'a', '', 'b'] -> ['a', 'b']
            col5 = filter(lambda x: x, sheet_obj.get_col_values(5))
            info_dic = dict(zip(col4, col5))
        except IndexError as err:
            info_dic = dict()
        return info_dic

    def __get_threshold_values(self, template_name):
        sheet_obj = AnalySheet(self.excel_obj, template_name)
        col1 = sheet_obj.get_col_values(1)
        trigger_index = col1.index('系统告警')
        MEM_lower_threshold_value = f_str2int(sheet_obj.get_cell_value(trigger_index+2, 2))
        MEM_upper_threshold_value = f_str2int(sheet_obj.get_cell_value(trigger_index+3, 2))
        CPU_lower_threshold_value = f_str2int(sheet_obj.get_cell_value(trigger_index+4, 2))
        CPU_upper_threshold_value = f_str2int(sheet_obj.get_cell_value(trigger_index+5, 2))
        return MEM_lower_threshold_value, MEM_upper_threshold_value, CPU_lower_threshold_value, CPU_upper_threshold_value

    def create_common_trigger(self, template_name):
        """
        创建公共的系统层面触发器
        """
        info_dic = self.__get_system_alarm_info(template_name)
        MEM_lower, MEM_upper, CPU_lower, CPU_upper = self.__get_threshold_values(template_name)
        for k, v in info_dic.items():
            if not v:
                pass
            else:
                trigger_node = et.SubElement(self.xml_node, 'trigger')
                temp = k.split('：')
                v = int(v)
                dependency_name = None
                node_dict = dict()
                if temp[0].strip() == 'CPU告警':
                    if v == CPU_lower:
                        node_dict = conf.get_common_trigger_dict(template_name, 'CPU', v, CPU_lower, CPU_upper)
                        dependency_name = '{HOST.NAME}:CPU使用率超过%s%%' % CPU_upper
                    elif v == CPU_upper:
                        node_dict = conf.get_common_trigger_dict(template_name, 'CPU', v, CPU_lower, CPU_upper, False)
                elif temp[0].strip() == '内存告警':
                    if v == MEM_lower:
                        node_dict = conf.get_common_trigger_dict(template_name, 'MEM', v, MEM_lower, MEM_upper)
                        dependency_name = '{HOST.NAME}:内存使用率超过%s%%' % MEM_upper
                    elif v == MEM_upper:
                        node_dict = conf.get_common_trigger_dict(template_name, 'MEM', v, MEM_lower, MEM_upper, False)
                for node in node_dict.items():
                    node_tag = et.SubElement(trigger_node, node[0])
                    value = int2str(node[1])
                    if node[0] != 'dependencies':
                        node_tag.text = value
                    else:
                        if not value:
                            node_tag.text = value
                        else:
                            create_dependency_node(node_tag, 'dependency', dependency_name, value)
        return

    def create_trigger(self, template_name):
        info_dic = self.__get_alarm_info(template_name)
        if info_dic is {}:
            pass
        else:
            for k, v in info_dic.items():
                trigger_node = et.SubElement(self.xml_node, 'trigger')
                node_dict = conf.get_trigger_dict(k, v)
                for node in node_dict.items():
                    node_tag = et.SubElement(trigger_node, node[0])
                    value = int2str(node[1])
                    node_tag.text = value
        return


if __name__ == '__main__':
    excel_obj = AnalyExcel('../a.xlsx')
    groups = CreateHostsZone('bb', excel_obj)
    hosts_values = groups._CreateHostsZone__get_hosts_values()
    groups.create_host('test', hosts_values['fam-B4'])