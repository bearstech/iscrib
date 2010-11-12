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
from itools.datatypes import String, Unicode, Email
from itools.gettext import MSG
from itools.uri import encode_query, get_reference, Reference
from itools.web import BaseView, STLView

# Import from ikaaro
from ikaaro.buttons import Button
from ikaaro.autoform import AutoForm, TextWidget, PasswordWidget
from ikaaro.control_panel import CPEditContactOptions
from ikaaro.website_views import ContactForm

# Import from iscrib
from autoform import RecaptchaDatatype, RecaptchaWidget
from base_views import FrontView
from utils import is_production
from workgroup import Workgroup


class Root_View(AutoForm):

    access = True
    title = MSG(u"View")
    template = "/ui/iscrib/root_view.xml"

    actions = [Button(access=True, css='button-create', title=MSG(u'Create'))]
    schema = {
        'title': Unicode(mandatory=True),
        'email': Email(mandatory=True),
        'password': String(mandatory=True),
        'password2': String(mandatory=True)}
    widgets = [
        TextWidget('title', title=MSG(u'Name of your client space'),
                tip=MSG(u'You can type the name of your company or '
                    u'organization')),
        TextWidget('email', title=MSG(u"E-mail address")),
        PasswordWidget('password', title=MSG(u"Password")),
        PasswordWidget('password2', title=MSG(u"Repeat Password"))]


    def get_namespace(self, resource, context):
        namespace = AutoForm.get_namespace(self, resource, context)
        # widgets
        widgets_dict = {}
        for widget in namespace['widgets']:
            widgets_dict[widget['name']] = widget
        namespace['widgets_dict'] = widgets_dict

        return namespace


    def action(self, resource, context, form):
        goto = '/;new_resource'
        query = {'type': 'Workgroup'}
        for key in ('title', 'email'):#, 'password', 'password2'):
            query[key] = str(form[key])
        return get_reference('%s?%s' % (goto, encode_query(query)))



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

        namespace['size'] = self.size

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
        return merge_dicts(schema, name=Unicode, company=Unicode,
                function=Unicode, phone=Unicode(mandatory=True),
                captcha=RecaptchaDatatype(mandatory=is_production))


    def get_widgets(self, resource, context):
        widgets = super(Root_Contact, self).get_widgets(resource, context)
        widgets = (widgets[:2]
                + [TextWidget('name', title=MSG(u"Name")),
                    TextWidget('company', title=MSG(u"Company/Organization")),
                    TextWidget('function', title=MSG(u"Function")),
                    TextWidget('phone', title=MSG(u"Phone Number"))]
                + widgets[2:-1])
        if is_production:
            widgets += [RecaptchaWidget('captcha')]
        return widgets


    def _get_form(self, resource, context):
        form = super(Root_Contact, self)._get_form(resource, context)

        body = form['message_body']
        body = MSG(u"\r\n{body}").gettext(body=body)
        for name in ('phone', 'from', 'function', 'company', 'name'):
            title = None
            for widget in self.get_widgets(resource, context):
                if widget.name == name:
                    title = widget.title.gettext()
            value = form[name]
            body = MSG(u"{title}: {value}\r\n{body}").gettext(title=title,
                    value=value, body=body)
        form['message_body'] = body

        return form




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
