# -*- coding: UTF-8 -*-
# Copyright (C) 2011 Hervé Cauwelier <herve@itaapy.com>
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

# Import from ikaaro

# Import from iscrib


def is_demo_application(resource):
    from application import Application

    application = resource
    while application is not None:
        if isinstance(application, Application):
            break
        application = application.parent
    else:
        return False
    return application.get_property('subscription') == 'demo'


def get_demo_user(resource):
    results = resource.get_root().search(username='demo')
    for brain in results.get_documents():
        return resource.get_resource(brain.abspath)
    # Create dummy on the fly
    users = resource.get_resource('/users')
    return users.set_user(email='demo@itaapy.com')


def is_demo_form(resource):
    demo_user = get_demo_user(resource)
    return resource.name == demo_user.name
