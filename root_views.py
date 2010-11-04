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
from itools.core import merge_dicts
from itools.datatypes import String, Unicode
from itools.gettext import MSG
from itools.uri import Reference
from itools.web import BaseView

# Import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.control_panel import CPEditContactOptions
from ikaaro.website_views import ContactForm

# Import from iscrib
from autoform import RecaptchaDatatype, RecaptchaWidget
from base_views import FrontView
from workgroup import Workgroup


class Root_View(BaseView):
    access = True
    title = MSG(u"View")


    def GET(self, resource, context):
        homepage = resource.get_property('homepage')
        if homepage is None:
            # Avoid response abort
            return ''
        return homepage



class Root_Show(FrontView):
    template = '/ui/iscrib/root/show.xml'
    title = MSG(u"Your Client Space")
    cls = Workgroup
    size = 128
    cols = 5


    def get_namespace(self, resource, context):
        namespace = super(Root_Show, self).get_namespace(resource, context)
        if isinstance(namespace, Reference):
            return namespace

        members = []
        guests = []
        for item in namespace['items']:
            if item['icon'] is None:
                item['icon'] = self.cls.get_class_icon(size=48)
            if item['role'] == 'members':
                rows = members
            else:
                rows = guests
            if not rows:
                rows.append([])
            rows[-1].append(item)
            if len(rows[-1]) == self.cols:
                rows.append([])
        namespace['members'] = members
        namespace['guests'] = guests
        return namespace



class Root_Contact(ContactForm):
    template = '/ui/iscrib/root/contact.xml'

    def get_schema(self, resource, context):
        schema = super(Root_Contact, self).get_schema(resource, context)
        return merge_dicts(schema, societe=Unicode, fonction=Unicode,
                phone=Unicode(mandatory=True),
                captcha=RecaptchaDatatype(mandatory=True))


    def get_widgets(self, resource, context):
        widgets = super(Root_Contact, self).get_widgets(resource, context)
        return (widgets[:2]
                + [TextWidget('societe', title=MSG(u"Company/Organization")),
                    TextWidget('fonction', title=MSG(u"Function")),
                    TextWidget('phone', title=MSG(u"Phone Number"))]
                + widgets[2:-1]
                + [RecaptchaWidget('captcha')])



class Root_EditContactOptions(CPEditContactOptions):
    recaptcha_schema = {'recaptcha_private_key': String(mandatory=True),
            'recaptcha_public_key': String(mandatory=True)}
    recaptcha_widgets = [TextWidget('recaptcha_private_key',
            title=MSG(u"ReCaptcha Private Key")),
        TextWidget('recaptcha_public_key',
            title=MSG(u"ReCaptcha Public Key"))]


    def _get_schema(self, resource, context):
        schema = super(Root_EditContactOptions, self)._get_schema(resource,
                context)
        del schema['captcha_question']
        del schema['captcha_answer']
        return merge_dicts(schema, self.recaptcha_schema)


    def _get_widgets(self, resource, context):
        widgets = super(Root_EditContactOptions, self)._get_widgets(resource,
                context)[:-2]
        return widgets + self.recaptcha_widgets
