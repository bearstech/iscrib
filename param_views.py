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

# Import from the Standard Library
from cStringIO import StringIO
from email.utils import parseaddr

# Import from lpod
from lpod import ODF_SPREADSHEET
from lpod.document import odf_get_document

# Import from itools
from itools.core import merge_dicts
from itools.csv import CSVFile
from itools.database import PhraseQuery, AndQuery, NotQuery
from itools.datatypes import Integer, Unicode, Email, String
from itools.gettext import MSG
from itools.uri import get_reference, get_uri_path
from itools.web import INFO, ERROR, BaseView

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.autoform import FileWidget, TextWidget
from ikaaro.datatypes import FileDataType
from ikaaro.file import ODS
from ikaaro.folder_views import Folder_BrowseContent, GoToSpecificDocument
from ikaaro.messages import MSG_PASSWORD_MISMATCH
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views_new import NewInstance

# Import from iscrib
from base import LoginView
from form import Form
from formpage import FormPage


class Param_NewInstance(NewInstance):
    access = 'is_allowed_to_add_param'
    schema = merge_dicts(NewInstance.schema,
            file=FileDataType(mandatory=True))
    widgets = (NewInstance.widgets
            + [FileWidget('file', title=MSG(u"ODS File"))])


    def action(self, resource, context, form):
        goto = NewInstance.action(self, resource, context, form)
        child = resource.get_resource(form['name'])
        filename, mimetype, body = form['file']
        if mimetype != ODF_SPREADSHEET:
            context.message = ERROR(u"not an ODS file")
            return
        # Save file used
        ods = child.make_resource('parameters', ODS, body=body,
                filename=filename, title={'en': u"Parameters"})
        stringio = StringIO(body)
        document = odf_get_document(stringio)
        if document.get_mimetype() != ODF_SPREADSHEET:
            context.message = ERROR(u"not an ODS file")
            return
        tables = iter(document.get_body().get_tables())
        # Controls and Schema
        for name, cls in [('controls', child.controls_class),
                          ('schema', child.schema_class)]:
            table = tables.next()
            table.rstrip(aggressive=True)
            table.delete_row(0)
            try:
                child.make_resource(name, cls,
                        title={'en': table.get_name()}, body=table.to_csv())
            except ValueError, e:
                context.commit = False
                message = ERROR(unicode(e))
                context.message = message
                return
        # Pages
        for table in tables:
            table.rstrip(aggressive=True)
            title = table.get_name()
            if title[1] != u" ":
                context.commit = False
                message = u'Page names must be in the form "C Title..."'
                context.message = ERROR(message)
                return
            page_number, _ = title.split(u" ", 1)
            name = 'page' + page_number.lower().encode()
            body = table.to_csv()
            try:
                child.make_resource(name, FormPage, title={'en': title},
                        body=body)
            except Exception, e:
                context.commit = False
                context.message = ERROR(unicode(e))
                return
        # Initial form
        child.make_resource(child.default_form, Form,
                title={'en': u"Test Form"})
        return goto



class Param_View(Folder_BrowseContent):
    access = 'is_allowed_to_edit'
    title = MSG(u"View")
    template = '/ui/iscrib/param/view.xml'
    search_template = None

    table_columns = [
            ('name', MSG(u"Form")),
            ('state', MSG(u"State")),
            ('mtime', MSG(u"Last Modified")),
            ('user', MSG(u"User")),
            ('email', MSG(u"E-mail")),
            ('registered', MSG(u"Registered"))]
    table_actions = []


    def get_items(self, resource, context, *args):
        items = super(Param_View, self).get_items(resource, context,
                AndQuery(PhraseQuery('format', Form.class_id),
                    NotQuery(PhraseQuery('name', resource.default_form))),
                *args)
        # XXX
        context.n_forms = len(items)
        return items


    def get_item_value(self, resource, context, item, column):
        brain, item_resource = item
        if column == 'name':
            return (brain.name, context.get_link(item_resource))
        elif column == 'state':
            return (item_resource.get_form_state(),
                    '{0}/;envoyer'.format(context.get_link(item_resource)))
        if column in ('user', 'email', 'registered'):
            user = context.root.get_user(brain.name)
            if column == 'user':
                if user is None:
                    return brain.name
                return user.get_title()
            elif column == 'email':
                email = user.get_property('email')
                return (email, 'mailto:{0}'.format(email))
            elif column == 'registered':
                password = user.get_property('password')
                return u"Yes" if password else u"No"
        return super(Param_View, self).get_item_value(resource, context,
                item, column)


    def get_namespace(self, resource, context):
        namespace = super(Param_View, self).get_namespace( resource, context)
        # XXX
        n_forms = context.n_forms
        namespace['n_forms'] = n_forms
        max_users = resource.get_property('max_users')
        namespace['max_users'] = max_users
        allowed_users = (max_users - n_forms) if max_users else 20
        namespace['allowed_users'] = allowed_users
        return namespace



class Param_Export(BaseView):
    access = 'is_allowed_to_edit'
    title = MSG(u"Export Collected Data")


    def GET(self, resource, context, encoding='cp1252'):
        csv = CSVFile()
        header = ["Form", "User", "E-mail", "State"]
        handler = resource.get_resource('schema').handler
        schema, pages = handler.get_schema_pages()
        for name in sorted(schema):
            header.append(name)
        csv.add_row(header)
        users = resource.get_resource('/users')
        for form in resource.get_forms():
            user = users.get_resource(form.name, soft=True)
            if user:
                email = user.get_property('email')
                user = user.get_title()
            else:
                email = ""
                user = form.name
            state = form.get_form_state().encode(encoding)
            row = [form.name, user, email, state]
            handler = form.handler
            for name, datatype in sorted(schema.iteritems()):
                value = handler.get_value(name, schema)
                try:
                    value = datatype.encode(value, encoding)
                except TypeError:
                    value = datatype.encode(value)
                if type(value) is not str:
                    raise ValueError, str(type(header))
                row.append(value)
            csv.add_row(row)

        context.set_content_type('text/comma-separated-values')
        context.set_content_disposition('attachment',
                filename="%s.csv" % (resource.name))

        return csv.to_str(separator=';')



class Param_Register(Param_View):
    access = 'is_allowed_to_edit'
    title = MSG(u"Register Users")
    template = '/ui/iscrib/param/register.xml'

    schema = {'new_users': Unicode}

    table_columns = [
            ('user', MSG(u"User")),
            ('email', MSG(u"E-mail"))]


    def get_namespace(self, resource, context):
        namespace = super(Param_Register, self).get_namespace(resource,
                context)
        namespace['title'] = self.title
        namespace['new_users'] = context.get_form_value('new_users')
        namespace['url_user'] = context.uri.resolve(';login')
        namespace['url_admin'] = context.uri.resolve(';view')
        return namespace


    def action(self, resource, context, form):
        new_users = form['new_users'].strip()
        users = resource.get_resource('/users')
        root = context.root
        site_root = resource.get_site_root()
        added = []
        for lineno, line in enumerate(new_users.splitlines()):
            lastname, email = parseaddr(line)
            try:
                email = email.encode('ascii')
            except UnicodeEncodeError:
                email = None
            if not email:
                context.commit = False
                message = u"Unrecognized line {lineno}: {line}"
                context.message = ERROR(message, lineno=lineno+1, line=line)
                return
            # Is the user already known?
            user = root.get_user_from_login(email)
            if user is None:
                # Register the user
                user = users.set_user(email, None)
                user.set_property('lastname', lastname)
            username = user.name
            # Add the form
            if resource.get_resource(username, soft=True) is not None:
                continue
            resource.make_resource(username, Form,
                    title={'en': lastname})
            added.append(username)

        if not added:
            context.message = ERROR(u"No user added.")
            return

        context.body['new_users'] = u""

        message = u"{n} users added. See below to send them the form URL."
        context.message = INFO(message, n=len(added))



class Param_Edit(DBResource_Edit):

    def _get_schema(self, resource, context):
        schema = super(Param_Edit, self)._get_schema(resource, context)
        if is_admin(context.user, resource):
            schema['max_users'] = Integer
        return schema


    def _get_widgets(self, resource, context):
        widgets = super(Param_Edit, self)._get_widgets(resource, context)
        if is_admin(context.user, resource):
            widgets.append(TextWidget('max_users',
                title=MSG(u"Maximum form users (0 = unlimited)")))
        return widgets



class Param_Login(LoginView):
    template = '/ui/iscrib/param/login.xml'
    schema = merge_dicts(LoginView.schema,
            password=String(mandatory=True),
            password2=String)


    def action_register(self, resource, context, form):
        email = form['username'].strip()
        if not Email.is_valid(email):
            message = u'The given username is not an email address.'
            context.message = ERROR(message)
            return

        user = context.root.get_user_from_login(email)

        # Is allowed?
        if user is None:
            error = u"You are not allowed to register."
            context.message = ERROR(error)
            return

        # Is already registered?
        if user.get_property('password') is not None:
            message = (u"You are already registered. "
                    u"Log in using your password.")
            context.message = ERROR(message)
            return

        # Register
        password = form['password']
        password2 = form['password2']
        if password != password2:
            context.message = MSG_PASSWORD_MISMATCH
            return

        user.set_password(password)

        # Send e-mail with login
        site_uri = context.uri.resolve(';login')
        user.send_autoregistration(context, email, site_uri, password)

        # Automatic login
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



class Param_RedirectToForm(GoToSpecificDocument):
    access = 'is_allowed_to_view_param'
    title = MSG(u"Show Form")


    def get_form_name(self, user, resource):
        ac = resource.get_access_control()
        if ac.is_allowed_to_edit(user, resource):
            return resource.default_form
        if resource.get_resource(user.name, soft=True) is not None:
            return user.name
        return None


    def get_specific_document(self, resource, context):
        return self.get_form_name(context.user, resource)
