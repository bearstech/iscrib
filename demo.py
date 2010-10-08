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
from itools.datatypes import Email
from itools.gettext import MSG
from itools.stl import stl
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR

# Import from ikaaro
from ikaaro.registry import register_document_type
from ikaaro.resource_ import DBResource
from ikaaro.resource_views import LoginView as BaseLoginView
from ikaaro.skins import Skin
from ikaaro.website import WebSite

# Import from iscrib
from application import Application
from application_views import Application_BrowseContent
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



# Pas d'héritage pour pas de méthode "action"
class LoginView(BaseLoginView):
    template = '/ui/iscrib/login.xml'


    def action_login(self, resource, context, form):
        email = form['username'].strip()
        password = form['password']

        user = context.root.get_user_from_login(email)
        if user is None or not user.authenticate(password, clear=True):
            message = u'The email or the password is incorrect.'
            context.message = ERROR(message)
            return

        # Set cookie & context
        user.set_auth_cookie(context, password)
        context.user = user

        # Come back
        referrer = context.get_referrer()
        if referrer is None:
            goto = get_reference('./')
        else:
            path = get_uri_path(referrer)
            if path.endswith(';login'):
                goto = get_reference('./')
            else:
                goto = referrer

        return context.come_back(INFO(u"Welcome!"), goto)


    def action_register(self, resource, context, form):
        email = form['username'].strip()
        if not Email.is_valid(email):
            message = u'The given username is not an email address.'
            context.message = ERROR(message)
            return

        user = context.root.get_user_from_login(email)

        # Case 1: Register
        if user is None:
            if context.site_root.is_allowed_to_register():
                return self._register(resource, context, email)
            error = u"You are not allowed to register."
            context.message = ERROR(error)
            return

        # Case 2: Forgotten password
        email = user.get_property('email')
        user.send_forgotten_password(context, email)
        path = '/ui/website/forgotten_password.xml'
        handler = resource.get_resource(path)
        return stl(handler)



class Demo(Application):
    class_id = 'Demo'
    class_title = MSG(u"Site de démo iScrib")
    class_skin = 'ui/iscrib'

    # Views
    view = Application_BrowseContent(access='is_allowed_to_view',
            title=MSG(u"View"))
    unauthorized = LoginView()



class Demo_Skin(Skin):

    def build_namespace(self, context):
        return merge_dicts(Skin.build_namespace(self, context),
                  website_title=context.site_root.get_property('title'))



register_document_type(Demo, WebSite.class_id)
DBResource.login = LoginView()
