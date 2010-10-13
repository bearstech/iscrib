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
from itools.stl import stl
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR

# Import from ikaaro
from ikaaro.resource_ import DBResource
from ikaaro.resource_views import DBResource_Edit, LoginView as BaseLoginView
from ikaaro.workflow import state_widget, WorkflowAware, StateEnumerate

# Import from iscrib


class AutomaticEditView(DBResource_Edit):
    base_schema = DBResource_Edit.schema

    def _get_schema(self, resource, context):
        schema = merge_dicts(DBResource_Edit.schema, resource.edit_schema)
        if isinstance(resource, WorkflowAware):
            schema['state'] = StateEnumerate(resource=resource,
                    context=context)
        return schema


    def _get_widgets(self, resource, context):
        widgets = self.widgets + resource.edit_widgets
        # Add state widget in bottom
        if isinstance(resource, WorkflowAware):
            widgets.append(state_widget)
        return widgets


    def get_value(self, resource, context, name, datatype):
        if name == 'state':
            return resource.get_workflow_state()
        return DBResource_Edit.get_value(self, resource, context, name,
                datatype)


    def set_value(self, resource, context, name, form):
        schema = self.get_schema(resource, context)
        datatype = schema[name]
        if getattr(datatype, 'ignore', False) is True:
            return False
        return DBResource_Edit.set_value(self, resource, context, name, form)



# Pas d'héritage pour pas de méthode "action"
class LoginView(BaseLoginView):
    template = '/ui/iscrib/login.xml'


    def action_login(self, resource, context, form):
        email = form['username'].strip()
        password = form['password']

        user = context.root.get_user_from_login(email)
        if user is None or not user.authenticate(password, clear=True):
            message = u'The e-mail or the password is incorrect.'
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
        print "goto", goto

        return context.come_back(INFO(u"Welcome!"), goto)


    def action_register(self, resource, context, form):
        email = form['username'].strip()
        if not Email.is_valid(email):
            message = u'The given username is not an e-mail address.'
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



DBResource.login = LoginView()
