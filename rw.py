# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2008-2010 Hervé Cauwelier <herve@itaapy.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# Import from the Standard Library
from cStringIO import StringIO

# Import from lpod
from lpod.document import odf_get_document, odf_new_document
from lpod.const import ODF_SPREADSHEET
from lpod.style import odf_create_style
from lpod.table import odf_create_table, odf_create_row

# Import from xlrd
from xlrd import open_workbook
from xlwt import Workbook, easyxf
from xlwt.Style import default_style

# Import from itools
from itools.csv import CSVFile

# Import from ikaaro

# Import from iscrib


class ODSReader(object):

    def __init__(self, body):
        self.body = body
        self.init()


    def init(self):
        file = StringIO(self.body)
        self.document = odf_get_document(file)


    def get_tables(self):
        return self.document.get_body().get_tables()



class XLSTable(object):

    def __init__(self, sheet):
        self.sheet = sheet


    def rstrip(self, aggressive=False):
        pass


    def get_name(self):
        name = self.sheet.name
        assert type(name) is unicode, '"{0}" is not a str'.format(repr(name))
        return name


    def iter_values(self):
        sheet = self.sheet
        for idx in range(sheet.nrows):
            values = []
            for value in sheet.row_values(idx):
                if type(value) is float:
                    if value == int(value):
                        value = unicode(int(value))
                    else:
                        value = unicode(value)
                elif type(value) is not unicode:
                    try:
                        value = unicode(value)
                    except UnicodeError:
                        try:
                            value = unicode(value, 'cp1252')
                        except UnicodeError:
                            value = u""
                values.append(value)
            yield values


    def to_csv(self):
        csv = CSVFile()
        for values in self.iter_values():
            row = (value.encode('utf_8') for value in values)
            csv.add_row(row)
        return csv.to_str()



class XLSReader(ODSReader):

    def init(self):
        self.book = open_workbook(file_contents=self.body)


    def get_tables(self):
        for sheet in self.book.sheets():
            yield XLSTable(sheet)



class ODSWriter(object):
    mimetype = ODF_SPREADSHEET
    extension = 'ods'
    header_style = odf_create_style('table-cell', area='text', bold=True)


    def __init__(self, name):
        self.document = document = odf_new_document('spreadsheet')
        self.table = table = odf_create_table(name)
        document.get_body().append(table)
        document.insert_style(self.header_style, automatic=True)


    def add_row(self, values, is_header=False):
        if is_header is True:
            style = self.header_style
        else:
            style = None
        row = odf_create_row()
        row.set_values(values, style=style)
        self.table.append_row(row)


    def to_str(self):
        body = StringIO()
        self.document.save(body)
        return body.getvalue()



class XLSWriter(object):
    mimetype = 'application/vnd.ms-excel'
    extension = 'xls'
    header_style = easyxf('font: bold on')

    # XXX
    y = 0


    def __init__(self, name):
        self.workbook = workbook = Workbook()
        self.sheet = workbook.add_sheet(name)


    def add_row(self, values, is_header=False):
        sheet = self.sheet
        if is_header is True:
            style = self.header_style
        else:
            style = default_style
        for x, value in enumerate(values):
            sheet.write(self.y, x, value, style)
        self.y += 1


    def to_str(self):
        body = StringIO()
        self.workbook.save(body)
        return body.getvalue()
