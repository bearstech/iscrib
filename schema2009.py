# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006 luis <luis@lucifer.localdomain>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
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
from ikaaro.registry import register_resource_class
from ikaaro.text import CSV

# Import from scrib
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime, Text
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import EnumCV, make_enumerate


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
    'text': Text,
    'enumcv': EnumCV}



class FormType(Enumerate):
    default = 'BM'
    options = [
        {'name': 'BM', 'value': u"BM"},
        {'name': 'BDP', 'value': u"BDP"}]



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
        {'name': 'boolean', 'value': u"Booléen"},
        {'name': 'dec', 'value': u"Décimal"},
        {'name': 'digit', 'value': u"00000"},
        {'name': 'hh:mm', 'value': u"HH:MM"},
        {'name': 'hhh:mm', 'value': u"HHH:MM"},
        {'name': 'int', 'value': u"Entier"},
        {'name': 'jj/mm/aaaa', 'value': u"JJ/MM/AAAA"},
        {'name': 'mm/aaaa', 'value': u"MM/AAAA"},
        {'name': 'str', 'value': u"Chaîne"},
        {'name': 'text', 'value': u"Texte"},
        {'name': 'enum', 'value': u"Liste de valeurs"},
        {'name': 'enumCV', 'value': u"(réservé variable CV)"}]



class Mandatory(Enumerate):
    default = ''
    options = [
        {'name': '', 'value': u"Oui"},
        {'name': 'Non', 'value': u"Non"}]



class ReadOnly(Enumerate):
    default = 'Non'
    options = [
        {'name': 'Oui', 'value': u"Oui"},
        {'name': '', 'value': u"Non"}]



class Abrege(Enumerate):
    default = 'AC'
    options = [
        {'name': 'A', 'value': u"Abrégé"},
        {'name': 'C', 'value': u"Complet"},
        {'name': 'AC', 'value': u"Les deux"}]



class Schema2009Handler(CSVFile):
    schema = {'name': String(mandatory=True, title=MSG(u"Variable")),
              'title': Unicode(mandatory=True, title=MSG(u"Titre")),
              'form': FormType(mandatory=True, title=MSG(u"Formulaire")),
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
              'dependencies': String(title=MSG(u"Champs dépendants")),
              'abrege': Abrege(mandatory=True, title=MSG(u"Formulaire "
                  u"abrégé, complet ou les deux (par défaut)")),
              'initialisation': String(mandatory=True,
                  title=MSG(u"Initialisation (par défaut aucune)")),
              'sql_field': String(mandatory=True, title=MSG(u"Nom variable "
                  u"n-1 dans ADRESSE08"))}
    columns = ['name', 'title', 'form', 'page_number', 'type',
            'representation', 'length', 'vocabulary', 'mandatory',
            'readonly', 'sum', 'dependencies', 'abrege', 'initialisation',
            'sql_field']


    def get_schema_pages(self):
        schema = {}
        pages = {}
        for row in self.get_rows():
            # 0007651 formulaires abrégés abandonnés
            if row.get_value('abrege') == 'A':
                continue
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
                raise NotImplementedError, (dt_name,
                        str(self.get_abspath()))
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
            representation = row.get_value('representation'),
            length = row.get_value('length') or representation
            page_numbers = tuple(page_numbers)
            is_mandatory = row.get_value('mandatory').strip()
            is_mandatory = not is_mandatory or is_mandatory.upper() == 'OUI'
            readonly = row.get_value('readonly').strip().upper() == 'OUI'
            sum = row.get_value('sum').strip()
            dependances = row.get_value('dependencies').split()
            sql_field = row.get_value('sql_field')
            schema[name] = datatype(representation=representation,
                    length=length, pages=page_numbers,
                    is_mandatory=is_mandatory, readonly=readonly, sum=sum,
                    dependances=dependances, sql_field=sql_field)
        return schema, pages



class Schema2009(CSV):
    class_id = 'Schema2009'
    class_title = MSG(u"Schéma 2009")
    class_handler = Schema2009Handler
    class_icon48 = 'icons/48x48/excel.png'



register_resource_class(Schema2009)
