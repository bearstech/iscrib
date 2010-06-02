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
from itools.datatypes import String, Boolean, Integer

# Import from ikaaro
from ikaaro.registry import register_field


# Import from scrib
from base2009_views import Base2009Form_New, Base2009Form_Help
from datatypes import NumInteger, NumDecimal, NumTime, NumShortTime, Text
from datatypes import NumDate, NumShortDate, NumDigit, Unicode, EnumBoolean
from datatypes import EnumCV, make_enumerate
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
    'text': Text,
    'enumcv': EnumCV}


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
            if not (page.isalpha() or page == '0'): # FIXME
                raise ValueError, """page "%s" n'est pas valide""" % page
            page_fields = pages.setdefault(page, set())
            page_fields.add(name)
            page_numbers.append(page)
        # Mandatory
        is_mandatory = is_mandatory.strip()
        is_mandatory = not is_mandatory or is_mandatory.upper() == 'OUI'
        # Read-only
        readonly = readonly.strip().upper() == 'OUI'
        # Sum
        sum = sum.strip()
        # Add to the schema
        page_numbers = tuple(page_numbers)
        schema[name] = datatype(representation=representation,
                length=(length.strip() or representation),
                pages=page_numbers, is_mandatory=is_mandatory,
                readonly=readonly, sum=sum, dependances=dependances.split(),
                sql_field=sql_field)
    return schema, pages



def get_controls(path):
    path = get_abspath(path)
    handler = CSVFile(path)
    rows = handler.get_rows()
    # Skip header
    rows.next()
    return list(rows)



class Base2009Handler(FormHandler):

    def is_disabled_by_dependency(self, name):
        for dep_name in self.schema[name].dependances:
            if self.get_value(dep_name) is not True:
                return True
            # Second level
            for dep_dep_name in self.schema[dep_name].dependances:
                if self.get_value(dep_dep_name) is not True:
                    return True
        return False


    def get_reverse_dependencies(self, name):
        return [dep_name
                for dep_name, dep_datatype in self.schema.iteritems()
                if name in dep_datatype.dependances]



class Base2009Form(Form):
    class_icon48 = 'scrib2009/images/form48.png'

    # Views
    new_instance = Base2009Form_New()
    aide = Base2009Form_Help()


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(Form.get_metadata_schema(),
                code_ua=Integer,
                departement=String,
                is_first_time=Boolean(default=True))


    def _get_catalog_values(self):
        return merge_dicts(Form._get_catalog_values(self),
                code_ua=self.get_property('code_ua'),
                departement=self.get_property('departement'))


    ######################################################################
    # API

    def get_code_ua(self):
        return self.get_property('code_ua')


    def get_departement(self):
        return self.get_property('departement')


    def is_bm(self):
        return self.parent.is_bm()


    def is_bdp(self):
        return self.parent.is_bdp()


    def is_ready(self):
        for name, datatype in self.get_invalid_fields():
            if datatype.is_mandatory:
                return False
        for control in self.get_failed_controls():
            if control['level'] == '2':
                return False
        return True


    def is_first_time(self):
        # 0008120 Le handler est prérempli donc marquage manuel
        return self.get_property('is_first_time')


    def get_invalid_fields(self, pages=freeze([]), exclude=freeze([''])):
        handler = self.handler
        schema = handler.schema
        fields = handler.fields
        for name in sorted(fields):
            if pages and name[0] not in pages:
                continue
            if name[0] in exclude:
                continue
            if handler.is_disabled_by_dependency(name):
                continue
            datatype = schema[name]
            value = fields[name]
            is_valid = datatype.is_valid(datatype.encode(value))
            is_sum_valid = True
            if datatype.sum:
                sum = handler.sum(datatype, datatype.sum, **fields)
                is_sum_valid = (sum is None or sum == value)
            if datatype.is_mandatory:
                # Vérifie toujours les champs obligatoires
                if is_valid and is_sum_valid:
                    continue
            else:
                # Vérifie seulement si quelque chose a été saisi
                if not datatype.encode(value):
                    continue
                if is_valid and is_sum_valid:
                    continue
            yield name, datatype


    def _get_controls(self, levels=freeze([]), pages=freeze([]),
            exclude=freeze([''])):
        for number, title, expr, level, page in self.handler.controls:
            if level not in levels:
                continue
            if pages and page not in pages:
                continue
            if page in exclude:
                continue
            # Risque d'espaces insécables autour des guillemets
            expr = expr.replace(' ', ' ').strip()
            if not expr:
                continue
            try:
                # Précision pour les informations statistiques
                if level == '0':
                    vars = self.get_floating_vars()
                else:
                    vars = self.get_vars()
                value = eval(expr, vars)
            except ZeroDivisionError:
                # Division par zéro toléré
                value = None
            except (InvalidOperation, ValueError):
                # Champs vides tolérés
                value = None
            # Passed
            if value is True and '0' not in levels:
                continue
            # Le titre contient des formules
            if '[' in title:
                expanded = []
                for is_expr, token in parse_control(title):
                    if not is_expr:
                        expanded.append(unicode(token, 'utf8'))
                    else:
                        if level == '0':
                            vars = self.get_floating_vars()
                        else:
                            vars = self.get_vars()
                        try:
                            value = eval(token, vars)
                        except ZeroDivisionError:
                            value = None
                        expanded.append(unicode(value))
                title = u"".join(expanded)
            else:
                title = unicode(title, 'utf8')
            if value is True:
                value = u"Vrai"
            elif value is False:
                value = u"Faux"
            elif isinstance(value, NumDecimal):
                value = str(value.round()).replace('.', ',')
            yield {'number': number, 'title': title, 'expr': expr,
                    'level': level, 'page': page, 'value': value,
                    'debug': u"'%s' = '%s'" % (unicode(expr, 'utf8'), value)}


    def get_info_controls(self, pages=freeze([]), exclude=freeze([''])):
        # 0008709 Contrôles purement informatifs
        for control in self._get_controls(levels=['0'], pages=pages,
                exclude=exclude):
            yield control


    def get_failed_controls(self, pages=freeze([]), exclude=freeze([''])):
        for control in self._get_controls(levels=['1', '2'], pages=pages,
                exclude=exclude):
            yield control


    def get_export_query(self, table, pages=freeze([]),
            exclude=freeze([''])):
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
            names.append('`%s`' % key)
            datatype = schema[key]
            value = quote_sql(datatype.encode_sql(handler.get_value(key)))
            values.append(value)
        return "INSERT INTO `%s` (%s) VALUES (%s);" % (table,
                ','.join(names), ','.join(values))



###########################################################################
# Register
register_field('code_ua', Integer(is_indexed=True, is_stored=True))
register_field('departement', String(is_indexed=True, is_stored=True))
