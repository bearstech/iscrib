# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006-2010 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2009 Taverne Sylvain <sylvain@itaapy.com>
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
from itools.database import register_field
from itools.gettext import MSG
from itools.handlers import File as FileHandler

# Import from ikaaro
from ikaaro.file import File
from ikaaro.folder import Folder

# Import from iscrib
from datatypes import Numeric, NumDecimal, Unicode
from datatypes import WorkflowState
from form_views import Form_Send, Form_Export, Form_Print
from formpage import FormPage
from utils import SI, get_page_number, parse_control
from workflow import workflow, EMPTY, SENT, EXPORTED, MODIFIED



class MultipleForm(Folder):
    class_id = 'MultipleForm'


    def is_first_time(self):
        return not len(self.get_names())



class FormHandler(FileHandler):

    ######################################################################
    # Load/Save
    def new(self, encoding='UTF-8', **raw_fields):
        self._raw_fields = raw_fields


    def _load_state_from_file(self, file):
        """Load known values, the rest will be the default values.
        """
        raw_fields = {}
        for line in file.readlines():
            if ':' not in line:
                continue
            key, data = line.split(':', 1)
            raw_fields[key.strip()] = data.strip()
        self._raw_fields = raw_fields


    def to_str(self, encoding='UTF-8'):
        lines = []
        for key, value in self._raw_fields.iteritems():
            lines.append('%s:%s' % (key, value))
        return '\n'.join(lines)


    ######################################################################
    # API
    def get_value(self, name, schema):
        datatype = schema[name]
        data = self._raw_fields.get(name)
        if data is None:
            return datatype.get_default()
        try:
            value = datatype.decode(data)
        except ValueError:
            value = data
        return value


    def set_value(self, name, value, schema):
        datatype = schema[name]
        try:
            data = datatype.encode(value)
        except ValueError:
            # XXX
            data = unicode(value).encode('UTF-8')
        self._raw_fields[name] = data
        self.set_changed()



class Form(File):
    class_id = 'Form'
    class_title = MSG(u"Form")
    class_views = ['envoyer', 'exporter', 'imprimer']
    class_handler = FormHandler
    workflow = workflow

    # Views
    envoyer = Form_Send()
    exporter = Form_Export()
    imprimer = Form_Print()


    def get_catalog_values(self):
        return merge_dicts(File.get_catalog_values(self),
                form_state=self.get_form_state())


    ######################################################################
    # API
    def get_param_folder(self):
        """Return the folder resource where parameters are stored.
        """
        raise NotImplementedError


    def get_schema_resource(self):
        """Return the CSV schema resource.
        """
        return self.get_param_folder().get_resource('schema')


    def get_schema_pages(self):
        """Load the schema from the CSV.
        """
        handler = self.get_schema_resource().handler
        return handler.get_schema_pages()


    def get_schema(self):
        schema, pages = self.get_schema_pages()
        return schema


    def get_pages(self):
        schema, pages = self.get_schema_pages()
        return pages


    def get_form_handler(self):
        return self.handler


    def get_fields(self, schema):
        handler = self.get_form_handler()
        fields = {}
        for name in schema:
            fields[name] = handler.get_value(name, schema)
        return fields


    def get_vars(self, fields):
        return merge_dicts(fields, SI=SI)


    def get_floating_vars(self, fields):
        vars = {}
        for name, value in fields.iteritems():
            if isinstance(value, Numeric):
                vars[name] = NumDecimal(value.value)
            else:
                vars[name] = value
        return vars


    def get_controls_resource(self):
        """Return the CSV controls resource.
        """
        return self.get_param_folder().get_resource('controls')


    def get_controls(self):
        """Load the controls from the CSV.
        """
        handler = self.get_controls_resource().handler
        return handler.get_controls()


    def get_formpages(self):
        folder = self.get_param_folder()
        root = self.get_root()
        results = root.search(format=FormPage.class_id,
                parent_path=str(folder.get_canonical_path()))
        for brain in results.get_documents(sort_by='name'):
            formpage = root.get_resource(brain.abspath)
            yield formpage


    def get_page_numbers(self):
        """Return the ordered list of form page numbers.
        """
        page_numbers = []
        for formpage in self.get_formpages():
            page_number = get_page_number(formpage.name)
            page_numbers.append(page_number)
        return page_numbers


    def get_formpage(self, page_number):
        """Return the FormPage resource for this number of page.
        """
        if page_number is None:
            return None
        name = 'page%s' % page_number.lower()
        return self.get_param_folder().get_resource(name, soft=True)


    def get_form(self):
        """Shortcut to find the root form in MultipleForm.
        """
        return self


    ######################################################################
    # Security
    def is_ready(self):
        raise NotImplementedError


    def get_form_state(self):
        """Translate workflow state to user-friendly state.
        """
        state = self.get_workflow_state()
        # Match the enumerate in order to search by values
        get_value = WorkflowState.get_value
        if state == EMPTY:
            if self.is_first_time():
                return get_value('vide')
            return get_value('en_cours')
        elif state == SENT:
            return get_value('envoye')
        elif state == EXPORTED:
            return get_value('exporte')
        elif state == MODIFIED:
            return get_value('modifie')
        raise NotImplementedError, state


    def is_first_time(self):
        return self.get_form_handler().timestamp is None


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


    def get_controls_namespace(self, levels=freeze([]), pages=freeze([]),
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
                        expanded.append(token)
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
        for control in self.get_controls_namespace(levels=['0'], pages=pages,
                exclude=exclude):
            yield control


    def get_failed_controls(self, pages=freeze([]), exclude=freeze([''])):
        for control in self.get_controls_namespace(levels=['1', '2'],
                pages=pages, exclude=exclude):
            yield control



###########################################################################
# Register
register_field('form_state', Unicode(indexed=True, stored=True))
