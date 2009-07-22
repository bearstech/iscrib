# -*- coding: UTF-8 -*-
# Copyright (C) 2006, 2008 Hervé Cauwelier <herve@itaapy.com>
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
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.folder import Folder

# Import from scrib
from forms_views import Forms_SearchForm


class Forms(Folder):

    class_id = 'Forms'
    class_title = MSG(u'Forms')
    class_description = MSG(u'...')
    class_icon48 = 'scrib/images/form48.png'
    class_views = ['search_form']

    search_form = Forms_SearchForm()

    #########################################################################
    # API
    #########################################################################
    def is_BM(self):
        return self.name.startswith('BM')


    def is_BDP(self):
        return self.name.startswith('BDP')


    def get_year(self):
        return int(self.name[-4:])



register_resource_class(Forms)
