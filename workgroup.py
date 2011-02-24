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
from itools.core import merge_dicts, freeze
from itools.datatypes import Boolean, PathDataType
from itools.gettext import MSG
from itools.web import get_context

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.control_panel import ControlPanel
from ikaaro.theme_views import Theme_AddFavIcon, Theme_AddLogo
from ikaaro.website import WebSite

# Import from iscrib
from application import Application
from base_views import FrontView, LoginView
from demo import is_demo_application, is_demo_form
from form import Form
from workflow import FINISHED, EXPORTED, MODIFIED
from workgroup_views import Workgroup_NewInstance, Workgroup_View
from workgroup_views import Workgroup_Edit


class Workgroup(WebSite):
    class_id = 'Workgroup'
    class_title = MSG(u"iScrib Workgroup")
    class_description = MSG(u"Create your client space to manage collection "
            u"applications and submit them.")
    class_schema = freeze(merge_dicts(
        WebSite.class_schema,
        logo=PathDataType(source='metadata', default=''),
        accept_terms_of_use=Boolean(source='metadata')))
    class_views = WebSite.class_views + ['show']
    class_skin = 'ui/iscrib'

    # Views
    new_instance = Workgroup_NewInstance()
    view = Workgroup_View()
    edit = Workgroup_Edit()
    show = FrontView(title=MSG(u"Your Collection Applications"),
            cls=Application)
    add_favicon = Theme_AddFavIcon()
    add_logo = Theme_AddLogo()
    # Security
    control_panel = ControlPanel(access='is_admin')
    unauthorized = LoginView()


    def init_resource(self, **kw):
        super(Workgroup, self).init_resource(**kw)
        theme = self.get_resource('theme')
        # Laisse voir le nom du website
        theme.set_property('logo', None)


    def get_document_types(self):
        return super(Workgroup, self).get_document_types() + [Application]


    def get_logo_icon(self, size=48):
        context = get_context()
        if context is not None:
            theme = self.get_resource('theme')
            logo_path = theme.get_property('logo')
            if logo_path not in ('', '.'):
                logo = theme.get_resource(logo_path)
                return '{0}/;thumb?width={1}&height={1}'.format(
                        context.resource.get_pathto(logo), size)
        return super(Workgroup, self).get_class_icon(size=size)


    def is_allowed_to_add_form(self, user, resource):
        return is_admin(user, resource)


    def is_allowed_to_view(self, user, resource):
        if user is None:
            if is_demo_application(resource):
                if isinstance(resource, Application):
                    return True
                elif isinstance(resource, Form):
                    return is_demo_form(resource)
                # Allow public content (parameters, theme, etc.)
                try:
                    return resource.get_workflow_state() == 'public'
                except AttributeError:
                    pass
            return False
        if is_admin(user, resource):
            return True
        role = self.get_user_role(user.name)
        if isinstance(resource, Application):
            subscription = resource.get_property('subscription')
            if subscription == 'demo':
                return True
            elif role in ('members', 'reviewers'):
                return True
            return resource.show.get_form_name(user, resource) is not None
        elif isinstance(resource, Form):
            return (role in ('members', 'reviewers')
                    or user.name == resource.name)
        abspath = resource.get_abspath()
        if len(abspath) > 1 and abspath[1] == 'theme':
            return role in ('guests', 'members', 'reviewers')
        return super(Workgroup, self).is_allowed_to_view(user, resource)


    def is_allowed_to_edit(self, user, resource):
        if user is None:
            if is_demo_application(resource):
                if isinstance(resource, Form):
                    return is_demo_form(resource)
            return False
        if is_admin(user, resource):
            return True
        role = self.get_user_role(user.name)
        if isinstance(resource, (Workgroup, Application)):
            return role in ('members', 'reviewers')
        elif isinstance(resource, Form):
            if resource.name == resource.parent.default_form:
                return role in ('members', 'reviewers')
            return resource.name == user.name or role == 'reviewers'
        elif resource.get_abspath()[1] == 'theme':
            return role in ('members', 'reviewers')
        return super(Workgroup, self).is_allowed_to_edit(user, resource)


    def is_allowed_to_export(self, user, resource):
        # XXX
        return False
        if user is None:
            return False
        if is_admin(user, resource):
            return True
        state = resource.get_workflow_state()
        if state not in (FINISHED, EXPORTED, MODIFIED):
            return False
        role = self.get_user_role(user.name)
        return role in ('members', 'reviewers')
