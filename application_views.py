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
from itools.database import PhraseQuery
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.folder_views import Folder_BrowseContent

# Import from iscrib
from param import Param


class Application_BrowseContent(Folder_BrowseContent):
    access = 'is_allowed_to_edit'
    template = '/ui/iscrib/application/view.xml'
    title = MSG(u"View")
    search_template = None

    table_columns = [
            ('form', MSG(u"Application")),
            ('file', MSG(u"Source ODS File")),
            ('ctime', MSG(u"Creation Date"))]
    table_actions = []


    def get_page_title(self, resource, context):
        return None


    def get_namespace(self, resource, context):
        return merge_dicts(super(Application_BrowseContent,
            self).get_namespace(resource, context),
            homepage=resource.get_property('homepage'))


    def get_items(self, resource, context, *args):
        return super(Application_BrowseContent, self).get_items(resource,
                context, PhraseQuery('format', Param.class_id), *args)


    def sort_and_batch(self, resource, context, results):
        start = context.query['batch_start']
        size = context.query['batch_size']
        sort_by = context.query['sort_by']
        reverse = context.query['reverse']
        items = results.get_documents(sort_by=sort_by, reverse=reverse,
                                      start=start, size=size)

        # FIXME This must be done in the catalog.
        if sort_by == 'title':
            items.sort(cmp=lambda x,y: cmp(x.title, y.title))
            if reverse:
                items.reverse()

        # Access Control (FIXME this should be done before batch)
        user = context.user
        root = context.root
        allowed_items = []
        for item in items:
            resource = root.get_resource(item.abspath)
            # On regarde mais sans toucher
            #ac = resource.get_access_control()
            #if ac.is_allowed_to_view(user, resource):
            allowed_items.append((item, resource))

        return allowed_items


    def get_item_value(self, resource, context, item, column):
        brain, item_resource = item
        if column == 'form':
            return brain.title, brain.name
        elif column == 'file':
            parameters = item_resource.get_resource('parameters')
            return (parameters.get_property('filename') or u"Source",
                    '%s/;download' % context.get_link(parameters))
        elif column == 'ctime':
            return context.format_datetime(brain.ctime)
        return super(Application_BrowseContent,
                self).get_item_value(resource, context, item, column)
