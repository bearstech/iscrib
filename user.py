# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Integer, Unicode, Boolean, String

# Import from ikaaro
from ikaaro.user import User
from ikaaro.registry import register_field, register_resource_class

# Import from scrib
from user_views import User_Home
#from utils import get_bdp, get_bm


class ScribUser2009(User):
    class_id = 'ScribUser2009'
    class_views = ['home', 'edit_password']

    # Views
    home = User_Home()


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(User.get_metadata_schema(),
                           title=Unicode,
                           code=Integer,
                           departement=String,
                           id=String)


    #def _get_catalog_values(self):
    #    values = User._get_catalog_values(self)
    #    values['user_town'] = self.get_user_town()
    #    values['departement'] = self.get_property('departement')
    #    values['is_BDP'] = self.is_BDP()
    #    values['is_BM'] = self.is_BM()
    #    return values


    ######################################################################
    # Scrib API
    def is_BM(self):
        """ patern is BMxxx"""
        return self.get_property('username').startswith('BM')


    def is_BDP(self):
        """ patern is BDPxx"""
        return self.get_property('username').startswith('BDP')


    def is_VoirSCRIB(self):
        return self.get_property('username') == 'VoirSCRIB'


    def is_not_BDP_nor_BM(self):
        return not self.is_BDP() and not self.is_BM()


    def get_user_town(self):
        title = u""
        if self.is_BM():
            code = self.get_property('code')
            if code:
                # Cf. #2617
                bib = get_bm(code)
                if bib:
                    title = bib.get_value('name')
                else:
                    print "bib", code, "n'existe pas"
        return title


    def get_department_name(self):
        dep = self.get_property('department')
        dep_name = get_bdp(dep)
        if dep_name:
            dep_name = dep_name.get_value('name')
        return dep_name



###########################################################################
# Register
register_resource_class(ScribUser2009)
#register_field('user_town', Unicode(is_indexed=True))
