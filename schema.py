# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006 luis <luis@lucifer.localdomain>
# Copyright (C) 2006-2008, 2010 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2008 Henry Obein <henry@itaapy.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Import from itools
from itools.csv import Table as TableFile
from itools.datatypes import Enumerate, String, Integer, Boolean
from itools.gettext import MSG
from itools.handlers import checkid
from itools.web import ERROR

# Import from ikaaro
from ikaaro.table import Table

# Import from iscrib
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime, Text
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import SqlEnumerate


ERR_WRONG_NUMBER_COLUMNS = ERROR(u'Wrong number of columns. Do you use the '
        u'latest template?')
ERR_EMPTY_NAME = ERROR(u'In schema, line {line}, variable name is missing.')
ERR_DUPLICATE_NAME = ERROR(u'In schema, line {line}, variable "{name}" is '
        u'duplicated.')
ERR_BAD_TYPE = ERROR(u'In schema, line {line}, type "{type}" is unknown.')
ERR_BAD_LENGTH = ERROR(u'In schema, line {line}, length "{length}" is '
        u'unknown.')
ERR_BAD_ENUM_REPR = ERROR(u'In schema, line {line}, enum representation '
        u'"{enum_repr}" is unknown.')
ERR_BAD_DECIMALS = ERROR(u'In schema, line {line}, decimals '
        u'"{decimals}" is unknown.')
ERR_BAD_MANDATORY = ERROR(u'In schema, line {line}, mandatory "{mandatory}" '
        u'is unknown.')
ERR_BAD_SIZE = ERROR(u'In schema, line {line}, size ' u'"{size}" is '
        u'unknown.')
ERR_BAD_FORMULA = ERROR(u'In schema, line {line}, in sum formula, variable '
        u'"{name}" is ' u'unknown.')
ERR_BAD_DEPENDENCY = ERROR(u'In schema, line {line}, dependency variable '
        u'name "{name}" is unknown.')


class FormatError(ValueError):

    def __init__(self, message, *args, **kw):
        super(FormatError, self).__init__(message, *args, **kw)
        self._message = message

    def __unicode__(self):
        # gettext already called
        return self._message.message



class Variable(String):

    @staticmethod
    def decode(data):
        value = String.decode(data).strip().upper()
        if value and value[0] == '#':
            value = value[1:]
        return value


    @staticmethod
    def get_page_number(value):
        page_number = ''
        for char in value:
            if char.isalpha():
                page_number += char
            else:
                break
        return page_number



class Type(Enumerate):
    options = [
        {'name': 'bool', 'value': u"Boolean", 'type': EnumBoolean},
        {'name': 'dec', 'value': u"Decimal", 'type': NumDecimal},
        {'name': 'digit', 'value': u"00000", 'type': NumDigit},
        {'name': 'hh:mm', 'value': u"HH:MM", 'type': NumShortTime},
        {'name': 'hhh:mm', 'value': u"HHH:MM", 'type': NumTime},
        {'name': 'int', 'value': u"Integer", 'type': NumInteger},
        {'name': 'jj/mm/aaaa', 'value': u"DD/MM/YYYY", 'type': NumDate},
        {'name': 'mm/aaaa', 'value': u"MM/YYYY", 'type': NumShortDate},
        {'name': 'str', 'value': u"String", 'type': Unicode},
        {'name': 'text', 'value': u"Text", 'type': Text},
        {'name': 'enum', 'value': u"List of values", 'type': SqlEnumerate}]


    @staticmethod
    def decode(data):
        return Enumerate.decode(data).strip().lower()


    @classmethod
    def get_type(cls, name):
        for option in cls.get_options():
            if option['name'] == name:
                return option['type']
        return cls.get_default()



class ValidInteger(Integer):

    @staticmethod
    def is_valid(value):
        return value is None or type(value) is int


    @classmethod
    def decode(cls, data):
        try:
            value = Integer.decode(data)
        except ValueError:
            return data
        if not value:
            value = cls.get_default()
        return value



class EnumerateOptions(Unicode):
    multiple = True

    @staticmethod
    def decode(data):
        value = Unicode.decode(data)
        return [{'name': checkid(option), 'value': option.strip()}
                for option in value.split(u"/")]


    @staticmethod
    def encode(value):
        raise NotImplementedError



class EnumerateRepresentation(Enumerate):
    options = [
        {'name': 'radio', 'value': MSG(u"Radio")},
        {'name': 'checkbox', 'value': MSG(u"Checkbox")}]


    @classmethod
    def decode(cls, data):
        value = Enumerate.decode(data).strip().lower()
        if not value:
            value = cls.get_default()



class Mandatory(Boolean):

    @classmethod
    def decode(cls, data):
        data = data.strip().upper()
        if data == '':
            return cls.get_default()
        elif data in ('O', 'OUI', '1'):
            return True
        elif data in ('N', 'NON', '0'):
            return False
        raise ValueError



class Dependency(String):

    @staticmethod
    def decode(data):
        return String.decode(data).strip().upper()


    @staticmethod
    def is_valid(value, known_variables):
        if not value:
            return True
        return value in known_variables



class Formula(String):

    @staticmethod
    def decode(data):
        value = String.decode(data).strip().upper()
        return ''.join(term.strip() for term in value.split('+'))


    @staticmethod
    def is_valid(value, known_variables):
        if not value:
            return True
        for name in value.split('+'):
            if name not in known_variables:
                raise ValueError, name
        return True



class SchemaHandler(TableFile):
    record_properties = {
        'title': Unicode(mandatory=True, title=MSG(u"Title")),
        'name': Variable(mandatory=True, title=MSG(u"Variable")),
        'type': Type(mandatory=True, title=MSG(u"Type")),
        'help': Unicode(title=MSG(u"Online Help")),
        'length': ValidInteger(default=20, title=MSG(u"Length")),
        'enum_options': EnumerateOptions(mandatory=True,
            title=MSG(u"Enumerate Options")),
        'enum_repr': EnumerateRepresentation(default='radio',
            title=MSG(u"Enumerate Representation")),
        'decimals': ValidInteger(default=2, title=MSG(u"Decimals")),
        'mandatory': Mandatory(default=True, title=MSG(u"Mandatory")),
        'size': ValidInteger(title=MSG(u"Input Size")),
        'dependency': Dependency(title=MSG(u"Dependent Field")),
        'formula': Formula(title=MSG(u"formula"))}


    def get_schema_pages(self):
        schema = {}
        pages = {}
        get_record_value = self.get_record_value
        for record in self.get_records():
            # The name
            name = get_record_value(record, 'name')
            # The datatype
            type_name = get_record_value(record, 'type')
            datatype = Type.get_type(type_name)
            if type_name == 'enum':
                options = get_record_value(record, 'enum_options')
                datatype = datatype(options=options)
            # The page number (now automatic)
            page_number = Variable.get_page_number(name)
            pages.setdefault(page_number, set()).add(name)
            page_numbers = []
            page_numbers.append(page_number)
            # Add to the datatype
            enum_repr = get_record_value(record, 'enum_repr')
            multiple = enum_repr == 'checkbox'
            length = get_record_value(record, 'length')
            size = get_record_value(record, 'size') or length
            schema[name] = datatype(pages=tuple(page_numbers),
                title=get_record_value(record, 'title'),
                help=get_record_value(record, 'help'),
                enum_repr=enum_repr,
                multiple=multiple,
                length=length,
                decimals = get_record_value(record, 'decimals'),
                mandatory=get_record_value(record, 'mandatory'),
                size=size,
                dependency=get_record_value(record, 'dependency'),
                formula=get_record_value(record, 'formula'))
        return schema, pages



class Schema(Table):
    class_id = 'Schema'
    class_version = '20090123' # TODO update
    class_title = MSG(u"Schema")
    class_handler = SchemaHandler
    class_icon16 = 'icons/16x16/excel.png'
    class_icon48 = 'icons/48x48/excel.png'

    # To import from CSV
    columns = ['title', 'name', 'type', 'help', 'length', 'enum_options',
            'enum_repr', 'decimals', 'mandatory', 'size', 'dependency',
            'formula']


    def _load_from_csv(self, body, columns):
        handler = self.handler
        try:
            handler.update_from_csv(body, columns, skip_header=True)
        except ValueError:
            raise FormatError, ERR_WRONG_NUMBER_COLUMNS
        # Consistency check
        get_record_value = handler.get_record_value
        # First round on variables
        known_variables = []
        for lineno, record in enumerate(handler.get_records()):
            # Starting from 0 + header
            lineno += 2
            name = get_record_value(record, 'name').strip().upper()
            if not name:
                raise FormatError, ERR_EMPTY_NAME(line=lineno)
            if name in known_variables:
                raise FormatError, ERR_DUPLICATE_NAME(line=lineno,
                        name=name)
            type_name = get_record_value(record, 'type')
            if not Type.is_valid(type_name):
                raise FormatError, ERR_BAD_TYPE(line=lineno,
                        type=type_name)
            length = get_record_value(record, 'length')
            if not ValidInteger.is_valid(length):
                raise FormatError, ERR_BAD_LENGTH(line=lineno, length=length)
            enum_repr = get_record_value(record, 'enum_repr')
            if not EnumerateRepresentation.is_valid(enum_repr):
                raise FormatError, ERR_BAD_ENUM_REPR(line=lineno,
                        enum_repr=enum_repr)
            decimals = get_record_value(record, 'decimals')
            if not ValidInteger.is_valid(decimals):
                raise FormatError, ERR_BAD_DECIMALS(line=lineno,
                        decimals=decimals)
            try:
                mandatory = get_record_value(record, 'mandatory')
            except ValueError:
                raise FormatError, ERR_BAD_MANDATORY(line=lineno,
                        mandatory=mandatory)
            size = get_record_value(record, 'size')
            if not ValidInteger.is_valid(size):
                raise FormatError, ERR_BAD_SIZE(line=lineno, size=size)
            known_variables.append(name)
        # Second round on references
        for lineno, record in enumerate(handler.get_records()):
            dependency = get_record_value(record, 'dependency')
            if not Dependency.is_valid(dependency, known_variables):
                raise FormatError, ERR_BAD_DEPENDENCY(line=lineno,
                        name=dependency)
            formula = get_record_value(record, 'formula')
            try:
                Formula.is_valid(formula, known_variables)
            except ValueError, name:
                raise FormatError, ERR_BAD_FORMULA(line=lineno,
                        name=name)


    def init_resource(self, body=None, filename=None, extension=None, **kw):
        super(Schema, self).init_resource(filename=filename,
                extension=extension, **kw)
        self._load_from_csv(body, self.columns)
