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
from itools.datatypes import Enumerate, String, Integer, Boolean, Date
from itools.gettext import MSG
from itools.handlers import checkid
from itools.web import ERROR

# Import from ikaaro
from ikaaro.table import Table

# Import from iscrib
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime, Text
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import SqlEnumerate


ERR_BAD_NAME = ERROR(u'In schema, line {line}, variable "{name}" is '
        u'invalid.')
ERR_DUPLICATE_NAME = ERROR(u'In schema, line {line}, variable "{name}" is '
        u'duplicated.')
ERR_BAD_TYPE = ERROR(u'In schema, line {line}, type "{type}" is invalid.')
ERR_BAD_LENGTH = ERROR(u'In schema, line {line}, length "{length}" is '
        u'invalid.')
ERR_MISSING_OPTIONS = ERROR(u'In schema, line {line}, enum options are '
        u'missing.')
ERR_BAD_ENUM_REPR = ERROR(u'In schema, line {line}, enum representation '
        u'"{enum_repr}" is invalid.')
ERR_BAD_DECIMALS = ERROR(u'In schema, line {line}, decimals '
        u'"{decimals}" are invalid.')
ERR_BAD_MANDATORY = ERROR(u'In schema, line {line}, mandatory "{mandatory}" '
        u'is invalid.')
ERR_BAD_SIZE = ERROR(u'In schema, line {line}, size ' u'"{size}" is '
        u'invalid.')
ERR_BAD_DEPENDENCY = ERROR(u'In schema, line {line}, dependency variable '
        u'name "{name}" is invalid.')
ERR_BAD_FORMULA = ERROR(u'In schema, line {line}, in sum formula, variable '
        u'"{name}" is ' u'invalid.')
ERR_BAD_DEFAULT = ERROR(u'In schema, line {line}, default value "{default}" '
        u'is invalid.')


class FormatError(ValueError):

    def __init__(self, message, *args, **kw):
        message = message.gettext()
        return super(FormatError, self).__init__(message, *args, **kw)



class Variable(String):

    @staticmethod
    def decode(data):
        data = data.strip().upper()
        if not data:
            # Turn it into default value at the time of writing
            return None
        if data[0] == '#':
            data = data[1:]
        return String.decode(data)


    @staticmethod
    def is_valid(value):
        return bool(value)


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
        data = data.strip().lower()
        if not data:
            # Turn it into default value at the time of writing
            return None
        return Enumerate.decode(data)


    @classmethod
    def get_type(cls, name):
        for option in cls.get_options():
            if option['name'] == name:
                return option['type']
        return None



class ValidInteger(Integer):

    @classmethod
    def decode(cls, data):
        data = data.strip()
        if not data:
            # Turn it into default value at the time of writing
            return None
        try:
            value = Integer.decode(data)
        except ValueError:
            value = data
        return value


    @staticmethod
    def is_valid(value):
        return type(value) is int



class EnumerateOptions(Unicode):
    default = None
    multiple = True


    @staticmethod
    def decode(data):
        data = data.strip()
        if not data:
            # Turn it into default value at the time of writing
            return None
        value = Unicode.decode(data)
        return {'name': checkid(value), 'value': value}


    @staticmethod
    def encode(value):
        if value is None:
            return None
        return Unicode.encode(value['value'])


    @staticmethod
    def is_valid(value):
        return value is not None or value['name'] is not None


    @staticmethod
    def split(value):
        return [{'name': checkid(option), 'value': option.strip()}
                for option in value.split(u"/")]



class EnumerateRepresentation(Enumerate):
    options = [
        {'name': 'select', 'value': MSG(u"Select")},
        {'name': 'radio', 'value': MSG(u"Radio")},
        {'name': 'checkbox', 'value': MSG(u"Checkbox")}]


    @staticmethod
    def decode(data):
        data = data.strip().lower()
        if not data:
            # Turn it into default value at the time of writing
            return None
        return Enumerate.decode(data)



class Mandatory(Boolean):

    @classmethod
    def decode(cls, data):
        data = data.strip().upper()
        if not data:
            # Turn it into default value at the time of writing
            return None
        elif data in ('O', 'OUI', '1'):
            return True
        elif data in ('N', 'NON', '0'):
            return False
        return data


    @classmethod
    def is_valid(cls, value):
        return type(value) is bool



class Dependency(String):

    @staticmethod
    def decode(data):
        data = data.strip().upper()
        if not data:
            # Turn it into default value at the time of writing
            return None
        return String.decode(data)


    @staticmethod
    def is_valid(value, known_variables):
        if not value:
            return True
        return value in known_variables



class Formula(String):

    @staticmethod
    def decode(data):
        data = data.strip().upper()
        if not data:
            # Turn it into default value at the time of writing
            return None
        value = String.decode(data)
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
    # Don't store default values here because any value needs to be written
    # down in case the default value changes later.
    record_properties = {
        'title': Unicode(mandatory=True, title=MSG(u"Title")),
        'name': Variable(mandatory=True, title=MSG(u"Variable")),
        'type': Type(mandatory=True, title=MSG(u"Type")),
        'help': Unicode(title=MSG(u"Online Help")),
        'length': ValidInteger(title=MSG(u"Length")),
        'enum_options': EnumerateOptions(mandatory=True,
            title=MSG(u"Enumerate Options")),
        'enum_repr': EnumerateRepresentation(
            title=MSG(u"Enumerate Representation")),
        'decimals': ValidInteger(title=MSG(u"Decimals")),
        'mandatory': Mandatory(title=MSG(u"Mandatory")),
        'size': ValidInteger(title=MSG(u"Input Size")),
        'dependency': Dependency(title=MSG(u"Dependent Field")),
        'formula': Formula(title=MSG(u"Formula")),
        'default': String(default='', title=MSG(u"Default Value"))}


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
            if issubclass(datatype, SqlEnumerate):
                enum_options = get_record_value(record, 'enum_options')
                representation = get_record_value(record, 'enum_repr')
                multiple = (representation == 'checkbox')
                datatype = datatype(options=enum_options,
                        representation=representation)
            elif issubclass(datatype, EnumBoolean):
                datatype = datatype(representation='radio')
                multiple = False
            else:
                multiple = False
            # The page number (now automatic)
            page_number = Variable.get_page_number(name)
            pages.setdefault(page_number, set()).add(name)
            page_numbers = []
            page_numbers.append(page_number)
            # Add to the datatype
            default = get_record_value(record, 'default')
            if multiple:
                default = [default]
            length = get_record_value(record, 'length')
            size = get_record_value(record, 'size') or length
            schema[name] = datatype(default=datatype.decode(default),
                multiple=multiple,
                pages=tuple(page_numbers),
                title=get_record_value(record, 'title'),
                help=get_record_value(record, 'help'),
                length=length,
                decimals=get_record_value(record, 'decimals'),
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
            'formula', 'default']


    def _load_from_csv(self, body, columns):
        handler = self.handler
        handler.update_from_csv(body, columns, skip_header=True)
        get_record_value = handler.get_record_value
        # Consistency check
        # First round on variables
        known_variables = []
        for lineno, record in enumerate(handler.get_records()):
            # Starting from 1 + header
            lineno += 2
            default_values = {}
            # Name
            name = get_record_value(record, 'name')
            if name is None:
                continue
            name = name.strip().upper()
            if not Variable.is_valid(name):
                raise FormatError, ERR_BAD_NAME(line=lineno, name=name)
            if name in known_variables:
                raise FormatError, ERR_DUPLICATE_NAME(line=lineno,
                        name=name)
            # Type
            type_name = get_record_value(record, 'type')
            datatype = Type.get_type(type_name)
            if datatype is None:
                raise FormatError, ERR_BAD_TYPE(line=lineno,
                        type=type_name)
            # Length
            length = get_record_value(record, 'length')
            if length is None:
                # Write down default at this time
                default_values['length'] = length = 20
            if not ValidInteger.is_valid(length):
                raise FormatError, ERR_BAD_LENGTH(line=lineno, length=length)
            if issubclass(datatype, SqlEnumerate):
                # Enumerate Options
                enum_option = get_record_value(record, 'enum_options')[0]
                if enum_option is None:
                    raise FormatError, ERR_MISSING_OPTIONS(line=lineno)
                # Split on "/"
                enum_options = EnumerateOptions.split(enum_option['value'])
                default_values['enum_options'] = enum_options
                # Enumerate Representation
                enum_repr = get_record_value(record, 'enum_repr')
                if enum_repr is None:
                    # Write down default at the time of writing
                    default_values['enum_repr'] = enum_repr = 'radio'
                if not EnumerateRepresentation.is_valid(enum_repr):
                    raise FormatError, ERR_BAD_ENUM_REPR(line=lineno,
                            enum_repr=enum_repr)
            elif issubclass(datatype, NumDecimal):
                # Decimals
                decimals = get_record_value(record, 'decimals')
                if decimals is None:
                    # Write down default at the time of writing
                    default_values['decimals'] = decimals = 2
                if not ValidInteger.is_valid(decimals):
                    raise FormatError, ERR_BAD_DECIMALS(line=lineno,
                            decimals=decimals)
            # Mandatory
            mandatory = get_record_value(record, 'mandatory')
            if mandatory is None:
                # Write down default at the time of writing
                default_values['mandatory'] = mandatory = True
            if not Mandatory.is_valid(mandatory):
                raise FormatError, ERR_BAD_MANDATORY(line=lineno,
                        mandatory=mandatory)
            # Size
            size = get_record_value(record, 'size')
            if size is None:
                # Write down default at the time of writing
                default_values['size'] = size = length
            if not ValidInteger.is_valid(size):
                raise FormatError, ERR_BAD_SIZE(line=lineno, size=size)
            # Default value
            default = get_record_value(record, 'default').strip()
            if default:
                if issubclass(datatype, EnumBoolean):
                    value = Mandatory.decode(default)
                    default = EnumBoolean.encode(value)
                elif issubclass(datatype, SqlEnumerate):
                    datatype = datatype(options=enum_options)
                    default = checkid(default)
                elif issubclass(datatype, NumTime):
                    # "0-0-0 09:00:00" -> "09:00:00"
                    default = default.split(' ')[-1]
                    # "09:00:00" -> "09:00"
                    if default.count(":") > 1:
                        default = default.rsplit(":", 1)[0]
                elif issubclass(datatype, NumDate):
                    # "2010-11-18 00:00:00" -> "18/11/2010"
                    default = default.split(' ')[0]
                    value = Date.decode(default)
                    default = NumDate.encode(value)
                elif issubclass(datatype, NumDigit):
                    datatype = datatype(length=length)
                if not datatype.is_valid(default):
                    raise FormatError, ERR_BAD_DEFAULT(line=lineno,
                            default=unicode(default, 'utf_8'))
                default_values['default'] = default
            # Update values for optional columns
            if default_values:
                handler.update_record(record.id, **default_values)
            known_variables.append(name)
        # Second round on references
        for lineno, record in enumerate(handler.get_records()):
            # Starting from 1 + header
            lineno += 2
            dependency = get_record_value(record, 'dependency')
            if not Dependency.is_valid(dependency, known_variables):
                raise FormatError, ERR_BAD_DEPENDENCY(line=lineno,
                        name=dependency)
            formula = get_record_value(record, 'formula')
            if not Formula.is_valid(formula, known_variables):
                raise FormatError, ERR_BAD_FORMULA(line=lineno,
                        name=name)


    def init_resource(self, body=None, filename=None, extension=None, **kw):
        super(Schema, self).init_resource(filename=filename,
                extension=extension, **kw)
        self._load_from_csv(body, self.columns)


    def update_20090123(self):
        handler = self.handler
        for lineno, record in enumerate(handler.get_records()):
            get_record_value = handler.get_record_value
            update_record = handler.update_record
            record_id = record.id
            # representation -> length+enum_repr+decimals
            # Default values at the time of writing
            length = 20
            enum_repr = 'radio'
            decimals = 2
            representation = get_record_value(record, 'representation')[0]
            if "." in representation:
                integer, decimals = representation.split(".")
            elif representation.isdigit():
                length = representation
            elif EnumerateRepresentation.is_valid(representation):
                enum_repr = representation
            update_record(record_id, length=length, enum_repr=enum_repr,
                    decimals=decimals, representation=None)
            # vocabulary -> enum_options
            vocabulary = get_record_value(record, 'vocabulary')[0]
            vocabulary = Unicode.decode(vocabulary)
            enum_options = EnumerateOptions.split(vocabulary)
            handler.update_record(record_id, enum_options=enum_options,
                    vocabulary=None)
