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
from itools.web import STLView, STLForm, INFO, ERROR

# Import from scrib
from form import SENT, EXPORTED
from utils import SI, parse_control


#
# Print
#
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


class Page_Form(STLForm):
    access = 'is_allowed_to_view'
    schema = {'page_number': String}
    query_schema = {'view': String}


    def GET(self, resource, context):
        try:
            bad_types = context.bad_types
        except AttributeError:
            bad_types = []
        print "bad_types", bad_types
        view = context.query['view']
        table = resource.get_resource('/ui/scrib/Page%s.table' % self.n)
        user = context.user
        skip_print = (user.is_voir_scrib()) #or user.is_consultation())
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
        user = context.user
        if user.is_voir_scrib(): #or user.is_consultation():
            from itools.http.exceptions import Forbidden
            raise Forbidden
        statename = resource.get_statename()
        ac = resource.get_access_control()
        is_admin = ac.is_admin(user, resource)
        if statename == EXPORTED and is_admin is False:
            context.message = ERROR(u"Vous ne pouvez plus modifier le "
                    u"questionnaire.")
            return
        # Save changes
        page_number = form['page_number']
        handler = resource.handler
        bad_types = []
        for key in handler.pages[page_number]:
            # Can't use "if not/continue" pattern here
            if context.has_form_value(key):
                # Do not use form schema, only default String
                value = context.get_form_value(key).strip()
                datatype = handler.schema[key]
                if datatype.somme:
                    expected_value = handler.somme(datatype, datatype.somme,
                            **form)
                    if value:
                        try:
                            value = datatype.encode(datatype.decode(value))
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
                elif datatype.is_mandatory and not value:
                    bad_types.append(key)
                    continue
                if datatype.is_valid(value, datatype.repr):
                    value = datatype.decode(value)
                else:
                    bad_types.append(key)
                    continue
            elif isinstance(datatype, Boolean):
                # Default value for missing bool
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



class Help_Page(STLView):
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
        return self.get_resource('/ui/scrib/help/%s' % template)



class Print_Help(STLView):
    access = 'is_allowed_to_view'
    title = MSG(u"Impression du questionnaire")
    template = '/ui/scrib/help/print.xml'



class Print_Form(STLView):
    access = 'is_allowed_to_view'
    template = '/ui/scrib/help/template.xhtml'


    def get_namespace(self, resource, context):
        namespace = {}

        body = []
        for page in [
                # Activités
                1, 2, 3, 4, 5, 6, 62, 63, 7, 8, 9, 14, 11,
                # Budget
                10, 13]:
            if page not in resource.handler.pages:
                continue
            table = resource.get_resource('/ui/scrib/Page%s.table' % page)
            body.extend(BREAK_HEADER)
            body.extend(table.to_html(context, resource, page, skip_print=True))
            body.extend(BREAK_FOOTER)

        namespace['body'] = body

        root = context.root
        skin = root.get_skin()
        namespace['styles'] = skin.get_styles(context)

        context.response.set_header('Content-Type', 'text/html; charset=UTF-8')
        return namespace



class Controls(STLForm):
    access = 'is_allowed_to_view'
    title = MSG(u"Envoi du questionnaire")
    template = '/ui/scrib/Form_controls.xml'


    def get_namespace(self, resource, context):
        user = context.user
        view = context.query['view']
        namespace = {}
        # Workflow - State
        state = resource.get_state()
        namespace['state'] = state['title']
        # Controls
        vars = {}
        vars['SI'] = SI
        for key in resource.handler.schema:
            vars[key] = resource.handler.get_value(key)
        # Errors
        errors = []
        warnings = []

        controls = resource.handler.controles
        for k, title, expr, level, page in controls:
            expr = expr.strip()
            if expr:
                try:
                    value = eval(expr, dict(vars))
                except ZeroDivisionError:
                    value = None
                if value is True:
                    continue
                info = {}
                info['number'] = k
                if '[' in title:
                    # Le contrôle contient des formules
                    expanded = []
                    for is_expr, token in parse_control(title):
                        if not is_expr:
                            expanded.append(token)
                        else:
                            try:
                                value = eval(token, dict(vars))
                            except ZeroDivisionError:
                                value = None
                            expanded.append(str(value))
                    title = ''.join(expanded)
                info['title'] = title
                info['page'] = page.replace('-', '')
                #info['debug'] = "%s %s" % (str(expr), value)
                if level == "2":
                    errors.append(info)
                else:
                    warnings.append(info)

        namespace['controls'] = {}
        namespace['controls']['errors'] = errors
        namespace['controls']['warnings'] = warnings

        # ACLs
        ac = resource.get_access_control()
        is_admin = ac.is_admin(user, resource)

        # Workflow - Transitions
        transitions = []
        for name, transition in state.transitions.items():
            access = transition['access']
            # Cache l'export à l'utilisateur
            if access == 'can_export' and not is_admin:
                continue
            can_send = (access == 'can_send' and not errors)
            can_export = (access == 'can_export' and is_admin and not errors)
            access = (access is True or can_send or can_export)
            transitions.append(
                {'name': name,
                 'title': transition['description'],
                 'access': access,
                 'can_send': can_send,
                 'can_export': can_export,
                 'disabled': not access})
        namespace['transitions'] = transitions

        namespace['skip_print'] = False
        if view == 'printable' or (user.is_voir_pelleas() or
                                   user.is_consultation()):
            namespace['skip_print'] = True

        namespace['help_onclick'] = """window.open(';help_page?page=controls',\
            'xxx', 'toolbar=no, location=no, status=no, menubar=no,\
            scrollbars=yes, width=440, height=540');\
            return false"""

        return namespace
