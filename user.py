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
from itools.stl import stl
from itools.catalog import KeywordField, TextField, BoolField

# Import from ikaaro
from ikaaro.users import User
from ikaaro.registry import register_object_class

# Import from scrib
from utils import get_bdp, get_bm



class ScribUser(User):
    class_version = '20080410'
    class_views = [['home'], ['edit_password_form']]

    def get_catalog_fields(self):
        fields = User.get_catalog_fields(self)
        fields += [TextField('user_town'),
                   KeywordField('dep', is_stored=True),
                   KeywordField('year'),
                   BoolField('is_BDP', is_stored=True),
                   BoolField('is_BM', is_stored=True)]
        return fields


    def get_catalog_values(self):
        values = User.get_catalog_values(self)
        values['user_town'] = self.get_user_town()
        values['dep'] = self.get_department()
        values['year'] = self.get_year()
        values['is_BDP'] = self.is_BDP()
        values['is_BM'] = self.is_BM()
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
           dep = name.split('BDP')[-1]
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
           # XXX just for 2005 ;)
           return '2006'
        elif self.is_BM():
           return '2006'
        return None


    #######################################################################
    # Security
    #######################################################################
    def is_self(self, user, object):
        if user is None:
            return False
        return self.name == user.name


    #######################################################################
    # Home
    home__access__ = 'is_self'
    home__label__ = u'Home'
    def home(self, context):
        namespace = {}
        root = self.get_root()
        name = self.name
        department, code = '', ''

        year = self.get_year()
        if self.is_BM():
            code = self.get_BM_code()
            report = root.get_object('BM%s/%s' % (year, code))
        elif self.is_BDP():
            department = self.get_department()
            report = root.get_object('BDP%s/%s' % (year, department))
        else:
            report = None

        if report is not None:
            namespace['report_url'] = '%s/;%s' % (self.get_pathto(report),
                                                  report.get_firstview())
        else:
            namespace['report_url'] = None

        # The year
        namespace['year'] = year
        # The department or the BM Code
        namespace['dep'] = ''
        if department:
            bib = get_bdp(department)
            if bib:
                namespace['dep'] = bib.get_value('name')
        elif code:
            bib = get_bm(code)
            if bib:
                namespace['dep'] = bib.get_value('name')

        template = self.get_object('/ui/scrib/User_home.xml')
        return stl(template, namespace)


    #######################################################################
    # Password
    edit_password_form__label__ = u'Change password'


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



register_object_class(ScribUser)
# TODO remove after migration
register_object_class(ScribUser, format="bibUser")
