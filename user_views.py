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
from itools.datatypes import Integer
from itools.gettext import MSG
from itools.web import STLView, ERROR

# Import from ikaaro
from ikaaro.forms import TextWidget, SelectWidget
from ikaaro.user_views import User_EditAccount

# Import from scrib
from datatypes import Departements


class User_Home(STLView):
    access = 'is_self_or_admin'
    title  = MSG(u"Profil")
    template = '/ui/scrib2009/User_home.xml'


    def get_namespace(self, resource, context):
        namespace = {}
        app = context.site_root
        code_ua = resource.get_property('code_ua')
        if resource.is_bm():
            form = app.get_resource('bm/%s' % code_ua)
        elif resource.is_bdp():
            form = app.get_resource('bdp/%s' % code_ua)
        else:
            form = None
        if form is not None:
            namespace['form_url'] = '%s/;aide' % resource.get_pathto(form)
        else:
            namespace['form_url'] = None
        namespace['application'] = app.get_title()
        departement = resource.get_property('departement')
        namespace['departement'] = Departements.get_value(departement)
        namespace['email'] = resource.get_property('email')
        namespace['username'] = resource.get_property('username')
        return namespace



class ScribUser_EditAccount(User_EditAccount):
    schema = merge_dicts(User_EditAccount.schema, code_ua=Integer,
            departement=Departements)
    widgets = User_EditAccount.widgets + [
            TextWidget('code_ua', title=MSG(u"Code UA")),
            SelectWidget('departement', title=MSG(u"Département"))]


    def action(self, resource, context, form):
        User_EditAccount.action(self, resource, context, form)
        if type(context.message) is ERROR:
            return
        root = context.root
        code_ua = form['code_ua']
        results = root.search(format=resource.class_id,
                code_ua=code_ua)
        if len(results):
            brain = results.get_documents()[0]
            if brain.name != resource.name:
                context.commit = False
                context.message = ERROR(u"Code UA déjà réservé par "
                        u"l'utilisateur {name}", name=brain.name)
            return
        bm = context.site_root.get_resource('bm/%s' % code_ua, soft=True)
        if bm is None:
            context.commit = False
            context.message = ERROR(u"Aucun formulaire ne porte ce code UA.")
        resource.set_property('code_ua', code_ua)
        resource.set_property('departement', form['departement'])
