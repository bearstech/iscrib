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
from itools.core import merge_dicts, is_thingy, freeze
from itools.datatypes import Unicode
from itools.gettext import MSG
from itools.web import INFO, ERROR

# Import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.csv_views import CSVColumn
from ikaaro.user_views import User_EditAccount as BaseUser_EditAccount
from ikaaro.user_views import (User_ConfirmRegistration
        as BaseUser_ConfirmRegistration)
from ikaaro.user_views import (User_ChangePasswordForgotten
        as BaseUser_ChangePasswordForgotten)
from ikaaro.user_views import (UserFolder_BrowseContent
        as BaseUserFolder_BrowseContent)


class User_ConfirmRegistration(BaseUser_ConfirmRegistration):
    schema = freeze(merge_dicts(
        BaseUser_ConfirmRegistration.schema,
        company=Unicode(mandatory=True)))
    widgets = freeze(
        BaseUser_ConfirmRegistration.widgets[:2]
        + [TextWidget('company', title=MSG(u'Company/Organization'))]
        + BaseUser_ConfirmRegistration.widgets[2:])


    def action(self, resource, context, form):
        proxy = super(User_ConfirmRegistration, self)
        proxy.action(resource, context, form)
        if is_thingy(context.message, ERROR):
            return

        # Company
        resource.set_property('company', form['company'])

        message = INFO(u'Operation successful! Welcome.')
        return context.come_back(message, goto='/;show')



class User_ChangePasswordForgotten(BaseUser_ChangePasswordForgotten,
        User_ConfirmRegistration):
    pass



class User_EditAccount(BaseUser_EditAccount):
    schema = freeze(merge_dicts(
        BaseUser_EditAccount.schema,
        company=Unicode(mandatory=True)))
    widgets = freeze(BaseUser_EditAccount.widgets[:3]
        + [TextWidget('company', title=MSG(u"Company/Organization"))]
        + BaseUser_EditAccount.widgets[3:])



class UserFolder_BrowseContent(BaseUserFolder_BrowseContent):
    search_fields = freeze(
            BaseUserFolder_BrowseContent.search_fields
            + [('company', MSG(u"Company"))])

    table_columns = freeze(
            BaseUserFolder_BrowseContent.table_columns[:6]
            + [('company', MSG(u"Company"), True)]
            + BaseUserFolder_BrowseContent.table_columns[6:])

    csv_columns = freeze(
            BaseUserFolder_BrowseContent.csv_columns[:3]
            + [CSVColumn('company', title=u"Company")])


    def get_key_sorted_by_company(self):
        return self._get_key_sorted_by_unicode('company')
