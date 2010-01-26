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
from itools.core import merge_dicts
from itools.datatypes import String, Integer, Boolean, Unicode
from itools.gettext import MSG
from itools.web import STLView, STLForm, INFO, ERROR

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.forms import TextWidget, BooleanRadio, MultilineWidget
from ikaaro.messages import MSG_NEW_RESOURCE
from ikaaro.registry import get_resource_class
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views_new import NewInstance

# Import from scrib
from form_views import Form_View
from utils import execute, get_adresse


class BM2009Form_View(Form_View):
    template = '/ui/scrib2009/Table_to_html.xml'
    page_template = '/ui/scrib2009/bm/Page%s.table.csv'


    def get_namespace(self, resource, context):
        namespace = Form_View.get_namespace(self, resource, context)
        namespace['code_ua'] = resource.get_code_ua()
        # TODO hardcoded
        menu = []
        code_ua = resource.get_code_ua()
        form = context.site_root.get_resource('bm/%s' % code_ua)
        for name, title in [('pageA', u"A-Identité"),
                            ('pageB', u"B-Bibliothèques du réseau"),
                            ('pageC', u"C-Accès et installations"),
                            ('pageD', u"D-Collections"),
                            ('pageE', u"E-Usages et usagers de la bib."),
                            ('pageF', u"F-Budget"),
                            ('pageG', u"G-Personnel et formation"),
                            ('pageH', u"H-Action culturelle"),
                            ('pageI', u"I-Commentaires")]:
            menu.append({'href': '%s/;%s' % (context.get_link(form), name),
                         'title': title,
                         'active': 'nav-active' if context.view_name == name
                                                else None})
        namespace['menu'] = menu
        return namespace


    def action(self, resource, context, form):
        Form_View.action(self, resource, context, form)
        resource.set_property('is_first_time', False)



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
        user = context.user
        namespace['is_admin'] = is_admin(user, resource)
        # Workflow - State
        namespace['statename'] = statename = resource.get_statename()
        namespace['form_state'] = resource.get_form_state()
        # Workflow - Transitions
        namespace['can_send'] = statename == 'private' and not errors
        namespace['can_export'] = not errors
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
        responsable_bm = context.site_root.get_property('responsable_bm')
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
        # D'abord les actions annulables (TODO factoriser avec action_send)
        if resource.get_workflow_state() == 'pending':
            wf_form = {'transition': 'accept', 'comments': u""}
            resource.edit_state.action(resource, context, wf_form)
            if isinstance(context.message, ERROR):
                context.commit = False
                return
            pageb = resource.get_pageb(make=True)
            pageb.edit_state.action(pageb, context, wf_form)
            if isinstance(context.message, ERROR):
                context.commit = False
                return

        # Export dans bm09
        year = context.site_root.get_year_suffix()
        table = "bm%s" % year
        query = ["delete from `%s` where `code_ua`=%s;" % (table,
                resource.get_code_ua()),
            resource.get_export_query(table)]
        try:
            execute("\n".join(query), context)
        except Exception:
            return

        # Export dans annexes09
        table = "annexes%s" % year
        query = ["delete from `%s` where `code_ua`=%s;" % (table,
                resource.get_code_ua())]
        pageb = resource.get_pageb()
        for form in pageb.get_resources():
            query.append(form.get_export_query(table, pages=['B'],
                exclude=[]))
        try:
            execute("\n".join(query), context)
        except Exception:
            return

        context.message = INFO(u"Le formulaire a été exporté.")



class BM2009Form_Print(STLView):
    access = 'is_allowed_to_view'
    title=MSG(u"Impression du rapport")
    template = '/ui/scrib2009/Table_to_print.xml'
    page_template = '/ui/scrib2009/bm/Page%s.table.csv'


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



class BM2009Form_Edit(DBResource_Edit):
    access = 'is_admin'
    schema = merge_dicts(DBResource_Edit.schema,
            code_ua=Integer(mandatory=True),
            departement=String(mandatory=True),
            is_first_time=Boolean(mandatory=True),
            content=String(mandatory=True))
    widgets = (DBResource_Edit.widgets
            + [TextWidget('code_ua', title=MSG(u"Code UA")),
                TextWidget('departement', title=MSG(u"Département")),
                BooleanRadio('is_first_time', title=MSG(u"Formulaire vide")),
                MultilineWidget('content', cols=100, rows=20,
                    title=MSG(u"Contenu brut /!\\ DANGEREUX /!\\ Toujours "
                        u"insérer une liste complète"))])


    def get_value(self, resource, context, name, datatype):
        if name == 'content':
            return resource.handler.to_str()
        return DBResource_Edit.get_value(self, resource, context, name, datatype)


    def action(self, resource, context, form):
        DBResource_Edit.action(self, resource, context, form)
        if not context.edit_conflict:
            resource.set_property('code_ua', form['code_ua'])
            resource.set_property('departement', form['departement'])
            resource.set_property('is_first_time', form['is_first_time'])
            resource.handler.load_state_from_string(form['content'])



class BM2009Form_New(NewInstance):
    schema = merge_dicts(NewInstance.schema, title=Unicode(mandatory=True),
            code_ua=Integer(mandatory=True),
            departement=Integer(mandatory=True))
    widgets = [TextWidget('title', title=MSG(u"Nom de la ville")),
            TextWidget('code_ua', title=MSG(u"Code UA")),
            TextWidget('departement', title=MSG(u"Département"))]


    def action(self, resource, context, form):
        cls = get_resource_class(context.query['type'])
        code_ua = form['code_ua']
        name = str(code_ua)
        app = context.site_root
        year = app.get_year_suffix()
        adresse = get_adresse(code_ua, 'adresse%s' % year, context=context)
        handler = cls.class_handler(A100=code_ua, **adresse)
        try:
            child = cls.make_resource(cls, resource, name,
                    body=handler.to_str(), code_ua=code_ua,
                    departement=str(form['departement']),
                    title={'fr': form['title']})
        except RuntimeError, e:
            if str(e).endswith('busy.'):
                context.message = ERROR(u"Code UA déjà pris")
                return
            raise
        return context.come_back(MSG_NEW_RESOURCE, goto='./%s/' % name)
