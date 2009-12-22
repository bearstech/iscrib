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
from itools.datatypes import String
from itools.gettext import MSG
from itools.web import STLView, STLForm, INFO, ERROR

# Import from scrib
from form_views import Form_View


class BM2009Form_View(Form_View):
    template = '/ui/scrib2009/Table_to_html.xml'
    page_template = '/ui/scrib2009/Page%s.table.csv'


    def get_namespace(self, resource, context):
        namespace = Form_View.get_namespace(self, resource, context)
        namespace['code_ua'] = resource.get_code_ua()
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
        # Invalid fields
        for name, datatype in resource.get_invalid_fields():
            info = {'number': name,
                    'title': u"Champ %s non valide" % name,
                    'href': ';page%s#field_%s' % (datatype.pages[0], name),
                    'debug': str(type(datatype))}
            if datatype.is_mandatory:
                errors.append(info)
            else:
                warnings.append(info)
        pageb = resource.get_pageb()
        for form in pageb.get_resources():
            title = form.get_title()
            for name, datatype in form.get_invalid_fields():
                info = {'number': name,
                        'title': (u"Bibliothèque %s : "
                            u"champ %s non valide" % (title, name)),
                        'href': '%s/;page%s#field_%s' % (
                            context.get_link(form), datatype.pages[0], name),
                        'debug': str(type(datatype))}
                if datatype.is_mandatory:
                    errors.append(info)
                else:
                    warnings.append(info)
        # Failed controls
        for control in resource.get_failed_controls():
            control['href'] = ';page%s#field_%s' % (control['page'],
                    control['title'].split()[0])
            if control['level'] == '2':
                errors.append(control)
            else:
                warnings.append(control)
        for form in pageb.get_resources():
            title = form.get_title()
            for control in form.get_failed_controls():
                control['title'] = u"Bibliothèque %s : %s" % (title,
                        control['title'])
                control['href'] = '%s/;page%s#field_%s' % (
                        context.get_link(form), control['page'],
                        control['title'].split()[0])
                if control['level'] == '2':
                    errors.append(control)
                else:
                    warnings.append(control)
        namespace['controls'] = {'errors': errors,
                                 'warnings': warnings}
        # ACLs
        ac = resource.get_access_control()
        user = context.user
        namespace['is_admin'] = ac.is_admin(user, resource)
        # Workflow - State
        namespace['statename'] = resource.get_statename()
        namespace['form_state'] = resource.get_form_state()
        # Workflow - Transitions
        namespace['can_send'] = can_send = not errors
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
        # D'abord les actions annulables
        wf_form = {'transition': 'request', 'comments': u""}
        resource.edit_state.action(resource, context, wf_form)
        if isinstance(context.message, ERROR):
            context.commit = False
            return
        pageb = resource.get_pageb(make=True)
        pageb.edit_state.action(pageb, context, wf_form)
        if isinstance(context.message, ERROR):
            context.commit = False
            return

        # Envoi mail responsable
        app = resource.get_site_root()
        responsable_bm = app.get_property('responsable_bm')
        to_addr = responsable_bm
        code_ua = resource.get_property('code_ua')
        departement = resource.get_property('departement')
        subject = u'SCRIB-BM : %s (%s)' % (code_ua, departement)
        text = (u"La Bibliothèque %s (%s), du département %s, a terminé son "
                u"formulaire." % (code_ua, resource.get_title(),
                    departement))
        root = context.root
        root.send_email(to_addr, subject, text=text)

        # Envoi accusé réception
        user = context.user
        to_addr = (user.get_title(), user.get_property('email'))
        subject = u"Accusé de réception DLL"
        text = (u"Votre rapport annuel a bien été reçu par votre "
                u"correspondant à la DLL.\n\nNous vous remercions de votre "
                u"envoi.\n\nCordialement.")
        root.send_email(to_addr, subject, from_addr=responsable_bm,
                text=text, return_receipt=True)

        context.message = INFO(u"Terminé, un mél est envoyé à votre "
                u"correspondant DLL.")


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
