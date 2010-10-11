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
from ikaaro.autoform import RTEWidget
from ikaaro.autoform import XHTMLBody
from ikaaro.registry import register_document_type
from ikaaro.website import WebSite

# Import from iscrib
from application_views import Application_BrowseContent
from param import Param
from utils_views import AutomaticEditView


class Application(WebSite):
    class_id = 'Application'
    class_title = MSG(u"Application client iScrib")
    class_views = ['view', 'edit', 'control_panel']
    # Rôle par défaut members au lieu de guests
    class_roles = WebSite.class_roles[1:]
    class_schema = merge_dicts(WebSite.class_schema,
            homepage=XHTMLBody(source='metadata', multilingual=True,
                parameters_schema = {'lang': String}))

    edit_schema = {'homepage': XHTMLBody(multilingual=True)}
    edit_widgets = [RTEWidget('homepage', title=MSG(u'Homepage'))]

    # Views
    view = Application_BrowseContent(access='is_allowed_to_edit',
            title=MSG(u"Welcome to iScrib"))
    edit = AutomaticEditView(access='is_admin')


    def init_resource(self, **kw):
        WebSite.init_resource(self, **kw)
        value = self.class_schema['homepage'].decode("""
              <h2>Welcome to your iScrib Application!</h2>
              <p>This is where you post your form and people will answer
                  it.</p>
              <p>Things you can do:</p>
              <ul>
                <li><a href="theme/;edit">Set your logo in the top
                    banner;</a></li>
                <li><a
                    href="http://iscrib.demo.itaapy.com/gabarit/;download">Download
                    the ODS template;</a></li>
                <li><a href=";new_resource?type=Param">Create a data
                    collection application.</a></li>
                <!--
                <li><a href=";xxx">Send an invitation to users;</a></li>
                <li><a href=";xxx">Follow the filling of the form by the users.</a></li>
                -->
              </ul>""")
        self.set_property('homepage', value, language='en')
        theme = self.get_resource('theme')
        # Laisse voir le nom du website
        theme.set_property('logo', None)


    def get_document_types(self):
        return [Param]



register_document_type(Application, WebSite.class_id)
