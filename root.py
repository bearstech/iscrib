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
from itools.core import merge_dicts, get_abspath
from itools.datatypes import String
from itools.fs import FileName
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.autoform import XHTMLBody, RTEWidget
from ikaaro.file import Image
from ikaaro.root import Root as BaseRoot
from ikaaro.workflow import WorkflowAware

# Import from iscrib
from base_views import AutomaticEditView, LoginView
from root_views import Root_View, Root_Show, Root_Contact
from root_views import Root_EditContactOptions
from workgroup import Workgroup


class Root(BaseRoot):
    class_id = 'iScrib'
    class_schema = merge_dicts(BaseRoot.class_schema,
            homepage=XHTMLBody(source='metadata', multilingual=True,
                parameters_schema = {'lang': String}),
            recaptcha_private_key=String(source='metadata'),
            recaptcha_public_key=String(source='metadata'))
    class_views = BaseRoot.class_views + ['show']
    class_skin = 'ui/iscrib'

    edit_schema = {'homepage': XHTMLBody(multilingual=True)}
    edit_widgets = [RTEWidget('homepage', title=MSG(u'Homepage'))]

    # Views
    view = Root_View()
    edit = AutomaticEditView()
    show = Root_Show()
    contact = Root_Contact()
    edit_contact_options = Root_EditContactOptions()
    # Security
    unauthorized = LoginView()


    def init_resource(self, email, password, admins=('0',)):
        super(Root, self).init_resource(email, password, admins=admins)
        self.set_property('title', u"iScrib", language='en')
        value = self.class_schema['homepage'].decode("""
                <h2>Welcome to iScrib!</h2>
                <ul>
                  <li><a href=";new_resource?type=Workgroup">Create a
                  workgroup</a>;</li>
                  <li><a href=";show">Your workgroups (authenticated users
                  only)</a>.</li>
                </ul>""")
        self.set_property('homepage', value, language='en')
        # Laisse voir le nom du website
        theme = self.get_resource('theme')
        theme.set_property('logo', None)
        # Favicon à utiliser partout
        filename = 'itaapy-favicon.ico'
        with open(get_abspath('ui/' + filename)) as file:
            body = file.read()
        name, extension, _ = FileName.decode(filename)
        theme.make_resource(name, Image, body=body, filename=filename,
                extension=extension, state='public', format='image/x-icon')
        theme.set_property('favicon', name)


    def get_document_types(self):
        return super(Root, self).get_document_types() + [Workgroup]


    def get_page_title(self):
        return None


    def is_allowed_to_view(self, user, resource):
        abspath = resource.get_abspath()
        if abspath and abspath[0] in ('gabarit', 'samples',
                'terms-and-conditions', 'theme'):
            if isinstance(resource, WorkflowAware):
                state = resource.get_workflow_state()
            else:
                state = 'public'
            if state == 'public':
                return True
        return super(Root, self).is_allowed_to_view(user, resource)
