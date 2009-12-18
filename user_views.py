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
from datatypes import Departements


class User_Home(STLView):
    access = 'is_self_or_admin'
    title  = MSG(u"Profil")
    template = '/ui/scrib2009/User_home.xml'


    def get_namespace(self, resource, context):
        namespace = {}
        app = resource.get_site_root()
        departement = resource.get_property('departement')
        if resource.is_bm():
            code_ua = resource.get_property('code_ua')
            form = app.get_resource('bm/%s' % code_ua)
        elif resource.is_bdp():
            form = app.get_resource('bdp/%s' % departement)
        else:
            form = None
        if form is not None:
            namespace['form_url'] = '%s/;aide' % resource.get_pathto(form)
        else:
            namespace['form_url'] = None
        namespace['application'] = app.get_title()
        namespace['departement'] = Departements.get_value(departement)
        namespace['email'] = resource.get_property('email')
        namespace['username'] = resource.get_property('username')
        return namespace
