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
from itools.csv import CSVFile
from itools.datatypes import Enumerate, String, Integer
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.text import CSV

# Import from iscrib
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime, Text
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import make_enumerate


ERR_BAD_PAGE = (u'In schema, line {line}, page "{page}" does not match '
        u'variable "{name}".')


dt_mapping = {
    'boolean': EnumBoolean,
    'dec': NumDecimal,
    'digit': NumDigit,
    'hh:mm': NumShortTime,
    'hhh:mm': NumTime,
    'int': NumInteger,
    'jj/mm/aaaa': NumDate,
    'mm/aaaa': NumShortDate,
    'str': Unicode,
    'text': Text}



class PageNumber(Enumerate):
    options = [
        {'name': '0', 'value': u"0"},
        {'name': 'A', 'value': u"A"},
        {'name': 'B', 'value': u"B"},
        {'name': 'C', 'value': u"C"},
        {'name': 'D', 'value': u"D"},
        {'name': 'D', 'value': u"D"},
        {'name': 'E', 'value': u"E"},
        {'name': 'F', 'value': u"F"},
        {'name': 'G', 'value': u"G"},
        {'name': 'H', 'value': u"H"},
        {'name': 'I', 'value': u"I"}]



class Type(Enumerate):
    options = [
        {'name': 'boolean', 'value': u"Boolean"},
        {'name': 'dec', 'value': u"Decimal"},
        {'name': 'digit', 'value': u"00000"},
        {'name': 'hh:mm', 'value': u"HH:MM"},
        {'name': 'hhh:mm', 'value': u"HHH:MM"},
        {'name': 'int', 'value': u"Integer"},
        {'name': 'jj/mm/aaaa', 'value': u"DD/MM/YYYY"},
        {'name': 'mm/aaaa', 'value': u"MM/YYYY"},
        {'name': 'str', 'value': u"String"},
        {'name': 'text', 'value': u"Text"},
        {'name': 'enum', 'value': u"List of values"}]



class Mandatory(Enumerate):
    default = ''
    options = [
        {'name': '', 'value': u"Yes"},
        {'name': 'Non', 'value': u"No"}]



class ReadOnly(Enumerate):
    default = 'Non'
    options = [
        {'name': 'Oui', 'value': u"Oui"},
        {'name': '', 'value': u"Non"}]



class SchemaHandler(CSVFile):
    schema = {'name': String(mandatory=True, title=MSG(u"Variable")),
              'title': Unicode(mandatory=True, title=MSG(u"Titre")),
              'page_number': PageNumber(mandatory=True, title=MSG(u"Page")),
              'type': Type(mandatory=True, title=MSG(u"Type")),
              'representation': String(mandatory=True,
                  title=MSG(u"Représentation (par défaut INPUT TEXT)")),
              'length': Integer(default=0, title=MSG(u"Taille de champs "
                  u"de saisie (par défaut identique à Représentation)")),
              'vocabulary': Unicode(title=MSG(u"Valeurs autorisées / "
                  u"modalités")),
              'mandatory': Mandatory(title=MSG(u"Obligatoire "
                  u"(par défaut Oui)")),
              'readonly': ReadOnly(mandatory=True, title=MSG(u"Non "
                  u"modifiable (par défaut Non)")),
              'sum': String(title=MSG(u"Somme")),
              'dependencies': String(title=MSG(u"Champs dépendants"))}
    columns = ['name', 'title', 'page_number', 'type', 'representation',
            'length', 'vocabulary', 'mandatory', 'readonly', 'sum',
            'dependencies']


    def get_schema_pages(self):
        schema = {}
        pages = {}
        for row in self.get_rows():
            # The name
            name = row.get_value('name').strip()
            if name == '':
                continue
            if name[0] == '#':
                name = name[1:]
            # The datatype
            dt_name = row.get_value('type').strip().lower()
            if dt_name == 'enum':
                datatype = make_enumerate(row.get_value('vocabulary'))
            else:
                datatype = dt_mapping.get(dt_name)
            if datatype is None:
                raise NotImplementedError, (dt_name, str(self.get_abspath()))
            # The page number
            page_number = row.get_value('page_number').replace('-', '')
            # allow multiple page numbers
            page_numbers = []
            for page_number in page_number.split(','):
                if not (page_number.isalpha() or page_number == '0'): # FIXME
                    message = """page "%s" n'est pas valide""" % page_number
                    raise ValueError, message
                pages.setdefault(page_number, set()).add(name)
                page_numbers.append(page_number)
            # Add to the datatype
            representation = row.get_value('representation')
            length = row.get_value('length') or representation
            page_numbers = tuple(page_numbers)
            is_mandatory = row.get_value('mandatory').strip()
            is_mandatory = not is_mandatory or is_mandatory.upper() == 'OUI'
            readonly = row.get_value('readonly').strip().upper() == 'OUI'
            sum = row.get_value('sum').strip()
            dependances = row.get_value('dependencies').split()
            schema[name] = datatype(representation=representation,
                    title=row.get_value('title'),
                    length=str(length), pages=page_numbers,
                    is_mandatory=is_mandatory, readonly=readonly, sum=sum,
                    dependances=dependances)
        return schema, pages



class Schema(CSV):
    class_id = 'Schema'
    class_title = MSG(u"Schema")
    class_handler = SchemaHandler
    class_icon16 = 'icons/16x16/excel.png'
    class_icon48 = 'icons/48x48/excel.png'


    def init_resource(self, body=None, filename=None, extension=None, **kw):
        super(Schema, self).init_resource(body=body, filename=filename,
                extension=extension, **kw)
        handler = self.handler
        # Consistency check
        for lineno, row in enumerate(handler.get_rows()):
            name = row.get_value('name')
            page = row.get_value('page_number')
            pages = page.split(',')
            if name[0] not in pages:
                raise ValueError, ERR_BAD_PAGE.format(line=lineno+1,
                        page=page, name=name)
