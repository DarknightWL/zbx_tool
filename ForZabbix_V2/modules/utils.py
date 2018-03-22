# coding: utf-8


def int2str(arg):
    if type(arg) is int:
        arg = str(arg)
    else:
        pass
    return arg


def f_str2int(arg):
    result = int(float(arg)) if arg else None
    return result


def handle_empty_cell(cell_value, temp_value):
    if cell_value == '':
        cell_value = temp_value
    else:
        temp_value = cell_value
