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
from itools.datatypes import Unicode
from itools.gettext import MSG
from itools.web import INFO, ERROR

# Import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.user_views import User_EditAccount as BaseUser_EditAccount
from ikaaro.user_views import (User_ConfirmRegistration
        as BaseUser_ConfirmRegistration)
from ikaaro.user_views import (User_ChangePasswordForgotten
        as BaseUser_ChangePasswordForgotten)


class User_ConfirmRegistration(BaseUser_ConfirmRegistration):
    schema = merge_dicts(BaseUser_ConfirmRegistration.schema,
        company=Unicode(mandatory=True))
    widgets = (BaseUser_ConfirmRegistration.widgets[:2]
            + [TextWidget('company', title=MSG(u'Company'))]
            + BaseUser_ConfirmRegistration.widgets[2:])


    def action(self, resource, context, form):
        goto = super(User_ConfirmRegistration, self).action(resource,
                context, form)
        if isinstance(context.message, ERROR):
            return

        # Company
        resource.set_property('company', form['company'])

        message = INFO(u'Operation successful! Welcome.')
        return context.come_back(message, goto='/;show')



class User_ChangePasswordForgotten(BaseUser_ChangePasswordForgotten,
        User_ConfirmRegistration):
    pass



class User_EditAccount(BaseUser_EditAccount):
    schema = merge_dicts(BaseUser_EditAccount.schema,
        company=Unicode(mandatory=True))
    widgets = (BaseUser_EditAccount.widgets[:2]
        + [TextWidget('company', title=MSG(u"Company"))]
        + BaseUser_EditAccount.widgets[2:])
