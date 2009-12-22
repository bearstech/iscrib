# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
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
from decimal import InvalidOperation

# Import from itools
from itools.core import get_abspath, merge_dicts, freeze
from itools.csv import CSVFile
from itools.datatypes import String, Integer, Boolean
from itools.gettext import MSG
from itools.uri import resolve_uri

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field
from ikaaro.text import Text

# Import from scrib
from bm2009_pageb_views import BM2009Form_PageB_View
from bm2009_views import BM2009Form_View, BM2009Form_Send, BM2009Form_Print
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import make_enumerate
from form import FormHandler, Form
from utils import parse_control


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


def get_schema_pages(path):
    path = get_abspath(path)
    handler = CSVFile(path)
    rows = handler.get_rows()
    # Skip header
    rows.next()

    schema = {}
    pages = {}
    for (name, title, form, page_number, dt_name, format, length, vocabulary,
            is_mandatory, fixed, sum, dependances, abrege, init,
            sql_field) in rows:
        # The name
        name = name.strip()
        if name == '':
            continue
        if name[0] == '#':
            name = name[1:]
        # The datatype
        dt_name = dt_name.strip().lower()
        if dt_name == 'enum':
            datatype = make_enumerate(vocabulary)
        else:
            datatype = dt_mapping.get(dt_name)
        if datatype is None:
            raise NotImplementedError, (dt_name, path)
        # The page number
        page_number = page_number.replace('-', '')
        # allow multiple page numbers
        page_numbers = []
        for page in page_number.split(','):
            if not page.isalpha():
                raise ValueError, """page "%s" n'est pas valide""" % page
            page_fields = pages.setdefault(page, set())
            page_fields.add(name)
            page_numbers.append(page)
        # Mandatory
        is_mandatory = (not is_mandatory or is_mandatory.upper() == 'OUI')
        # Sum
        sum = sum.strip()
        # Add to the schema
        page_numbers = tuple(page_numbers)
        schema[name] = datatype(format=format,
                length=(length.strip() or format), pages=page_numbers,
                is_mandatory=is_mandatory, sum=sum, abrege=abrege,
                sql_field=sql_field)
    return schema, pages



def get_controls(path):
    path = get_abspath(path)
    handler = CSVFile(path)
    rows = handler.get_rows()
    # Skip header
    rows.next()
    return list(rows)



class BM2009Handler(FormHandler):
    schema, pages = get_schema_pages('ui/scrib2009/schema-bm.csv')
    controls = get_controls('ui/scrib2009/controls-bm.csv')



class BM2009Form(Form):
    class_id = 'BM2009Form'
    class_handler = BM2009Handler
    class_icon48 = 'scrib2009/images/form48.png'
    class_views = ['pageA'] + Form.class_views

    # Views
    pageA = BM2009Form_View(title=MSG(u"Saisie du rapport"), n='A')
    pageB = BM2009Form_PageB_View(n='B')
    pageC = BM2009Form_View(n='C')
    pageD = BM2009Form_View(n='D')
    pageE = BM2009Form_View(n='E')
    pageF = BM2009Form_View(n='F')
    pageG = BM2009Form_View(n='G')
    pageH = BM2009Form_View(n='H')
    envoyer = BM2009Form_Send()
    imprimer = BM2009Form_Print()


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Form.get_metadata_schema(),
                code_ua=Integer,
                # Utilisé pour la recherche, pas la sécurité
                departement=String)


    def _get_catalog_values(self):
        return merge_dicts(Form._get_catalog_values(self),
                is_bm=True,
                code_ua=self.get_property('code_ua'),
                # Utilisé pour la recherche, pas la sécurité
                departement=self.get_property('departement'))


    ######################################################################
    # Security
    def is_bm(self):
        return self.parent.is_bm()


    def get_code_ua(self):
        return self.get_property('code_ua')


    ######################################################################
    # API
    def get_pageb(self, make=False):
        from bm2009_pageb import MultipleForm_PageB

        name = '%s-pageb' % self.get_code_ua()
        pageb = self.parent.get_resource(name, soft=True)
        if pageb is None:
            if make is False:
                metadata = MultipleForm_PageB.build_metadata()
                metadata.uri = resolve_uri(self.metadata.uri,
                        '%s.metadata' % name)
                metadata.database = self.metadata.database
                pageb = MultipleForm_PageB(metadata)
                pageb.name = name
                pageb.parent = self.parent
            else:
                pageb = MultipleForm_PageB.make_resource(MultipleForm_PageB,
                        self.parent, name,
                        title={'fr': self.get_title()})
        return pageb


    def is_first_time(self):
        pageb = self.get_pageb()
        return Form.is_first_time(self) and pageb.is_first_time()


    def get_invalid_fields(self, pages=freeze([]), exclude=freeze(['B'])):
        handler = self.handler
        schema = handler.schema
        fields = handler.fields
        for name in sorted(fields):
            if pages and name[0] not in pages:
                continue
            if name[0] in exclude:
                continue
            datatype = schema[name]
            value = fields[name]
            is_valid = datatype.is_valid(datatype.encode(value))
            if datatype.is_mandatory:
                # Vérifie toujours les champs obligatoires
                if is_valid:
                    continue
            else:
                # Vérifie seulement si quelque chose a été saisi
                if not datatype.encode(value):
                    continue
                if is_valid:
                    continue
            yield name, datatype


    def get_failed_controls(self, pages=freeze([]), exclude=freeze(['B'])):
        for number, title, expr, level, page in self.handler.controls:
            if pages and page not in pages:
                continue
            if page in exclude:
                continue
            expr = expr.strip()
            if not expr:
                continue
            # Le contrôle contient des formules
            if '[' in title:
                expanded = []
                for is_expr, token in parse_control(title):
                    if not is_expr:
                        expanded.append(token)
                    else:
                        try:
                            value = eval(token, self.get_vars())
                        except ZeroDivisionError:
                            value = None
                        expanded.append(str(value))
                title = ''.join(expanded)
            else:
                try:
                    value = eval(expr, self.get_vars())
                except ZeroDivisionError:
                    # Division par zéro toléré
                    value = None
                except InvalidOperation:
                    # Champs vides tolérés
                    value = None
            # Passed
            if value is True:
                continue
            yield {'number': number,
                   'title': unicode(title, 'utf8'),
                   'expr': expr,
                   'level': level,
                   'page': page,
                   'debug': "'%s' = '%s'" % (str(expr), value)}



###########################################################################
# Register
register_resource_class(BM2009Form)
# TODO remove after production
register_resource_class(BM2009Form, format='BM2009')
register_field('is_bm', Boolean(is_indexed=True, is_stored=True))
register_field('code_ua', Integer(is_indexed=True, is_stored=True))
register_field('departement', Unicode(is_indexed=True, is_stored=True))
