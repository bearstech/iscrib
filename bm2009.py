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

# Import from itools
from itools.core import get_abspath, merge_dicts
from itools.csv import CSVFile
from itools.datatypes import String, Integer, Boolean
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class, register_field
from ikaaro.text import Text

# Import from scrib
from bm2009_pageb_views import PageB_View
from bm2009_views import BMForm_View, BMSend_View, BMPrint_View
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import make_enumerate
from form import FormHandler, Form


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
                length=(length.strip() or format),pages=page_numbers,
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
    pageA = BMForm_View(title=MSG(u"Saisie du rapport"), n='A')
    pageB = PageB_View(n='B')
    pageC = BMForm_View(n='C')
    pageD = BMForm_View(n='D')
    pageE = BMForm_View(n='E')
    pageF = BMForm_View(n='F')
    pageG = BMForm_View(n='G')
    pageH = BMForm_View(n='H')
    envoyer = BMSend_View()
    imprimer = BMPrint_View()


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


    def get_pageb(self, make=False):
        from bm2009_pageb import MultipleForm_PageB

        name = '%s-pageb' % self.get_code_ua()
        pageb = self.parent.get_resource(name, soft=True)
        if pageb is None:
            if make is False:
                metadata = MultipleForm_PageB.build_metadata()
                pageb = MultipleForm_PageB(metadata)
                pageb.name = name
                pageb.parent = self.parent
            else:
                pageb = MultipleForm_PageB.make_resource(MultipleForm_PageB,
                        self.parent, name,
                        title={'fr': self.get_title()})
        return pageb



###########################################################################
# Register
register_resource_class(BM2009Form)
# TODO remove after production
register_resource_class(BM2009Form, format='BM2009')
register_field('is_bm', Boolean(is_indexed=True, is_stored=True))
register_field('code_ua', Integer(is_indexed=True, is_stored=True))
register_field('departement', Unicode(is_indexed=True, is_stored=True))
