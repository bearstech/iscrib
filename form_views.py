# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Taverne Sylvain <sylvain@itaapy.com>
# Copyright (C) 2009-2010 Hervé Cauwelier <herve@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from itools
from itools.csv import CSVFile
from itools.datatypes import String, Enumerate
from itools.gettext import MSG
from itools.web import BaseView, STLView, STLForm, INFO, ERROR

# Import from ikaaro

# Import from iscrib
from datatypes import Numeric
from utils import get_page_number, set_html_message
from widgets import is_mandatory_filled
from workflow import WorkflowState, EMPTY, PENDING, SENT, EXPORTED


# Messages
MSG_SAVED_ERROR = ERROR(u"WARNING! There are missing or invalid "
        u"fields.")
MSG_SAVED = INFO(u"The page is saved. Check your input in the "
        u'<a href=";send">Input Control</a> tab.')
MSG_SENT = INFO(u"Your form was successfully sent.")
MSG_EXPORTED_ITAAPY = ERROR(u'To export to a SQL database, contact <a '
        u'href="http://www.itaapy.com/contact">Itaapy</a>')


class Generic(String):

    @classmethod
    def decode(cls, data):
        if data:
            return data.strip()
        return data


Multiple = Generic(multiple=True)



class Form_View(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    template = '/ui/iscrib/form/view.xml'
    query_schema = {'view': String}
    schema = {'page_number': String}
    hidden_fields = []


    def get_page_title(self, resource, context):
        return resource.get_form_title()


    def get_hidden_fields(self, resource, context):
        schema = resource.get_schema()
        handler = resource.get_form().handler
        return [{'name': field, 'value': handler.get_value(field, schema)}
                for field in self.hidden_fields]


    def get_menu(self, resource, context):
        menu = []
        view_name = context.view_name or 'pageA'
        view_name = view_name.lower()
        for formpage in resource.get_formpages():
            menu.append({'title': formpage.get_title(),
                'href': ';page%s' % get_page_number(formpage.name),
                'active': 'active' if formpage.name == view_name else None})
        return menu


    def is_skip_print(self, resource, context):
        return False


    def get_namespace(self, resource, context):
        try:
            # Return from POST
            bad_types = context.bad_types
        except AttributeError:
            # Fresh GET: not bad yet
            context.bad_types = []
        user = context.user
        skip_print = self.is_skip_print(resource, context)
        view = context.query['view']
        if view == 'printable':
            skip_print = True
        ac = resource.get_access_control()
        readonly = not ac.is_allowed_to_edit(context.user, resource)
        formpage = resource.get_formpage(self.page_number)
        namespace = formpage.get_namespace(resource, self, context,
                skip_print=skip_print, readonly=readonly)
        namespace['hidden_fields'] = self.get_hidden_fields(resource,
                context)
        namespace['menu'] = self.get_menu(resource, context)
        return namespace


    def action(self, resource, context, form):
        schema, pages = resource.get_schema_pages()
        fields = resource.get_fields(schema)
        page_number = form['page_number']
        handler = resource.get_form().handler
        bad_types = []
        for key in pages[page_number]:
            value = ''
            datatype = schema[key]
            # Can't use because they need to be stored
            #if datatype.readonly:
            #    continue
            # Can't use "if not/continue" pattern here
            if context.get_form_value(key) is not None:
                # Do not use form schema, only default String
                if datatype.multiple:
                    data = context.get_form_value(key, type=Multiple)
                else:
                    data = context.get_form_value(key, type=Generic)
                try:
                    value = datatype.decode(data)
                except Exception:
                    # Keep invalid values
                    value = data
                # Compare sums
                if datatype.formula:
                    expected = datatype.sum(datatype.formula, schema,
                            # Raw form, not the filtered one
                            context.get_form())
                    # Sum inputed
                    if data and value != expected:
                        # What we got was OK so blame the user
                        if expected is not None:
                            bad_types.append(key)
                    # Sum deduced
                    else:
                        # Got it right!
                        if expected is not None:
                            value = expected
                        # Got it wrong!
                        else:
                            bad_types.append(key)
                # Mandatory
                elif datatype.is_mandatory and not data:
                    bad_types.append(key)
                # Invalid (0008102 and mandatory -> and filled)
                elif data and not datatype.is_valid(data):
                    bad_types.append(key)
            # First skip instance datatypes:
            #   TypeError: issubclass() arg 1 must be a class
            elif isinstance(datatype, Numeric):
                pass
            # Now detect unchecked checkboxes
            elif issubclass(datatype, Enumerate):
                if not is_mandatory_filled(datatype, key, value, schema,
                        fields, context):
                    bad_types.append(key)
            handler.set_value(key, value, schema)
            fields[key] = value
        # Reindex
        context.database.change_resource(resource)
        # Transmit list of errors when returning GET
        if bad_types:
            context.message = MSG_SAVED_ERROR
            context.bad_types = bad_types
        else:
            set_html_message(MSG_SAVED, context)
        if resource.get_workflow_state() == EMPTY:
            resource.set_workflow_state(PENDING)



class Form_Send(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    template = '/ui/iscrib/form/send.xml'
    title = MSG(u"Input Control")
    query_schema = {'view': String}


    def get_page_title(self, resource, context):
        return resource.get_form_title()


    def get_namespace(self, resource, context):
        namespace = {}
        namespace['first_time'] = resource.is_first_time()
        # Errors
        errors = []
        warnings = []
        infos = []
        # Invalid fields
        for name, datatype in resource.get_invalid_fields():
            if datatype.formula:
                title = MSG(u"{name} is not equal to {formula}".gettext(
                    name=name, formula=datatype.formula))
            else:
                title = MSG(u"{name} invalid").gettext(name=name)
            info = {'number': name,
                    'title': title,
                    'href': ';page{page}#field_{name}'.format(
                        page=datatype.pages[0], name=name),
                    'debug': str(type(datatype))}
            if datatype.is_mandatory:
                errors.append(info)
            else:
                warnings.append(info)
        # Failed controls
        for control in resource.get_failed_controls():
            control['href'] = ';page%s#field_%s' % (control['page'],
                    control['variable'])
            if control['level'] == '2':
                errors.append(control)
            else:
                warnings.append(control)
        # Informative controls
        for control in resource.get_info_controls():
            control['href'] = ';page%s#field_%s' % (control['page'],
                    control['variable'])
            infos.append(control)
        namespace['controls'] = {'errors': errors, 'warnings': warnings,
                'infos': infos}
        # ACLs
        user = context.user
        ac = resource.get_access_control()
        is_allowed_to_export = ac.is_allowed_to_export(user, resource)
        namespace['is_allowed_to_export'] = is_allowed_to_export
        # State
        namespace['statename'] = statename = resource.get_statename()
        namespace['form_state'] = WorkflowState.get_value(
                resource.get_workflow_state())
        # Transitions
        namespace['can_send'] = statename == PENDING and not errors
        namespace['can_export'] = is_allowed_to_export and not errors
        # Debug
        namespace['debug'] = context.get_form_value('debug')
        # Print
        namespace['skip_print'] = False
        if context.query['view'] == 'printable':
            namespace['skip_print'] = True
        return namespace


    def action_send(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire est soumis.
        """
        resource.set_workflow_state(SENT)

        context.message = MSG_SENT


    def action_export(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire est exporté.
        """
        resource.set_workflow_state(EXPORTED)

        # XXX
        context.commit = False
        set_html_message(MSG_EXPORTED_ITAAPY, context)



class Form_Export(BaseView):
    access = 'is_allowed_to_view'
    title = MSG(u"Download form")


    def GET(self, resource, context, encoding='cp1252'):
        if not resource.is_ready():
            return MSG(u"Your form is not finished "
                    u"yet.").gettext().encode('utf8')

        # construct the csv
        csv = CSVFile()
        csv.add_row(["Chapitre du formulaire", "rubrique", "valeur"])
        schema = resource.get_schema()
        handler = resource.get_form().handler
        for name, datatype in sorted(schema.iteritems()):
            value = handler.get_value(name, schema)
            try:
                value = datatype.encode(value, encoding)
            except TypeError:
                value = datatype.encode(value)
            if type(value) is not str:
                raise ValueError, str(type(datatype))
            csv.add_row([datatype.pages[0], name, value])

        context.set_content_type('text/comma-separated-values')
        context.set_content_disposition('attachment',
                filename="%s.csv" % (resource.name))

        return csv.to_str(separator=';')



class Form_Print(STLView):
    access = 'is_allowed_to_view'
    title=MSG(u"Print form")
    template = '/ui/iscrib/form/print.xml'
    pages = []


    def get_page_title(self, resource, context):
        return resource.get_form_title()


    def get_namespace(self, resource, context):
        context.query['view'] = 'printable'
        context.bad_types = []
        forms = []
        for page_number in resource.get_page_numbers():
            formpage = resource.get_formpage(page_number)
            view = getattr(resource, 'page%s' % page_number)
            forms.append(formpage.get_namespace(resource, view, context,
                skip_print=True))
        namespace = {}
        namespace['forms'] = forms
        return namespace
