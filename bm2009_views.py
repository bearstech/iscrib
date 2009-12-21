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
from itools.gettext import MSG
from itools.web import STLView

# Import from scrib
from form_views import Form_View, Send_View


class BMForm_View(Form_View):
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



class BMSend_View(Send_View):

    def action_send(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire BM est soumis.
        """
        raise NotImplementedError


    def action_export(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire BM est exporté.
        """
        raise NotImplementedError



class BMPrint_View(STLView):
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
