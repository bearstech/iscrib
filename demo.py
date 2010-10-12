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
from itools.gettext import MSG
from itools.web import INFO

# Import from ikaaro
from ikaaro.registry import register_document_type
from ikaaro.skins import Skin
from ikaaro.website import WebSite

# Import from iscrib
from application import Application
from application_views import Application_BrowseContent
from base import LoginView
from form import Form
from form_views import Form_Send
from param import Param


class ParamForm_Send(Form_Send):

    def get_namespace(self, resource, context):
        # FIXME
        namespace = super(ParamForm_Send, self).get_namespace(resource,
                context)
        namespace['first_time'] = resource.is_first_time()
        return namespace


    def action_send(self, resource, context, form):
        message = INFO(u"Your report was successfully sent.")
        context.message = message


    def action_export(self, resource, context, form):
        message = INFO(u"Your report was successfully exported.")
        context.message = message



class ParamForm(Param, Form):
    """Application avec un seul formulaire en proxy
    """
    class_id = 'ParamForm'
    class_views = ['pageA'] + Form.class_views
    class_schema = merge_dicts(Form.class_schema, Param.class_schema)

    # Views
    envoyer = ParamForm_Send()


    def get_catalog_values(self):
        form = self.get_form()
        if form:
            values = Form.get_catalog_values(self)
        else:
            values = {}
        return merge_dicts(values, Param.get_catalog_values(self))



class Demo(Application):
    class_id = 'Demo'
    class_title = MSG(u"Site de démo iScrib")
    class_skin = 'ui/iscrib'
    # Rôle par défaut members au lieu de guests
    class_roles = WebSite.class_roles[1:]

    # Views
    view = Application_BrowseContent(access='is_allowed_to_view',
            title=MSG(u"View"))
    unauthorized = LoginView()



class Demo_Skin(Skin):

    def build_namespace(self, context):
        return merge_dicts(Skin.build_namespace(self, context),
                  website_title=context.site_root.get_property('title'))



register_document_type(Demo, WebSite.class_id)
