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

# Import from scrib
from bm2009_pageb_views import BM2009Form_PageB_View
from bm2009_views import BM2009Form_View, BM2009Form_Send, BM2009Form_Print
from bm2009_views import BM2009Form_Edit, BM2009Form_New
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime, Text
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import make_enumerate
from form import quote_sql, FormHandler, Form
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
    for (name, title, form, page_number, dt_name, representation, length,
            vocabulary, is_mandatory, readonly, sum, dependances, abrege,
            init, sql_field) in rows:
        # 0007651 formulaires abrégés abandonnés
        if abrege == 'A':
            continue
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
        is_mandatory = (not is_mandatory.strip()
                or is_mandatory.upper() == 'OUI')
        # Sum
        sum = sum.strip()
        # Add to the schema
        page_numbers = tuple(page_numbers)
        schema[name] = datatype(representation=representation,
                length=(length.strip() or representation),
                pages=page_numbers, is_mandatory=is_mandatory,
                readonly=readonly, sum=sum, dependances=dependances,
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


    def is_disabled_by_dependency(self, name):
        dep_name = self.schema[name].dependances
        if not dep_name:
            return False
        if self.get_value(dep_name) is not True:
            return True
        # Second level
        dep_dep_name = self.schema[dep_name].dependances
        if not dep_dep_name:
            return False
        return self.get_value(dep_dep_name) is not True


    def get_reverse_dependencies(self, name):
        return [dep_name for dep_name, dep_datatype in self.schema.iteritems()
                if dep_datatype.dependances == name]



class BM2009Form(Form):
    class_id = 'BM2009Form'
    class_handler = BM2009Handler
    class_title = MSG(u"Formulaire BM")
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
    pageI = BM2009Form_View(n='I')
    envoyer = BM2009Form_Send()
    imprimer = BM2009Form_Print()
    edit = BM2009Form_Edit()
    new_instance = BM2009Form_New()


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Form.get_metadata_schema(),
                code_ua=Integer,
                # Utilisé pour la recherche, pas la sécurité
                departement=String,
                # 0008120 marquage manuel
                is_first_time=Boolean(default=True))


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


    def is_ready(self):
        for name, datatype in self.get_invalid_fields():
            if datatype.is_mandatory:
                return False
        for control in self.get_failed_controls():
            if control['level'] == '2':
                return False
        for form in self.get_pageb().get_resources():
            for name, datatype in form.get_invalid_fields():
                if datatype.is_mandatory:
                    return False
            for control in form.get_failed_controls():
                if control['level'] == '2':
                    return False
        return True


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
        # 0008120 Le handler est prérempli donc marquage manuel
        return self.get_property('is_first_time') and pageb.is_first_time()


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
                        expanded.append(unicode(token, 'utf8'))
                    else:
                        try:
                            value = eval(token, self.get_vars())
                        except ZeroDivisionError:
                            value = None
                        expanded.append(unicode(value))
                title = u"".join(expanded)
            else:
                try:
                    value = eval(expr, self.get_vars())
                except ZeroDivisionError:
                    # Division par zéro toléré
                    value = None
                except InvalidOperation:
                    # Champs vides tolérés
                    value = None
                title = unicode(title, 'utf8')
            # Passed
            if value is True:
                continue
            yield {'number': number, 'title': title, 'expr': expr,
                    'level': level, 'page': page,
                    'debug': u"'%s' = '%s'" % (unicode(expr, 'utf8'), value)}


    def get_export_query(self, table, pages=freeze([]),
            exclude=freeze(['B'])):
        # Primary key first
        names = ['code_ua']
        code_ua = self.get_code_ua()
        values = ["'%s'" % item for item in [code_ua]]
        handler = self.handler
        schema = self.handler.schema
        # Ensure order consistency
        for key in sorted(schema.keys()):
            page = key[0]
            if pages and page not in pages:
                continue
            if page in exclude:
                continue
            names.append(key)
            datatype = schema[key]
            value = quote_sql(datatype.encode_sql(handler.get_value(key)))
            values.append(value)

        return "INSERT INTO `%s` (%s) VALUES (%s);" % (table,
                ','.join(names), ','.join(values))



###########################################################################
# Register
register_resource_class(BM2009Form)
register_field('is_bm', Boolean(is_indexed=True, is_stored=True))
register_field('code_ua', Integer(is_indexed=True, is_stored=True))
register_field('departement', Unicode(is_indexed=True, is_stored=True))
