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
from ikaaro.user import User
from ikaaro.registry import register_resource_class

# Import from scrib
from user_views import User_Home, ScribUser_EditAccount


class ScribUser(User):
    """Les méthodes sont communes à tous les utilisateurs, quelque soit leur
    application, pour simplifier la gestion des droits.
    """
    class_views = ['home', 'edit_password', 'edit_account']

    # Views
    home = User_Home() # Si besoin déplacer dans la BM/BDP
    edit_account = ScribUser_EditAccount(access='is_admin')
    edit = None


    @classmethod
    def get_metadata_schema(cls):
        return merge_dicts(User.get_metadata_schema(),
                title=Unicode,
                code_ua=Integer,
                departement=String)


    def _get_catalog_values(self):
        return merge_dicts(User._get_catalog_values(self),
                code_ua=self.get_property('code_ua'),
                departement=self.get_property('departement'))


    # Affiche le nom de la ville, pas l'identifiant
    def get_title(self, language=None):
        return self.get_property('title', language=language)


    ######################################################################
    # Scrib API
    def is_bm(self):
        """ patern is BMxxx"""
        username = self.get_property('username')
        return username and username.startswith('BM')


    def is_bdp(self):
        """ patern is BDPxx"""
        username = self.get_property('username')
        return username and username.startswith('BDP')


    def is_voir_scrib(self):
        username = self.get_property('username')
        return username and username == 'VoirSCRIB'



###########################################################################
# Register
register_resource_class(ScribUser)
