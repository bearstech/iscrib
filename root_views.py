# -*- coding: UTF-8 -*-
# Copyright (C) 2006, 2008-2010 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2009 Taverne Sylvain <sylvain@itaapy.com>
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
from itools.gettext import MSG
from itools.web import BaseView

# Import from ikaaro
from ikaaro.views import IconsView

# Import from iscrib
from application import Application


class Root_View(BaseView):
    access = True
    title = MSG(u"View")


    def GET(self, resource, context):
        homepage = resource.get_property('homepage')
        if homepage is None:
            # Avoid response abort
            return ''
        return homepage



class Root_Clients(IconsView):
    access = 'is_authenticated'
    title = MSG(u"Clients")


    def get_namespace(self, resource, context):
        items = []
        for application in resource.search_resources(cls=Application):
            if not application.is_allowed_to_view(context.user, application):
                continue
            items.append({'icon': '/ui/' + application.class_icon48,
                'title': application.get_title(),
                'description': application.get_property('description'),
                'url': context.get_link(application)})
        return {'batch': None, 'items': items}
