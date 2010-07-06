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
from itools.web import STLView, INFO, ERROR

# Import from scrib
from base2009_views import Base2009Form_View, Base2009Form_Send
from utils import execute


class BDP2009Form_View(Base2009Form_View):
    hidden_fields = ['0']



class BDP2009Form_Send(Base2009Form_Send):

    def action_send(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire BDP est soumis.
        """
        # D'abord les actions annulables
        wf_form = {'transition': 'request', 'comments': u""}
        resource.edit_state.action(resource, context, wf_form)
        if isinstance(context.message, ERROR):
            context.commit = False
            return

        # Envoi mail responsable
        responsable_bdp = context.site_root.get_property('responsable_bdp')
        to_addr = responsable_bdp
        code_ua = resource.get_property('code_ua')
        departement = resource.get_property('departement')
        subject = u'SCRIB-BDP : %s (%s)' % (code_ua, departement)
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
        root.send_email(to_addr, subject, from_addr=responsable_bdp,
                text=text, return_receipt=True)

        context.message = INFO(u"Terminé, un mél est envoyé à votre "
                u"correspondant DLL.")


    def action_export(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire BDP est exporté.
        """
        # D'abord les actions annulables (TODO factoriser avec action_send)
        if resource.get_workflow_state() == 'pending':
            wf_form = {'transition': 'accept', 'comments': u""}
            resource.edit_state.action(resource, context, wf_form)
            if isinstance(context.message, ERROR):
                context.commit = False
                return

        # Export dans bdp09
        year = context.site_root.get_year_suffix()
        table = "bdp%s" % year
        query = ["delete from `%s` where `code_ua`=%s;" % (table,
                resource.get_code_ua()),
            resource.get_export_query(table)]
        try:
            execute("\n".join(query), context)
        except Exception:
            return

        context.message = INFO(u"Le formulaire a été exporté.")



class BDP2009Form_Print(STLView):
    access = 'is_allowed_to_view'
    title=MSG(u"Impression du rapport")
    template = '/ui/scrib2009/Table_to_print.xml'
    pages = []


    def get_namespace(self, resource, context):
        context.query['view'] = 'printable'
        context.bad_types = []
        forms = []
        for pagenum in ('0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                'L'):
            formpage = resource.get_formpage(pagenum)
            view = getattr(resource, 'page%s' % pagenum)
            forms.append(formpage.get_namespace(resource, view, context,
                skip_print=True))
        namespace = {}
        namespace['forms'] = forms
        return namespace
