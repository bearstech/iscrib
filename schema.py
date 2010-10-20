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

# Import from ikaaro
from ikaaro.table import Table

# Import from iscrib
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime, Text
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import SqlEnumerate


ERR_EMPTY_NAME = u'In schema, line {line}, variable name is missing.'
ERR_DUPLICATE_NAME = (u'In schema, line {line}, variable "{name}" is '
        u'duplicated.')
ERR_BAD_TYPE = u'In schema, line {line}, type "{type}" is unknown.'
ERR_BAD_MANDATORY = (u'In schema, line {line}, mandatory "{mandatory}" is '
        u'unknown.')
ERR_BAD_SUM = (u'In schema, line {line}, in sum, variable "{name}" is '
        u'unknown.')
ERR_BAD_DEPENDENCY = (u'In schema, line {line}, dependency variable name '
        u'"{name}" is unknown.')


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


    def get_type(cls, name, default=None):
        for option in cls.get_options():
            if option['name'] == name:
                return option['type']
        return default



class Representation(String):

    @staticmethod
    def decode(data):
        return String.decode(data).strip().lower()


    @staticmethod
    def is_valid(value):
        return value.isdigit() or value == 'radio'



class Mandatory(Boolean):

    @staticmethod
    def decode(data):
        data = data.strip().upper()
        if data in ('', 'O', 'OUI', '1'):
            return True
        elif data in ('N', 'NON', '0'):
            return False
        raise ValueError



class Sum(String):

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



class Dependency(String):

    @staticmethod
    def decode(data):
        return String.decode(data).strip().upper()


    @staticmethod
    def is_valid(value, known_variables):
        return value and value in known_variables or True



class SchemaHandler(TableFile):
    record_properties = {
        'name': Variable(mandatory=True, title=MSG(u"Variable")),
        'title': Unicode(mandatory=True, title=MSG(u"Title")),
        'help': Unicode(title=MSG(u"Online Help")),
        'type': Type(mandatory=True, title=MSG(u"Type")),
        'representation': Representation(mandatory=True,
            title=MSG(u"Representation")),
        'length': Integer(default=0, title=MSG(u"Length")),
        'vocabulary': Unicode(title=MSG(u"Vocabulary")),
        'mandatory': Mandatory(title=MSG(u"Mandatory")),
        'sum': Sum(title=MSG(u"Sum")),
        'dependency': Dependency(title=MSG(u"Dependent Field"))}


    def get_schema_pages(self):
        schema = {}
        pages = {}
        get_record_value = self.get_record_value
        for record in self.get_records():
            # The name
            name = get_record_value(record, 'name')
            # The datatype
            dt_name = get_record_value(record, 'type')
            datatype = Type.get_type(dt_name)
            if dt_name == 'enum':
                vocabulary = get_record_value(record, 'vocabulary')
                options = []
                for value in vocabulary.strip().split('/'):
                    options.append({'name': checkid(value),
                                    'value': value.strip()})
                datatype.options = options
            # The page number (now automatic)
            page_number = Variable.get_page_number(name)
            pages.setdefault(page_number, set()).add(name)
            page_numbers = []
            page_numbers.append(page_number)
            # Add to the datatype
            representation = get_record_value(record, 'representation')
            length = get_record_value(record, 'length') or representation
            is_mandatory = get_record_value(record, 'mandatory')
            sum = get_record_value(record, 'sum')
            dependency = get_record_value(record, 'dependency')
            schema[name] = datatype(representation=representation,
                    help=get_record_value(record, 'help'),
                    length=str(length), pages=tuple(page_numbers),
                    is_mandatory=is_mandatory, sum=sum,
                    dependency=dependency)
        return schema, pages



class Schema(Table):
    class_id = 'Schema'
    class_title = MSG(u"Schema")
    class_handler = SchemaHandler
    class_icon16 = 'icons/16x16/excel.png'
    class_icon48 = 'icons/48x48/excel.png'

    # XXX To import from CSV
    columns = ['name', 'title', 'help', 'type', 'representation', 'length',
            'vocabulary', 'mandatory', 'sum', 'dependency']


    def init_resource(self, body=None, filename=None, extension=None, **kw):
        super(Schema, self).init_resource(filename=filename,
                extension=extension, **kw)
        handler = self.handler
        handler.update_from_csv(body, self.columns)
        # Consistency check
        get_record_value = handler.get_record_value
        # First round on variables
        known_variables = []
        for lineno, record in enumerate(handler.get_records()):
            name = get_record_value(record, 'name').strip().upper()
            if not name:
                raise ValueError, ERR_EMPTY_NAME.format(line=lineno+1)
            if name in known_variables:
                raise ValueError, ERR_DUPLICATE_NAME.format(line=lineno+1,
                        name=name)
            dt_name = get_record_value(record, 'type')
            if not Type.is_valid(dt_name):
                raise ValueError, ERR_BAD_TYPE.format(line=lineno+1,
                        type=dt_name)
            try:
                mandatory = get_record_value(record, 'mandatory')
            except ValueError:
                raise ValueError, ERR_BAD_MANDATORY.format(line=lineno+1,
                        mandatory=mandatory)
            known_variables.append(name)
        # Second round on references
        for lineno, record in enumerate(handler.get_records()):
            sum = get_record_value(record, 'sum')
            try:
                Sum.is_valid(sum, known_variables)
            except ValueError, name:
                raise ValueError, ERR_BAD_SUM.format(line=lineno+1,
                        name=name)
            dependency = get_record_value(record, 'dependency')
            if not Dependency.is_valid(dependency, known_variables):
                raise ValueError, ERR_BAD_DEPENDENCY.format(line=lineno+1,
                        name=dependency)
