# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Hervé Cauwelier <herve@itaapy.com>
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
from itools.datatypes import String, DateTime
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.folder import Folder

# Import from iscrib
from controls import Controls
from param_views import Param_NewInstance, Param_View
from schema import Schema



class Param(Folder):
    class_id = 'Param'
    class_title = MSG(u"Collection Application")
    class_description = MSG(u"Create from an OpenDocument Spreadsheet file")
    class_icon16 = 'icons/16x16/tasks.png'
    class_icon48 = 'icons/48x48/tasks.png'
    class_schema = merge_dicts(Folder.class_schema,
            author=String(source='metadata', indexed=False, stored=True),
            ctime=DateTime(source='metadata', indexed=False, stored=True))
    
    schema_class = Schema
    controls_class = Controls
    default_form = '0'

    # Views
    new_instance = Param_NewInstance()
    view = Param_View()


    def get_form(self):
        return self.get_resource(self.default_form, soft=True)


    def get_param_folder(self):
        return self


    def get_catalog_values(self):
        author = (self.get_property('author')
                or self.get_property('last_author'))
        ctime = self.get_property('ctime') or self.get_property('mtime')
        return merge_dicts(Folder.get_catalog_values(self),
                author=author, ctime=ctime)
