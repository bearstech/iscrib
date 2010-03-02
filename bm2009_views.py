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
from itools.web import INFO, ERROR

# Import from scrib
from base2009_views import Base2009Form_View, Base2009Form_Send
from utils import execute


class BM2009Form_View(Base2009Form_View):
    page_template = '/ui/scrib2009/bm/Page%s.table.csv'


    def get_scrib_menu(self, resource, context):
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
        return menu



class BM2009Form_Send(Base2009Form_Send):

    def get_namespace(self, resource, context):
        namespace = Base2009Form_Send.get_namespace(self, resource, context)
        errors = namespace['controls']['errors']
        warnings = namespace['controls']['warnings']
        pageb = resource.get_pageb()
        for form in pageb.get_resources():
            title = form.get_title()
            # Invalid fields
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
            for control in form.get_failed_controls():
                control['href'] = '%s/;page%s#field_%s' % (
                        context.get_link(form), control['page'],
                        control['title'].split()[0])
                if control['level'] == '2':
                    errors.append(control)
                else:
                    warnings.append(control)
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
