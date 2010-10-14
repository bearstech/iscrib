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
from itools.datatypes import String
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.autoform import XHTMLBody, RTEWidget
from ikaaro.root import Root as BaseRoot

# Import from iscrib
from application import Application
from base_views import AutomaticEditView, FrontView
from root_views import Root_View


class Root(BaseRoot):
    class_id = 'iScrib'
    class_schema = merge_dicts(BaseRoot.class_schema,
            homepage=XHTMLBody(source='metadata', multilingual=True,
                parameters_schema = {'lang': String}))
    class_views = BaseRoot.class_views + ['show']
    class_skin = 'ui/iscrib'

    edit_schema = {'homepage': XHTMLBody(multilingual=True)}
    edit_widgets = [RTEWidget('homepage', title=MSG(u'Homepage'))]

    # Views
    view = Root_View()
    edit = AutomaticEditView()
    show = FrontView(title=MSG(u"Show Workgroup(s)"), cls=Application)


    def init_resource(self, email, password, admins=('0',)):
        super(Root, self).init_resource(email, password, admins=admins)
        value = self.class_schema['homepage'].decode("""
                <h2>Welcome to iScrib!</h2>""")
        self.set_property('homepage', value, language='en')
        theme = self.get_resource('theme')
        # Laisse voir le nom du website
        theme.set_property('logo', None)


    def get_document_types(self):
        return super(Root, self).get_document_types() + [Application]
