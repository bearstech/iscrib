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

# Import from the Standard Library
from decimal import InvalidOperation

# Import from itools
from itools.csv import CSVFile
from itools.core import merge_dicts, freeze
from itools.datatypes import String, Enumerate
from itools.gettext import MSG
from itools.log import log_debug
from itools.web import BaseView, STLView, STLForm, INFO, ERROR

# Import from ikaaro

# Import from iscrib
from buttons import InputControlLink, PagePrintLink, FormPrintLink
from buttons import SaveButton
from datatypes import Numeric, FileImage
from utils import get_page_number, force_encode, is_print, set_print
from widgets import is_mandatory_filled
from workflow import WorkflowState, EMPTY, PENDING, FINISHED, EXPORTED


# Messages
ERR_INVALID = ERROR(u"The following fields are invalid: {fields}.",
        format='replace_html')
ERR_MANDATORY = ERROR(u"The following fields are mandatory: {fields}.",
        format='replace_html')
ERR_BAD_SUMS = ERROR(u"The following sums are invalid: {fields}.",
        format='replace_html')
MSG_SAVED = INFO(u"The page is saved. Check your input in the "
        u'<a href=";send">Input Control</a> tab.', format='html')
MSG_FINISHED = INFO(u"Your form is finished. "
        u"Your correspondent has been informed.")
MSG_EXPORTED_ITAAPY = ERROR(u'To export to a SQL database, contact <a '
        u'href="http://www.itaapy.com/contact">Itaapy</a>', format='html')


class Single(String):

    @classmethod
    def decode(cls, data):
        if type(data) is str:
            return data.strip()
        return data


Multiple = Single(multiple=True)



class Form_View(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    template = '/ui/iscrib/form/view.xml'
    title = MSG(u"Start filling")
    schema = freeze({
        'page_number': String})
    hidden_fields = []
    toolbar = freeze([
        InputControlLink, PagePrintLink, FormPrintLink, SaveButton])
    actions = freeze([SaveButton])


    def get_page_title(self, resource, context):
        return resource.get_form_title()


    def get_hidden_fields(self, resource, context):
        schema = resource.get_schema()
        handler = resource.get_form().handler
        return [{
            'name': field,
            'value': handler.get_value(field, schema)}
                for field in self.hidden_fields
                if field[0] == self.page_number]


    def get_application_menu(self, resource, context):
        parent = resource.parent
        if resource.name == parent.default_form:
            return parent.menu.GET(parent, context)
        return None


    def get_menu(self, resource, context):
        menu = []
        view_name = context.view_name or 'pageA'
        view_name = view_name.lower()
        for formpage in resource.get_formpages():
            menu.append({
                'title': formpage.get_title(),
                'href': ';page%s' % get_page_number(formpage.name),
                'class': 'active' if formpage.name == view_name else None})
        if len(menu) == 1:
            return []
        return menu


    def is_skip_print(self, resource, context):
        return False


    def get_toolbar_namespace(self, resource, context, readonly):
        actions = []
        for button in self.toolbar:
            actions.append(button(resource=resource, context=context,
                readonly=readonly, page_number=self.page_number))
        return actions


    def get_actions_namespace(self, resource, context, readonly):
        actions = []
        for button in self.actions:
            actions.append(button(resource=resource, context=context,
                readonly=readonly))
        return actions


    def get_namespace(self, resource, context):
        try:
            # Return from POST
            context.bad_types
        except AttributeError:
            # Fresh GET: not bad yet
            context.bad_types = set()
        skip_print = self.is_skip_print(resource, context)
        if is_print(context):
            skip_print = True
        ac = resource.get_access_control()
        readonly = not ac.is_allowed_to_edit(context.user, resource)
        formpage = resource.get_formpage(self.page_number)
        namespace = formpage.get_namespace(resource, self, context,
                skip_print=skip_print, readonly=readonly)
        namespace['hidden_fields'] = self.get_hidden_fields(resource,
                context)
        namespace['application_menu'] = self.get_application_menu(resource,
                context)
        namespace['menu'] = self.get_menu(resource, context)
        namespace['toolbar'] = self.get_toolbar_namespace(resource, context,
                readonly)
        namespace['actions'] = self.get_actions_namespace(resource, context,
                readonly)
        return namespace


    def action(self, resource, context, form):
        schema, pages = resource.get_schema_pages()
        fields = resource.get_fields(schema)
        page_number = form['page_number']
        handler = resource.get_form().handler
        formpage = resource.get_formpage(page_number)

        # First save everything even invalid
        for field in formpage.get_fields():
            datatype = schema[field]
            value = fields[field]
            # Avoid "TypeError: issubclass() arg 1 must be a class"
            if isinstance(datatype, Numeric):
                pass
            elif issubclass(datatype, FileImage):
                # Delete existing file
                if context.get_form_value(field + '_delete'):
                    resource.parent.del_resource(value, ref_action='force')
                    fields[field] = ''
                    handler.set_value(field, '', schema)
            # Decode form data
            if context.get_form_value(field) is not None:
                # First the raw data
                if datatype.multiple:
                    data = context.get_form_value(field, type=Multiple)
                else:
                    data = context.get_form_value(field, type=Single)
                # Then the decoded value
                try:
                    value = datatype.decode(data)
                except Exception:
                    # Keep invalid values
                    value = data
                # Avoid "TypeError: issubclass() arg 1 must be a class"
                if isinstance(datatype, Numeric):
                    pass
                elif issubclass(datatype, FileImage):
                    # Load file
                    value = resource.save_file(*data)
            fields[field] = value
            handler.set_value(field, value, schema)

        # Then check bad types
        invalid = []
        mandatory = []
        bad_sums = []
        for field in formpage.get_fields():
            if resource.is_disabled_by_dependency(field, schema, fields):
                continue
            datatype = schema[field]
            # Raw data
            if datatype.multiple:
                data = context.get_form_value(field, type=Multiple)
            else:
                data = context.get_form_value(field, type=Single)
            # Decoded value
            value = fields[field]
            # Compute formula and compare
            if datatype.formula:
                try:
                    expected = datatype.sum(datatype.formula, schema,
                            # Raw form, not the filtered one
                            context.get_form())
                except InvalidOperation:
                    expected = None
                # Result given
                if data and value != expected:
                    # What we got was OK so blame the user
                    if expected is not None:
                        log = "field {0!r} data {1!r} value {2!r} bad sum"
                        log_debug(log.format(field, data, value))
                        if field not in bad_sums:
                            bad_sums.append(field)
                # Result deduced
                else:
                    # Got it right!
                    if expected is not None:
                        value = expected
                        # Fill the form
                        fields[field] = value
                        handler.set_value(field, value, schema)
                    # Got it wrong!
                    else:
                        log = "field {0!r} data {1!r} value {2!r} bad sum"
                        log_debug(log.format(field, data, value))
                        if field not in bad_sums:
                            bad_sums.append(field)
            # Mandatory
            if not data and datatype.mandatory:
                log = "field {0!r} data {1!r} value {2!r} mandatory"
                log_debug(log.format(field, data, value))
                mandatory.append(field) if field not in mandatory else None
            # Invalid (0008102 and mandatory -> and filled)
            elif data and not datatype.is_valid(data):
                log = "field {0!r} data {1!r} value {2!r} invalid"
                log_debug(log.format(field, data, value))
                if field not in invalid:
                    invalid.append(field)
            # Avoid "TypeError: issubclass() arg 1 must be a class"
            if isinstance(datatype, Numeric):
                pass
            elif issubclass(datatype, Enumerate):
                # Detect unchecked checkboxes
                if not is_mandatory_filled(datatype, field, value, schema,
                        fields, context):
                    log = "field {0!r} data {1!r} value {2!r} not filled"
                    log_debug(log.format(field, data, value))
                    if field not in mandatory:
                        mandatory.append(field)

        # Reindex
        context.database.change_resource(resource)
        # Transmit list of errors when returning GET
        pattern = u'<a href="#field_{name}">{name}</a>'
        messages = []
        bad_types = set()
        for fields, message in [
                (invalid, ERR_INVALID),
                (mandatory, ERR_MANDATORY),
                (bad_sums, ERR_BAD_SUMS)]:
            if fields:
                bad_types.update(fields)
                fields = [pattern.format(name=f) for f in sorted(fields)]
                messages.append(message(fields=", ".join(fields)))
        if messages:
            context.bad_types = bad_types
            context.message = messages
        else:
            context.message = MSG_SAVED
        if resource.get_workflow_state() == EMPTY:
            resource.set_workflow_state(PENDING)



class Form_Send(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    template = '/ui/iscrib/form/send.xml'
    title = MSG(u"Input Control")
    query_schema = freeze({
        'view': String})


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
            if datatype.mandatory:
                errors.append(info)
            else:
                warnings.append(info)
        # Failed controls
        for control in resource.get_failed_controls(context):
            control['href'] = ';page%s#field_%s' % (control['page'],
                    control['variable'])
            if control['level'] == '2':
                errors.append(control)
            else:
                warnings.append(control)
        # Informative controls
        for control in resource.get_info_controls(context):
            control['href'] = ';page%s#field_%s' % (control['page'],
                    control['variable'])
            infos.append(control)
        namespace['controls'] = {
                'errors': errors,
                'warnings': warnings,
                'infos': infos}
        # ACLs
        user = context.user
        ac = resource.get_access_control()
        is_allowed_to_export = ac.is_allowed_to_export(user, resource)
        namespace['is_allowed_to_export'] = is_allowed_to_export
        # State
        namespace['statename'] = statename = resource.get_workflow_state()
        namespace['form_state'] = WorkflowState.get_value(
                resource.get_workflow_state())
        # Transitions
        namespace['can_send'] = statename == PENDING and not errors
        namespace['can_export'] = is_allowed_to_export and not errors
        # Debug
        namespace['debug'] = context.get_form_value('debug')
        # Print
        namespace['skip_print'] = is_print(context)
        return namespace


    def action_send(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire est soumis.
        """
        resource.set_workflow_state(FINISHED)

        context.message = MSG_FINISHED


    def action_export(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire est exporté.
        """
        resource.set_workflow_state(EXPORTED)

        # XXX
        context.commit = False
        context.message = MSG_EXPORTED_ITAAPY



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
            data = force_encode(value, datatype, encoding)
            if type(data) is not str:
                raise ValueError, str(type(datatype))
            csv.add_row([datatype.pages[0], name, data])

        context.set_content_type('text/comma-separated-values')
        context.set_content_disposition('attachment',
                filename="%s.csv" % (resource.name))

        return csv.to_str(separator=';')



class Form_Print(STLView):
    access = 'is_allowed_to_view'
    title=MSG(u"Print form")
    template = '/ui/iscrib/form/print.xml'
    styles = ['/ui/iscrib/print.css']
    pages = []


    def get_page_title(self, resource, context):
        return resource.get_form_title()


    def get_namespace(self, resource, context):
        set_print(context)
        context.bad_types = set()
        forms = []
        for page_number in resource.get_page_numbers():
            formpage = resource.get_formpage(page_number)
            view = getattr(resource, 'page%s' % page_number)
            ns = merge_dicts(formpage.get_namespace(resource, view, context,
                             skip_print=True), title=formpage.get_title())
            forms.append(ns)
        namespace = {}
        namespace['forms'] = forms
        return namespace
