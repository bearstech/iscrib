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
from itools.datatypes import String
from itools.gettext import MSG
from itools.web import STLView, STLForm

# Import from scrib
from form_views import Form_View
from utils import parse_control


class BM2009Form_View(Form_View):
    template = '/ui/scrib2009/Table_to_html.xml'
    page_template = '/ui/scrib2009/Page%s.table.csv'


    def get_namespace(self, resource, context):
        namespace = Form_View.get_namespace(self, resource, context)
        # TODO hardcoded
        menu = []
        code_ua = resource.get_code_ua()
        form = resource.get_site_root().get_resource('bm/%s' % code_ua)
        for name, title in [('pageA', u"A-Identité"),
                            ('pageB', u"B-Bibliothèques du réseau"),
                            ('pageC', u"C-Accès et installations"),
                            ('pageD', u"D-Collections"),
                            ('pageE', u"E-Usages et usagers de la bib."),
                            ('pageF', u"F-Budget"),
                            ('pageG', u"G-Personnel et formation"),
                            ('pageH', u"H-Action culturelle")]:
            menu.append({'href': '%s/;%s' % (context.get_link(form), name),
                         'title': title,
                         'active': 'nav-active' if context.view_name == name
                                                else None})
        namespace['menu'] = menu
        return namespace



class BM2009Form_Send(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    template = '/ui/scrib2009/BM2009Form_send.xml'
    title = MSG(u"Contrôle de saisie")
    query_schema = {'view': String}


    def get_namespace(self, resource, context):
        namespace = {}
        namespace['first_time'] = first_time = resource.is_first_time()
        # Errors
        errors = []
        warnings = []
        handler = resource.handler
        controls = resource.handler.controls
        for number, title, expr, level, page in controls:
            expr = expr.strip()
            if not expr:
                continue
            if page == 'B':
                forms = list(resource.get_pageb().get_resources())
            else:
                forms = [resource]
            for form in forms:
                # Le contrôle contient des formules
                if '[' in title:
                    expanded = []
                    for is_expr, token in parse_control(title):
                        if not is_expr:
                            expanded.append(token)
                        else:
                            try:
                                value = eval(token, form.get_vars())
                            except ZeroDivisionError:
                                value = None
                            expanded.append(str(value))
                    title = ''.join(expanded)
                else:
                    try:
                        value = eval(expr, form.get_vars())
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
                        'href': '%s/;page%s' % (context.get_link(form),
                            page),
                        'debug': "'%s' = '%s'" % (str(expr), value)}
                if level == '2':
                    errors.append(info) 
                else:
                    warnings.append(info)
        namespace['controls'] = {'errors': errors,
                                 'warnings': warnings}
        namespace['is_ready'] = is_ready = resource.is_ready()
        # ACLs
        ac = resource.get_access_control()
        user = context.user
        namespace['is_admin'] = ac.is_admin(user, resource)
        # Workflow - State
        namespace['statename'] = resource.get_statename()
        namespace['form_state'] = resource.get_form_state()
        # Workflow - Transitions
        namespace['can_send'] = can_send = is_ready and not errors
        namespace['can_export'] = can_send
        # Debug
        namespace['debug'] = context.has_form_value('debug')
        # Print
        namespace['skip_print'] = False
        view = context.query['view']
        if view == 'printable' or user.is_voir_scrib():
            namespace['skip_print'] = True
        return namespace


    def action_send(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire BM est soumis.
        """
        raise NotImplementedError


    def action_export(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire BM est exporté.
        """
        raise NotImplementedError



class BM2009Form_Print(STLView):
    access = 'is_allowed_to_view'
    title=MSG(u"Impression du rapport")
    template = '/ui/scrib2009/Table_to_print.xml'
    page_template = '/ui/scrib2009/Page%s.table.csv'


    def get_namespace(self, resource, context):
        context.query['view'] = 'printable'
        context.bad_types = []
        forms = []
        for page in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'):
            table = resource.get_resource(self.page_template % page)
            if page == 'B':
                pageb = resource.get_pageb()
                for form in pageb.get_resources():
                    view = form.pageB
                    forms.append(table.get_namespace(form, view, context,
                        skip_print=True))
            else:
                view = getattr(resource, 'page%s' % page)
                forms.append(table.get_namespace(resource, view, context,
                    skip_print=True))
        namespace = {}
        namespace['forms'] = forms
        return namespace
