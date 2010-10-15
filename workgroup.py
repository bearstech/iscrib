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
from ikaaro.access import is_admin
from ikaaro.autoform import XHTMLBody, RTEWidget
from ikaaro.control_panel import ControlPanel
from ikaaro.website import WebSite

# Import from iscrib
from application import Application
from base_views import AutomaticEditView, FrontView, LoginView
from form import Form
from workflow import SENT, EXPORTED, MODIFIED
from workgroup_views import Workgroup_NewInstance, Workgroup_BrowseContent


class Workgroup(WebSite):
    class_id = 'Workgroup'
    class_title = MSG(u"iScrib Workgroup")
    class_description = MSG(u"Private workgroup with logo, users and "
            u"collection applications")
    class_views = WebSite.class_views + ['show']
    class_schema = merge_dicts(WebSite.class_schema,
            homepage=XHTMLBody(source='metadata', multilingual=True,
                parameters_schema = {'lang': String}))
    class_skin = 'ui/iscrib'

    edit_schema = {'homepage': XHTMLBody(multilingual=True)}
    edit_widgets = [RTEWidget('homepage', title=MSG(u'Homepage'))]

    # Views
    new_instance = Workgroup_NewInstance()
    view = Workgroup_BrowseContent()
    edit = AutomaticEditView()
    show = FrontView(title=MSG(u"Show Application(s)"), cls=Application)
    # Security
    control_panel = ControlPanel(access='is_admin')
    unauthorized = LoginView()


    def init_resource(self, **kw):
        super(Workgroup, self).init_resource(**kw)
        value = self.class_schema['homepage'].decode("""
              <h2>Welcome to your iScrib Workgroup!</h2>
              <p>This is where you create collection applications.</p>
              <p>Things you can do:</p>
              <ul>
                <li><a
                    href="http://iscrib.demo.itaapy.com/gabarit/;download">Download
                    the ODS template</a>;</li>
                <li><a href=";new_resource?type=Application">Create a data
                    collection application</a>;</li>
                <li><a href="theme/;edit">Upload your logo</a>.</li>
              </ul>""")
        self.set_property('homepage', value, language='en')
        theme = self.get_resource('theme')
        # Laisse voir le nom du website
        theme.set_property('logo', None)


    def get_document_types(self):
        return super(Workgroup, self).get_document_types() + [Application]


    def is_allowed_to_add_form(self, user, resource):
        return is_admin(user, resource)


    def is_allowed_to_view(self, user, resource):
        if user is None:
            return False
        if is_admin(user, resource):
            return True
        role = self.get_user_role(user.name)
        if isinstance(resource, Application):
            if role in ('members', 'reviewers'):
                return True
            return resource.show.get_form_name(user, resource) is not None
        elif isinstance(resource, Form):
            return (role in ('members', 'reviewers')
                    or user.name == resource.name)
        return super(Workgroup, self).is_allowed_to_view(user, resource)


    def is_allowed_to_edit(self, user, resource):
        if user is None:
            return False
        if is_admin(user, resource):
            return True
        role = self.get_user_role(user.name)
        if isinstance(resource, (Workgroup, Application)):
            return role in ('members', 'reviewers')
        elif isinstance(resource, Form):
            if resource.name == resource.parent.default_form:
                return role in ('members', 'reviewers')
            return resource.name == user.name
        return super(Workgroup, self).is_allowed_to_edit(user, resource)


    def is_allowed_to_export(self, user, resource):
        if user is None:
            return False
        if is_admin(user, resource):
            return True
        state = resource.get_workflow_state()
        if state not in (SENT, EXPORTED, MODIFIED):
            return False
        role = self.get_user_role(user.name)
        return role in ('members', 'reviewers')
