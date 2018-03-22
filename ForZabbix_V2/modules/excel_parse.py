# coding: utf-8
import xlrd


class AnalyExcel(object):
    """分析Excel文件，获得基本信息"""
    def __init__(self, excel_name):
        self.__excel_obj = xlrd.open_workbook(excel_name)

    def get_sheet_names(self):
        # 获取sheet的名称
        valid_sheets = []
        sheet_names = self.__excel_obj.sheet_names()
        for item in sheet_names:
            if item[0] == '@':
                pass
            else:
                valid_sheets.append(item)
        return valid_sheets

    def get_sheet(self, sheet_name):
        # 获取sheet对象
        sheet_obj = self.__excel_obj.sheet_by_name(sheet_name)
        return sheet_obj


class AnalySheet(object):
    """分析Sheet，获取内容"""
    def __init__(self, sheet_obj):
        self.sheet_obj = sheet_obj

    @property
    def sheet_nrow(self):
        # 获取sheet的行数
        return self.sheet_obj.nrows

    def get_row_values(self, row_num, start_colx=0, end_colx=None):
        # 获取sheet中某行的值
        values = self.sheet_obj.row_values(row_num, start_colx, end_colx)
        return values

    def get_col_values(self, col_num, start_rowx=0, end_rowx=None):
        # 获取sheet中某列的值
        values = self.sheet_obj.col_values(col_num, start_rowx, end_rowx)
        return values

    def get_cell_value(self, row_num, col_num):
        # 获取sheet中某单元格的值
        cell_value = str(self.sheet_obj.cell_value(row_num, col_num))
        return cell_value

    def get_merged_cells(self):
        # 获取sheet中全部合并单元格的坐标
        merged_cells = self.sheet_obj.merged_cells
        return merged_cells
