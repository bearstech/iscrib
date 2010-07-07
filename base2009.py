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
from itools.core import merge_dicts, freeze
from itools.datatypes import String, Boolean, Integer

# Import from ikaaro
from ikaaro.registry import register_field


# Import from scrib
from base2009_views import Base2009Form_New, Base2009Form_Help
from datatypes import NumDecimal
from form import Form
from formpage import FormPage
from utils import parse_control


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
    # Form API
    def get_param_folder(self):
        if self.is_bm():
            path = 'param_bm'
        else:
            path = 'param_bdp'
        return self.get_site_root().get_resource(path)


    def get_schema_pages(self):
        handler = self.get_schema_resource().handler
        return handler.get_schema_pages()


    def get_schema(self):
        schema, pages = self.get_schema_pages()
        return schema


    def get_pages(self):
        schema, pages = self.get_schema_pages()
        return pages


    def get_controls(self):
        handler = self.get_controls_resource().handler
        return handler.get_controls()


    def get_page_numbers(self):
        folder = self.get_param_folder()
        page_numbers = []
        for page in folder.search_resources(cls=FormPage):
            page_numbers.append(page.name[4:].upper())
        return sorted(page_numbers)


    def get_formpage(self, pagenum):
        name = 'page%s' % pagenum.lower()
        return self.get_param_folder().get_resource(name)


    ######################################################################
    # Scrib API
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


    @staticmethod
    def is_disabled_by_dependency(name, schema, fields):
        for dep_name in schema[name].dependances:
            if fields[dep_name] is not True:
                return True
            # Second level
            for dep_dep_name in schema[dep_name].dependances:
                if fields[dep_dep_name] is not True:
                    return True
        return False


    @staticmethod
    def get_reverse_dependencies(name, schema):
        return [dep_name
                for dep_name, dep_datatype in schema.iteritems()
                if name in dep_datatype.dependances]


    def get_invalid_fields(self, pages=freeze([]), exclude=freeze([''])):
        schema = self.get_schema()
        fields = self.get_fields(schema)
        for name in sorted(fields):
            if pages and name[0] not in pages:
                continue
            if name[0] in exclude:
                continue
            if self.is_disabled_by_dependency(name, schema, fields):
                continue
            datatype = schema[name]
            value = fields[name]
            is_valid = datatype.is_valid(datatype.encode(value))
            is_sum_valid = True
            if datatype.sum:
                sum = self.sum(datatype, datatype.sum, schema, fields)
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
        schema = self.get_schema()
        fields = self.get_fields(schema)
        controls = self.get_controls()
        for number, title, expr, level, page in controls:
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
                    vars = self.get_floating_vars(fields)
                else:
                    vars = self.get_vars(fields)
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
            if u'[' in title:
                expanded = []
                for is_expr, token in parse_control(title):
                    if not is_expr:
                        expanded.append(unicode(token, 'utf8'))
                    else:
                        if level == '0':
                            vars = self.get_floating_vars(fields)
                        else:
                            vars = self.get_vars(fields)
                        try:
                            value = eval(token, vars)
                        except ZeroDivisionError:
                            value = None
                        expanded.append(unicode(value))
                title = u"".join(expanded)
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
        names = [u'code_ua']
        code_ua = self.get_code_ua()
        values = [u"'%s'" % item for item in [code_ua]]
        handler = self.handler
        schema = self.get_schema()
        # Ensure order consistency
        for key in sorted(schema.keys()):
            page = key[0]
            if pages and page not in pages:
                continue
            if page in exclude:
                continue
            names.append(u'`%s`' % key)
            datatype = schema[key]
            value = datatype.encode_sql(handler.get_value(key))
            if type(value) is not unicode:
                message = 'form "%s" field "%s" of type "%s"failed to encode'
                raise TypeError, message % (self.name, key, datatype)
            values.append(value)
        return u"INSERT INTO `%s` (%s) VALUES (%s);" % (table,
                u",".join(names), u",".join(values))



###########################################################################
# Register
register_field('code_ua', Integer(is_indexed=True, is_stored=True))
register_field('departement', String(is_indexed=True, is_stored=True))
