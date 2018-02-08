# coding: utf-8
import xlrd


class AnalyExcel(object):
    """分析Excel文件，获得基本信息"""
    def __init__(self, excel_name):
        self.__excel_obj = xlrd.open_workbook(excel_name)

    def get_sheet_names(self):
        # 获取sheet的名称
        sheet_names = self.__excel_obj.sheet_names()
        return sheet_names

    def get_sheet(self, sheet_name):
        # 获取sheet对象
        sheet_obj = self.__excel_obj.sheet_by_name(sheet_name)
        return sheet_obj


class AnalySheet(object):
    """分析Sheet，获取内容"""
    def __init__(self, excel_obj, sheet_name):
        self.sheet_name = sheet_name
        self.sheet_obj = excel_obj.get_sheet(self.sheet_name)

    @property
    def sheet_nrow(self):
        # 获取sheet的行数
        return self.sheet_obj.nrows

    def get_row_values(self, row_num, start_colx=1, end_colx=None):
        # 获取sheet中某行的值
        values = self.sheet_obj.row_values(row_num-1, start_colx-1, end_colx)
        return values

    def get_col_values(self, col_num, start_rowx=1, end_rowx=None):
        # 获取sheet中某列的值
        values = self.sheet_obj.col_values(col_num-1, start_rowx-1, end_rowx)
        return values

    def get_cell_value(self, row_num, col_num):
        # 获取sheet中某单元格的值
        cell_value = str(self.sheet_obj.cell_value(row_num-1, col_num-1))
        return cell_value


if __name__ == '__main__':
    anaE = AnalyExcel('../a.xlsx')
    ana = AnalySheet(anaE, 'Template SYS FAM_BIZ')
    sheet_rows = ana.sheet_nrow
    row_values = ana.get_row_values(1, 2, 5)
    print('取行：', row_values)
    col_values = ana.get_col_values(1)
    print('取列1：', col_values, len(col_values))
    col_values = ana.get_col_values(2)
    print('取列2：', col_values, len(col_values))
