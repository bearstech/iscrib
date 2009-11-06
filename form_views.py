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

# Import from itools
from itools.datatypes import Boolean, String
from itools.gettext import MSG
from itools.html import HTMLParser
from itools.web import BaseForm, STLView, STLForm, INFO, ERROR

# Import from scrib
from utils import parse_control
from workflow import SENT, SEND, EXPORT


PAGE_FILENAME = '/ui/scrib2009/Page%s.table.csv'

# Print
PAGE_BREAK = list(HTMLParser('<div style="page-break-after: always"></div>'))
BREAK_HEADER = PAGE_BREAK[:1]
BREAK_FOOTER = PAGE_BREAK[1:]

# Messages
MSG_ERREUR_SAUVEGARDE = ERROR(
        u"ATTENTION ! "
        u"IL Y A DES RUBRIQUES MANQUANTES ET/OU INVALIDES")
MSG_SAUVEGARDE = INFO(
        u"La page est enregistrée, veuillez vérifier votre saisie dans : "
        u"Envoi du questionnaire")


class Form_View(BaseForm):
    # TODO STLView
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    schema = {'page_number': String}
    query_schema = {'view': String}


    def GET(self, resource, context):
        try:
            bad_types = context.bad_types
        except AttributeError:
            bad_types = context.bad_types = []
        view = context.query['view']
        table = resource.get_resource(PAGE_FILENAME % self.n)
        user = context.user
        skip_print = user.is_voir_scrib()
        if view == 'printable':
            skip_print = True
        readonly = False
        statename = resource.get_statename()
        if statename == SENT and (user.is_bm() or user.is_bdp()):
            # 0005566
            # Si le formulaire est dans l'état terminé,
            # une bibliothèque ne peut plus le modifier
            readonly = True
        return table.to_html(context, resource, self, skip_print=skip_print,
                             readonly=readonly)


    def action(self, resource, context, form):
        page_number = form['page_number']
        handler = resource.handler
        bad_types = []
        for key in handler.pages[page_number]:
            # Can't use "if not/continue" pattern here
            if context.has_form_value(key):
                # Do not use form schema, only default String
                data = context.get_form_value(key).strip()
                datatype = handler.schema[key]
                if datatype.somme:
                    expected_value = handler.somme(datatype, datatype.somme,
                            # Raw form, not the filtered one
                            **context.request.get_form())
                    if data:
                        try:
                            value = datatype.encode(datatype.decode(data))
                        except ValueError:
                            # Got it wrong!
                            bad_types.append(key)
                            continue
                        # Sum inputed
                        if expected_value != 'NC' and value != expected_value:
                            # Not what we get
                            if expected_value is not None:
                                # What we got was OK so blame the user
                                bad_types.append(key)
                                continue
                        # Else, we got it wrong anyway
                    else:
                        # Sum computed
                        if expected_value is not None:
                            # Got it right!
                            value = expected_value
                        else:
                            # Got it wrong!
                            bad_types.append(key)
                            continue
                elif datatype.is_mandatory and not data:
                    bad_types.append(key)
                    continue
                if datatype.is_valid(data):
                    value = datatype.decode(data)
                else:
                    bad_types.append(key)
                    continue
            elif isinstance(datatype, Boolean):
                # Default value for missing checkbox
                value = False
            else:
                # Nothing to save
                continue
            # TODO Save the value wether it is good or wrong
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
    title = MSG(u"Envoyer")
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
        # Print
        namespace['skip_print'] = False
        view = context.query['view']
        if view == 'printable' or user.is_voir_scrib():
            namespace['skip_print'] = True
        return namespace



class Help_View(STLView):
    access = 'is_allowed_to_view'
    schema = {'page': String}


    def get_template(self, resource, context):
        # avoid skin template
        context.response.set_header('Content-Type',
                                    'text/html; charset=UTF-8')
        # Get template
        page = context.query['page']
        if page is None:
            template = 'notice.xml'
        elif page == 'controls':
            template = 'controls.xml'
        else:
            template = 'page%s.xml' % page
        return self.get_resource('/ui/scrib2009/help/%s' % template)



class Print_Help(STLView):
    access = 'is_allowed_to_view'
    title = MSG(u"Impression du questionnaire")
    template = '/ui/scrib2009/help/print.xml'



class Print_Form(STLView):
    access = 'is_allowed_to_view'
    template = '/ui/scrib2009/help/template.xhtml'


    def get_namespace(self, resource, context):
        namespace = {}
        pages = resource.handler.pages
        body = []
        for page in [
                # Activités
                1, 2, 3, 4, 5, 6, 62, 63, 7, 8, 9, 14, 11,
                # Budget
                10, 13]:
            if page not in pages:
                continue
            table = resource.get_resource(PAGE_FILENAME % page)
            body.extend(BREAK_HEADER)
            body.extend(table.to_html(context, resource, page,
                skip_print=True))
            body.extend(BREAK_FOOTER)
        namespace['body'] = body
        root = context.root
        skin = root.get_skin()
        namespace['styles'] = skin.get_styles(context)
        context.response.set_header('Content-Type',
                                    'text/html; charset=UTF-8')
        return namespace
