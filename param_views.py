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

# Import from lpod
from lpod import ODF_SPREADSHEET
from lpod.document import odf_get_document

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Integer
from itools.gettext import MSG
from itools.web import ERROR

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.autoform import FileWidget, TextWidget
from ikaaro.datatypes import FileDataType
from ikaaro.file import ODS
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views import IconsView
from ikaaro.views_new import NewInstance

# Import from iscrib
from form import Form
from formpage import FormPage


class Param_NewInstance(NewInstance):
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



class Param_View(IconsView):
    access = 'is_allowed_to_edit'
    title = MSG(u"View")

    
    def get_namespace(self, resource, context):
        items = []
        for name in sorted(resource.get_names()):
            item = resource.get_resource(name)
            items.append({'icon': '/ui/' + item.class_icon48,
                'title': item.get_title(),
                'description': None,
                'url': context.get_link(item)})
        return {'batch': None, 'items': items}



class Param_Edit(DBResource_Edit):

    def _get_schema(self, resource, context):
        schema = DBResource_Edit._get_schema(self, resource, context)
        if is_admin(context.user, resource):
            schema['max_users'] = Integer
        return schema


    def _get_widgets(self, resource, context):
        widgets = DBResource_Edit._get_widgets(self, resource, context)
        if is_admin(context.user, resource):
            widgets.append(TextWidget('max_users',
                title=MSG(u"Maximum form users")))
        return widgets
