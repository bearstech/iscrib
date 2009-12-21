# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Sylvain Taverne <sylvain@itaapy.com>
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
from itools.datatypes import Boolean, String
from itools.gettext import MSG
from itools.stl import set_prefix
from itools.web import BaseView, STLForm, INFO, ERROR

# Import from scrib
from datatypes import Numeric
from utils import parse_control


# Messages
MSG_ERREUR_SAUVEGARDE = ERROR(u"ATTENTION ! IL Y A DES RUBRIQUES MANQUANTES "
        u"ET/OU INVALIDES")
MSG_SAUVEGARDE = INFO(u"La page est enregistrée, veuillez vérifier votre "
        u"saisie dans l'onglet Contrôle de saisie")


class Form_View(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    query_schema = {'view': String}
    schema = {'page_number': String}


    def get_namespace(self, resource, context):
        try:
            # Return from POST
            bad_types = context.bad_types
        except AttributeError:
            # Fresh GET: find from current state
            context.bad_types = []
        user = context.user
        skip_print = user.is_voir_scrib()
        view = context.query['view']
        if view == 'printable':
            skip_print = True
        ac = resource.get_access_control()
        readonly = not ac.is_allowed_to_edit(context.user, resource)
        table = resource.get_resource(self.page_template % self.n)
        namespace = table.get_namespace(resource, self, context,
                skip_print=skip_print, readonly=readonly)
        return namespace


    def action(self, resource, context, form):
        page_number = form['page_number']
        handler = resource.handler
        bad_types = []
        for key in handler.pages[page_number]:
            # Can't use "if not/continue" pattern here
            datatype = handler.schema[key]
            if context.has_form_value(key):
                # Do not use form schema, only default String
                data = context.get_form_value(key).strip()
                try:
                    value = datatype.decode(data)
                except Exception:
                    # Keep invalid values
                    value = data
                # Compare sums
                if datatype.sum:
                    expected = handler.sum(datatype, datatype.sum,
                            # Raw form, not the filtered one
                            **context.request.get_form())
                    # Sum inputed
                    if data and data != expected:
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
                # Invalid
                elif not datatype.is_valid(data):
                    bad_types.append(key)
            # Skip Scrib instance datatypes
            elif isinstance(datatype, Numeric):
                pass
            # Unchecked checkboxes return no value
            elif issubclass(datatype, Boolean):
                value = False
            else:
                value = ''
            handler.set_value(key, value)
        # Reindex
        context.server.change_resource(resource)
        # Transmit list of errors when returning GET
        if bad_types:
            context.message = MSG_ERREUR_SAUVEGARDE
            context.bad_types = bad_types
        else:
            context.message = MSG_SAUVEGARDE



class Send_View(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    title = MSG(u"Contrôle de saisie")
    template = '/ui/scrib2009/Form_send.xml'
    query_schema = {'view': String}


    def get_namespace(self, resource, context):
        user = context.user
        handler = resource.handler
        namespace = {}
        namespace['first_time'] = first_time = resource.is_first_time()
        # Errors
        errors = []
        warnings = []
        controls = resource.handler.controls
        for number, title, expr, level, page in controls:
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
                            value = eval(token, resource.get_vars())
                        except ZeroDivisionError:
                            value = None
                        expanded.append(str(value))
                title = ''.join(expanded)
            else:
                try:
                    value = eval(expr, resource.get_vars())
                except ZeroDivisionError:
                    # Division par zéro toléré
                    value = None
                except InvalidOperation:
                    # Champs vides tolérés
                    value = None
            # Passed
            if value is True:
                continue
            # Failed
            info = {'number': number,
                    'title': title,
                    'page': page.replace('-', ''),
                    'debug': "'%s' = '%s'" % (str(expr), value)}
            errors.append(info) if level == '2' else warnings.append(info)
        namespace['controls'] = {'errors': errors,
                                 'warnings': warnings}
        # ACLs
        ac = resource.get_access_control()
        namespace['is_admin'] = ac.is_admin(user, resource)
        # Workflow - State
        namespace['statename'] = resource.get_statename()
        namespace['form_state'] = resource.get_form_state()
        # Workflow - Transitions
        namespace['can_send'] = can_send = not first_time and not errors
        namespace['can_export'] = can_send
        # Debug
        namespace['debug'] = context.has_form_value('debug')
        # Print
        namespace['skip_print'] = False
        view = context.query['view']
        if view == 'printable' or user.is_voir_scrib():
            namespace['skip_print'] = True
        return namespace



class Help_View(BaseView):
    access = 'is_allowed_to_view'
    title = MSG(u"Aide à la saisie")


    def GET(self, resource, context):
        page = context.get_query_value('page')
        app = resource.get_site_root()
        if page:
            # Aide spécifique
            response = context.response
            response.set_header('Content-Type', 'text/html; charset=UTF-8')
            resource = app.get_resource('Page' + page)
            return resource.handler.to_str()
        # Aide générale
        resource = app.get_resource('aide')
        prefix = resource.get_pathto(resource)
        return set_prefix(resource.get_html_data(), prefix)



class Todo_View(BaseView):
    access = 'is_allowed_to_view'


    def GET(self, resource, context):
        return 'TODO'
