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
from utils import SI, parse_control


#
# Print
#
PAGE_BREAK = list(HTMLParser('<div style="page-break-after: always"></div>'))
BREAK_HEADER = PAGE_BREAK[:1]
BREAK_FOOTER = PAGE_BREAK[1:]


# Messages
MSG_ERREUR_SAUVEGARDE = MSG(
        u"ATTENTION ! FICHE NON ENREGISTREE : "
        u"IL Y A DES RUBRIQUES MANQUANTES ET/OU INVALIDES")
MSG_SAUVEGARDE = MSG(
        u"La page est enregistrée, veuillez vérifier votre saisie dans : "
        u"Envoi du questionnaire")


class Page_Form(STLForm):
    access = 'is_allowed_to_view'


    def GET(self, resource, context):
        n = self.n
        view = context.get_form_value('view')
        table = resource.get_resource('/ui/scrib/Page%s.table' % n)
        user = context.user
        skip_print = (user.is_voir_scrib()) #or user.is_consultation())
        if view == 'printable':
            skip_print = True
        readonly = False
        statename = resource.get_statename()
        if statename == 'sent' and (user.is_bm() or user.is_bdp()):
            # 0005566
            # Si le formulaire est dans l'état terminé,
            # une bibliothèque ne peut plus le modifier
            readonly = True
        return table.to_html(context, resource, n, skip_print=skip_print,
                             readonly=readonly)


    def action(self, resource, context, form):
        user = context.user
        if user.is_voir_scrib(): #or user.is_consultation():
            from itools.http.exceptions import Forbidden
            raise Forbidden
        statename = resource.get_statename()
        ac = resource.get_access_control()
        is_admin = ac.is_admin(user, resource)
        if statename == 'exported' and is_admin is False:
            context.message = ERROR(u"Vous ne pouvez plus modifier le "
                                    u"questionnaire.")
            return
        # Save changes
        page_number = context.get_form_value('page_number')
        page_number = int(page_number)
        handler = resource.handler
        bad_type = []

        for key in handler.pages[page_number]:
            datatype = handler.schema[key]

            if context.has_form_value(key):
                value = context.get_form_value(key)
                value = value.strip()
                if datatype.somme:
                    expected_value = handler.somme(datatype, datatype.somme,
                            **context.request.get_form())
                    if value:
                        try:
                            value = datatype.encode(datatype.decode(value))
                        except ValueError:
                            # got it wrong!
                            bad_type.append(key)
                            continue
                        # sum inputed
                        if expected_value != 'NC' and value != expected_value:
                            # not what we get
                            if expected_value is not None:
                                # what we got was ok so blame the user
                                bad_type.append(key)
                                continue
                            # else, we got it wrong anyway
                    else:
                        # sum computed
                        if expected_value is not None:
                            # got it right!
                            value = expected_value
                        else:
                            # got it wrong!
                            bad_type.append(key)
                            continue
                elif datatype.is_mandatory and not value:
                    bad_type.append(key)
                    continue
                if datatype.is_valid(value, datatype.repr):
                    value = datatype.decode(value)
                else:
                    bad_type.append(key)
                    continue
            elif isinstance(datatype, Boolean):
                value = False
            else:
                continue

            handler._set_value(key, value)
            # Reindex
            context.server.change_resource(resource)

        # But drop previous parameters
        if bad_type:
            context.request.get_form()['bad_type'] = bad_type
            context.message = ERROR(MSG_ERREUR_SAUVEGARDE)
        else:
            context.message = INFO(MSG_SAUVEGARDE)

        if resource.get_statename() == 'empty':
            if is_admin is False:
                # Will notify the object changed
                # only if the user is not an admin
                resource.do_trans('start')



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
        view = context.get_form_value('view')
        namespace = {}

        # Workflow - State
        state = resource.get_state()
        namespace['state'] = state['title']

        # Controls
        vars = {}
        vars['SI'] = SI
        for key in resource.handler.schema:
            vars[key] = resource.handler._get_value(key)

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
