# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006 luis <luis@lucifer.localdomain>
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2008 Henry Obein <henry@itaapy.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Import from the Standard Library
from cStringIO import StringIO

# Import from itools
from itools.gettext import MSG
from itools.web import INFO, ERROR

# Import from ikaaro
from ikaaro.datatypes import FileDataType
from ikaaro.forms import AutoForm, FileWidget
from ikaaro.views import IconsView

# Import from lpod
from lpod.container import ODF_SPREADSHEET
from lpod.document import odf_get_document

# Import from scrib


class Param2009_View(IconsView):
    access = 'is_allowed_to_edit'
    title = MSG(u"Voir")


    def get_namespace(self, resource, context):
        items = []
        for name in sorted(resource.get_names()):
            item = resource.get_resource(name)
            items.append({'icon': '/ui/' + item.class_icon48,
                'title': item.get_title(),
                'description': None,
                'url': context.get_link(item)})
        return {'batch': None, 'items': items}



class Param2009_Import(AutoForm):
    access = 'is_allowed_to_edit'
    title = MSG(u"Importer")
    schema = {'file': FileDataType(mandatory=True)}
    widgets = [FileWidget('file', title=MSG(u"Fichier ODS"))]
    submit_value = MSG(u'Importer')


    def action(self, resource, context, form):
        filename, mimetype, body = form['file']
        if mimetype != ODF_SPREADSHEET:
            context.message = ERROR(u"not an ODS file")
            return
        stringio = StringIO(body)
        document = odf_get_document(stringio)
        assert document.get_type() == 'spreadsheet'
        tables = iter(document.get_body().get_table_list())
        server = context.server
        for name in ('controls', 'schema'):
            table = tables.next()
            table.rstrip_table(aggressive=True)
            table.delete_row(0)
            csv = table.export_to_csv()
            item = resource.get_resource(name)
            try:
                item.handler.load_state_from_string(csv)
                server.change_resource(item)
            except Exception, e:
                context.message = ERROR(unicode(e))
                return
        for table in tables:
            table.rstrip_table(aggressive=True)
            csv = table.export_to_csv()
            page_number, title = table.get_table_name().split(u" ", 1)
            name = 'page%s' % page_number.lower().encode()
            formpage = resource.get_resource(name)
            formpage.set_property('title', title)
            try:
                formpage.handler.load_state_from_string(csv)
            except Exception, e:
                context.message = ERROR(unicode(e))
                return
        context.message = INFO(u"Pages importées")
