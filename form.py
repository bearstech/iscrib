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
from __future__ import print_function
from decimal import InvalidOperation

# Import from itools
from itools.core import merge_dicts, freeze
from itools.fs import FileName
from itools.gettext import MSG
from itools.handlers import checkid
from itools.i18n import format_number
from itools.handlers import File as FileHandler

# Import from ikaaro
from ikaaro.file import File
from ikaaro.file_views import File_NewInstance
from ikaaro.folder import Folder
from ikaaro.folder_views import GoToSpecificDocument
from ikaaro.registry import get_resource_class
from ikaaro.utils import generate_name

# Import from iscrib
from datatypes import Numeric, NumDecimal, Unicode, FileImage
from formpage import FormPage
from form_views import Form_View, Form_Send, Form_Export, Form_Print
from utils import SI, get_page_number, parse_control
from schema import Variable
from workflow import workflow, FINISHED



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
        if datatype.multiple:
            values = []
            for data in data.split():
                try:
                    value = datatype.decode(data)
                except ValueError:
                    value = data
                values.append(value)
            return values
        try:
            value = datatype.decode(data)
        except ValueError:
            value = data
        return value


    def set_value(self, name, value, schema):
        datatype = schema[name]
        if datatype.multiple:
            datas = []
            for value in value:
                try:
                    data = datatype.encode(value)
                except ValueError:
                    # XXX
                    data = unicode(value).encode('UTF-8')
                datas.append(data)
            data = ' '.join(datas)
        else:
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
    class_views = ['pageA', 'export', 'show']
    class_handler = FormHandler
    class_schema = merge_dicts(File.class_schema,
            form_state=Unicode(indexed=True, stored=True))

    workflow = workflow

    # Views
    new_instance = File_NewInstance(access='is_allowed_to_add_form')
    send = Form_Send()
    export = Form_Export()
    print = Form_Print()
    show = GoToSpecificDocument(access='is_allowed_to_edit',
            title=MSG(u"Manage your Data Collection Application"),
            specific_document='..', specific_view='view')


    def __getattr__(self, name):
        """Vues des pages du formulaire dynamiques
        """
        page_number = get_page_number(name)
        page = self.get_formpage(page_number)
        if page is None:
            raise AttributeError, name
        return Form_View(page_number=page.get_page_number())


    def get_links(self):
        links = super(Form, self).get_links()
        base = self.parent.get_canonical_path()
        schema = self.get_schema()
        for key, datatype in schema.iteritems():
            if isinstance(datatype, Numeric):
                pass
            elif issubclass(datatype, FileImage):
                value = self.handler.get_value(key, schema)
                if value:
                    links.add(str(base.resolve2(value)))
        return links


    ######################################################################
    # API
    def get_param_folder(self):
        """Return the folder resource where parameters are stored.
        """
        return self.parent


    def get_schema_resource(self):
        """Return the CSV schema resource.
        """
        return self.get_param_folder().get_resource('schema')


    def get_schema_pages(self):
        """Load the schema from the CSV.
        """
        return self.get_schema_resource().handler.get_schema_pages()


    def get_schema(self):
        schema, pages = self.get_schema_pages()
        return schema


    def get_pages(self):
        schema, pages = self.get_schema_pages()
        return pages


    def get_fields(self, schema):
        handler = self.get_form().handler
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
        return self.get_controls_resource().handler


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


    def get_form_title(self):
        param = self.get_param_folder()
        if self.name == param.default_form:
            return MSG(u"{application}: <em>Test Form</em>",
                    format='replace_html', application=param.get_title())
        form_title = None
        user = self.get_resource('/users/' + self.name, soft=True)
        if user is not None:
            form_title = user.get_title()
        if form_title is None:
            form_title = self.get_title()
        return MSG(u"{application}: {form}", application=param.get_title(),
                form=form_title)


    ######################################################################
    # Security
    def is_ready(self):
        return self.get_workflow_state() == FINISHED


    def is_first_time(self):
        handler = self.get_form().handler
        # Force loading
        handler._raw_fields
        return handler.timestamp is None


    def is_disabled_by_dependency(self, name, schema, fields):
        dependency = schema[name].dependency
        if not dependency:
            return False
        vars = self.get_vars(fields)
        try:
            return not eval(dependency, vars)
        except (ZeroDivisionError, InvalidOperation, ValueError):
            return False


    @staticmethod
    def get_reverse_dependency(name, schema):
        return [dep_name
                for dep_name, dep_datatype in schema.iteritems()
                if name == dep_datatype.dependency]


    def get_dep_names(self, name, schema, iteration=0, max_dep_names=3):
        dep_names = []
        for dep_name in self.get_reverse_dependency(name, schema):
            dep_names.append(dep_name)
            if iteration < max_dep_names:
                dep_names.extend(self.get_dep_names(dep_name, schema,
                    iteration=iteration+1))
        return dep_names


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
            if datatype.formula:
                sum = datatype.sum(datatype.formula, schema, fields)
                is_sum_valid = (sum is None or sum == value)
            if datatype.mandatory:
                # False or 0 must be valid
                if unicode(value).strip() and is_valid and is_sum_valid:
                    continue
            else:
                if is_valid and is_sum_valid:
                    continue
            yield name, datatype


    def get_controls_namespace(self, levels=freeze([]), pages=freeze([]),
            exclude=freeze([''])):
        schema = self.get_schema()
        fields = self.get_fields(schema)
        controls = self.get_controls()
        get_record_value = controls.get_record_value
        for record in controls.get_records():
            level = get_record_value(record, 'level')
            if level not in levels:
                continue
            variable = get_record_value(record, 'variable')
            page = Variable.get_page_number(variable)
            if pages and page not in pages:
                continue
            if page in exclude:
                continue
            expression = get_record_value(record, 'expression')
            try:
                # Précision pour les informations statistiques
                if level == '0':
                    vars = self.get_floating_vars(fields)
                else:
                    vars = self.get_vars(fields)
                value = eval(expression, vars)
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
            title = get_record_value(record, 'title')
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
                value = MSG(u"True")
            elif value is False:
                value = MSG(u"False")
            elif isinstance(value, NumDecimal):
                value = format_number(value.value)
            number = get_record_value(record, 'number')
            yield {
                'number': number,
                'title': title,
                'level': level,
                'variable': variable,
                'page': page,
                'value': value,
                'debug': u"'%s' = '%s'" % (expression, value)}


    def get_info_controls(self, pages=freeze([]), exclude=freeze([''])):
        for control in self.get_controls_namespace(levels=['0'], pages=pages,
                exclude=exclude):
            yield control


    def get_failed_controls(self, pages=freeze([]), exclude=freeze([''])):
        for control in self.get_controls_namespace(levels=['1', '2'],
                pages=pages, exclude=exclude):
            yield control


    def save_file(self, filename, mimetype, body):
        name, extension, language = FileName.decode(filename)
        parent = self.parent
        used = parent.get_names()
        name = checkid(name) or 'invalid'
        name = generate_name(name, used)
        cls = get_resource_class(mimetype)
        metadata = {
                'format': mimetype,
                'filename': filename,
                'extension': extension}
        parent.make_resource(name, cls, body=body, **metadata)
        return name
