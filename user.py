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
from itools.datatypes import Integer, Unicode, String

# Import from ikaaro
from ikaaro.user import User as BaseUser
from ikaaro.registry import register_field, register_resource_class

# Import from scrib
from user_views import User_Home
#from utils import get_bdp, get_bm


class User(BaseUser):
    """Ici des méthodes communes à tous les utilisateurs, quelque soit leur
    application, pour simplifier la gestion des droits. Surtout pour l'admin
    qui est indépendant de toute application.
    """

    ######################################################################
    # Scrib API
    def is_bm(self):
        """ patern is BMxxx"""
        return self.get_property('username').startswith('BM')


    def is_bdp(self):
        """ patern is BDPxx"""
        return self.get_property('username').startswith('BDP')


    def is_voir_scrib(self):
        return self.get_property('username') == 'VoirSCRIB'



class ScribUser2009(User):
    """Les utilisateurs spécifiques à Scrib.
    """
    class_id = 'ScribUser2009'
    class_views = ['home', 'edit_password']

    # Views
    home = User_Home()


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(User.get_metadata_schema(),
                           title=Unicode,
                           code_ua=Integer,
                           departement=String,
                           id=String)


    #def _get_catalog_values(self):
    #    values = User._get_catalog_values(self)
    #    values['user_town'] = self.get_user_town()
    #    values['departement'] = self.get_property('departement')
    #    values['is_bdp'] = self.is_bdp()
    #    values['is_bm'] = self.is_bm()
    #    return values


    ######################################################################
    # Scrib API
    def get_user_town(self):
        title = u""
        if self.is_bm():
            code_ua = self.get_property('code_ua')
            if code_ua:
                # Cf. #2617
                bib = get_bm(code_ua)
                if bib:
                    title = bib.get_value('name')
                else:
                    print "bib", code_ua, "n'existe pas"
        return title


    def get_department_name(self):
        dep = self.get_property('department')
        dep_name = get_bdp(dep)
        if dep_name:
            dep_name = dep_name.get_value('name')
        return dep_name



###########################################################################
# Register
register_resource_class(User)
register_resource_class(ScribUser2009)
#register_field('user_town', Unicode(is_indexed=True))
