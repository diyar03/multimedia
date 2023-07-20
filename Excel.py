"""
File creates a basic excel spreadsheet.
"""

import xlsxwriter as xl


class ExcelFile(object):
    def __init__(self, titles, column_names, data, tabnames, filename, single_sheet=False):
        if single_sheet:
            self.create_excel_file_single_sheet(titles, column_names, data, tabnames, filename)
        else:
            self.create_excel_file(titles, column_names, data, tabnames, filename)

    def create_excel_file(self, titles, column_names, data, tabnames, filename):
        my_excel = xl.Workbook(filename)
        length = len(tabnames)
        for i in range(length):
            my_worksheet = my_excel.add_worksheet()
            self.create_excel_sheet(my_worksheet, titles[i], column_names[i], tabnames[i], data[i])
        my_excel.close()

    def create_excel_file_single_sheet(self, titles, column_names, data, tabnames, filename):
        my_excel = xl.Workbook(filename)
        my_worksheet = my_excel.add_worksheet()
        self.create_excel_sheet(my_worksheet, titles, column_names, tabnames, data)
        my_excel.close()

    def create_excel_sheet(self, my_worksheet, title, column_names, tab_name, data):
        my_worksheet.name = tab_name

        row = 0
        col = 0
        for t in title:
            my_worksheet.write(row, col, t)
            col += 1
        col = 0
        row += 2

        for name in column_names:
            my_worksheet.write(row, col, name)
            col += 1

        col = 0
        row += 1

        for data_row in data:
            for data_cell in data_row:
                my_worksheet.write(row, col, data_cell)
                col += 1
            col = 0
            row += 1
