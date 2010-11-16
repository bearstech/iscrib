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
from lpod.document import odf_get_document

# Import from xlrd
from xlrd import open_workbook

# Import from itools
from itools.csv import CSVFile

# Import from ikaaro

# Import from iscrib
from datatypes import Numeric, Unicode


class ProgressMeter(object):
    last_percent = 0

    def __init__(self, max):
        self.max = max


    def show(self, i):
        percent = i * 100 / self.max
        if percent % 10 == 0 and percent != self.last_percent:
            print "  %s %%" % percent
            self.last_percent = percent



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



def get_page_number(name):
    try:
        _, page_number = name.split('page')
    except ValueError:
        return None
    return page_number.upper()



def SI(condition, iftrue, iffalse=True):
    if condition:
        value = iftrue
    else:
        value = iffalse
    return value



def parse_control(title):
    """Découpe le titre du contrôle pour remplacer les patterns du type ::

        « A123 : mauvaise valeur [A123] »

    par ::

        « A123 : mauvaise valeur [toto] »
    """
    generator = enumerate(title)
    end = 0
    for start, char in generator:
        if char == u'[':
            yield False, title[end:start+1]
            for end, char2 in generator:
                if char2 == u']':
                    yield True, title[start + 1:end]
                    break
    yield False, title[end:]



def force_encode(value, datatype, encoding):
    if datatype.multiple:
        return ' '.join(value)
    try:
        # TypeError: issubclass() arg 1 must be a class
        if isinstance(datatype, Numeric):
            return datatype.encode(value)
        elif issubclass(datatype, Unicode):
            return datatype.encode(value, encoding)
        return datatype.encode(value)
    except ValueError:
        return unicode(value).encode(encoding)
