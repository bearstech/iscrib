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
from ikaaro.registry import register_resource_class

# Import from scrib
from user_views import User_Home


class User(BaseUser):
    """Les méthodes sont communes à tous les utilisateurs, quelque soit leur
    application, pour simplifier la gestion des droits.
    """
    class_views = ['home', 'edit_password']

    # Views
    home = User_Home() # Si besoin déplacer dans la BM/BDP


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(User.get_metadata_schema(),
                           title=Unicode,
                           code_ua=Integer,
                           departement=String,
                           id=String)


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



###########################################################################
# Register
register_resource_class(User)
