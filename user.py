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
from itools.datatypes import String, Unicode
from itools.gettext import MSG
from itools.web import INFO

# Import from ikaaro
from ikaaro.messages import MSG_REGISTERED, MSG_BAD_KEY
from ikaaro.messages import MSG_PASSWORD_MISMATCH
from ikaaro.autoform import AutoForm, HiddenWidget, PasswordWidget
from ikaaro.autoform import TextWidget
from ikaaro.registry import register_resource_class
from ikaaro.user import User as BaseUser
from ikaaro.user_views import User_EditAccount as BaseUser_EditAccount


class User_ConfirmRegistration(AutoForm):

    access = True
    title = MSG(u'Choose your password')

    schema = {
        'key': String(mandatory=True),
        'company': Unicode(mandatory=True),
        'newpass': String(mandatory=True),
        'newpass2': String(mandatory=True)}

    widgets = [
        HiddenWidget('key', title=None),
        TextWidget('company', title=MSG(u'Company')),
        PasswordWidget('newpass', title=MSG(u'Password')),
        PasswordWidget('newpass2', title=MSG(u'Repeat your password'))]


    def get_namespace(self, resource, context):
        # Check register key
        must_confirm = resource.get_property('user_must_confirm')
        username = context.get_form_value('username', default='')
        if must_confirm is None:
            return context.come_back(MSG_REGISTERED,
                    goto='/;login?username=%s' % username)
        elif context.get_form_value('key') != must_confirm:
            return context.come_back(MSG_BAD_KEY,
                    goto='/;login?username=%s' % username)
        return AutoForm.get_namespace(self, resource, context)


    def get_value(self, resource, context, name, datatype):
        if name == 'key':
            return resource.get_property('user_must_confirm')
        return AutoForm.get_value(self, resource, context, name, datatype)


    def action(self, resource, context, form):
        # Check register key
        must_confirm = resource.get_property('user_must_confirm')
        if form['key'] != must_confirm:
            context.message = MSG_BAD_KEY
            return

        # Check passwords
        password = form['newpass']
        password2 = form['newpass2']
        if password != password2:
            context.message = MSG_PASSWORD_MISMATCH
            return

        # Set user
        resource.set_password(password)
        resource.del_property('user_must_confirm')

        # Company
        resource.set_property('company', form['company'])

        # Set cookie
        resource.set_auth_cookie(context, password)

        # Ok
        message = INFO(u"Your account was created! You can create a "
                u"collection application.")
        return context.come_back(message, goto='/')



class User_EditAccount(BaseUser_EditAccount):
    schema = merge_dicts(BaseUser_EditAccount.schema,
        company=Unicode(mandatory=True))
    widgets = (BaseUser_EditAccount.widgets[:2]
        + [TextWidget('company', title=MSG(u"Société"))]
        + BaseUser_EditAccount.widgets[2:])



class User(BaseUser):
    class_schema = merge_dicts(BaseUser.class_schema,
            company=Unicode(source='metadata'))

    # Views
    edit_account = User_EditAccount()
    confirm_registration = User_ConfirmRegistration()



register_resource_class(User)
