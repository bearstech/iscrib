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
from itools.datatypes import Integer, Unicode, Boolean

# Import from ikaaro
from ikaaro.user import User
from ikaaro.registry import register_field, register_resource_class

# Import from scrib
from user_views import User_Home
from utils import get_bdp, get_bm


class ScribUser(User):

    class_version = '20080410'
    class_views = ['home', 'edit_password']

    home = User_Home()

    def _get_catalog_values(self):
        values = User._get_catalog_values(self)
        values['user_town'] = self.get_user_town()
        values['dep'] = self.get_department()
        values['year'] = self.get_year()
        values['stored_BDP'] = self.is_BDP()
        values['stored_BM'] = self.is_BM()
        return values


    def is_BM(self):
        """ patern is BMxxx"""
        return self.name.startswith('BM')


    def is_BDP(self):
        """ patern is BDPxx"""
        return self.name.startswith('BDP')


    def is_not_BDP_or_BM(self):
        return not self.is_BDP() and not self.is_BM()


    def get_department_name(self):
        name = self.name
        dep = self.get_department()
        dep_name = get_bdp(dep)
        if dep_name:
            dep_name = dep_name.get_value('name')
        return dep_name


    def get_department(self):
        name = self.name
        dep = ''
        if self.is_BDP():
           dep = name.split('BDP')[-1].upper()
        elif self.is_BM():
            code = self.get_BM_code()
            if code:
                # Cf. #2617
                bib = get_bm(code)
                if bib:
                    dep = bib.get_value('dep')
                else:
                    print "bib", code, "n'existe pas"
        return dep


    def get_BM_code(self):
        """ patern is BMxxx"""
        name = self.name
        if self.is_BM():
           return name.split('BM')[-1]
        else:
            return None


    def get_user_town(self):
        title = ''
        if self.is_BM():
            code = self.get_BM_code()
            if code:
                # Cf. #2617
                bib = get_bm(code)
                if bib:
                    title = bib.get_value('name')
                else:
                    print "bib", code, "n'existe pas"
        return title


    def get_year(self):
        name = self.name
        if self.is_BDP():
           # XXX just for 2008 ;)
           return 2008
        elif self.is_BM():
           return 2008
        return None


    #########################################################################
    # Upgrade
    #########################################################################
    def update_20080407(self):
        """bibUser obsolète.
        """
        self.metadata.format = "user"
        self.metadata.set_changed()


    def update_20080410(self):
        """username pour compatibilité arrière.
        """
        self.set_property('username', self.name)



register_resource_class(ScribUser)
# TODO remove after migration
register_resource_class(ScribUser, format="bibUser")


register_field('user_town', Unicode(is_indexed=True))
register_field('dep', Unicode(is_indexed=True, is_stored=True))
register_field('year', Integer(is_indexed=True))
register_field('stored_BDP', Boolean(is_stored=True))
register_field('stored_BM', Boolean(is_stored=True))
