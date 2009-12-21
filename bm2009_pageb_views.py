# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Hervé Cauwelier <herve@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library

# Import from itools
from itools.datatypes import String, Integer, Boolean, Unicode
from itools.gettext import MSG
from itools.handlers import checkid
from itools.web import INFO, ERROR

# Import from ikaaro
from ikaaro.buttons import RemoveButton
from ikaaro.folder_views import Folder_BrowseContent, GoToSpecificDocument

# Import from scrib
from bm2009_views import BMForm_View


class PageB_View(Folder_BrowseContent):
    template = '/ui/scrib2009/BM2009_PageB.xml'
    query_schema = {'view': String,
                    'batch_start': Integer(default=0),
                    'batch_size': Integer(default=0),
                    'sort_by': String,
                    'reverse': Boolean(default=False)}
    schema = {'page_number': String,
              'ids': String(multiple=True)}
    table_columns = [('checkbox', None),
                     ('icon', None),
                     ('title', MSG(u'Nom')),
                     ('mtime', MSG(u'Dernière modification'))]
    table_actions = [RemoveButton]
    context_menus = []


    def get_items(self, resource, context, *args):
        pageb = resource.get_pageb()
        return Folder_BrowseContent.get_items(self, pageb, context, *args)


    def get_item_value(self, resource, context, item, column):
        value = Folder_BrowseContent.get_item_value(self, resource, context,
                item, column)
        if column == 'title':
            brain, item_resource = item
            href = '%s/' % context.get_link(item_resource)
            value = value, href
        return value


    def get_namespace(self, resource, context):
        namespace = Folder_BrowseContent.get_namespace(self, resource,
                context)
        namespace.update(BMForm_View(n=self.n).get_namespace(resource,
            context))
        return namespace


    def action_add(self, resource, context, form):
        pageb = resource.get_pageb(make=True)
        title = context.get_form_value('B101', type=Unicode).strip()
        name = checkid(title)
        if not name:
            context.commit = False
            context.message = ERROR(u"Le nom est obligatoire pour commencer "
                    u"à saisir une bibliothèque")
            return
        elif pageb.get_resource(name, soft=True) is not None:
            context.commit = False
            context.message = ERROR(u"Bibliothèque déjà enregistrée.")
            return
        from bm2009_pageb import BM2009Form_PageB
        bib = BM2009Form_PageB.make_resource(BM2009Form_PageB, pageb, name,
                title={'fr': title})
        BMForm_View(n=self.n).action(bib, context, form)
        context.bad_types = []
        context.message = INFO(u"Bibliothèque ajoutée")


    def action_remove(self, resource, context, form):
        pageb = resource.get_pageb()
        Folder_BrowseContent().action_remove(pageb, context, form)



class GoToBM2009Form(GoToSpecificDocument):

    def get_specific_document(self, resource, context):
        return '../%s/;pageB' % resource.get_code_ua()
