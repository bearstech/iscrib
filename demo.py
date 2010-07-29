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
from itools.datatypes import String, DateTime
from itools.database import PhraseQuery
from itools.gettext import MSG
from itools.web import INFO

# Import from ikaaro
from ikaaro.root import Root
from ikaaro.folder_views import Folder_BrowseContent

# Import from iscrib
from form import Form
from form_views import Form_View, Form_Send
from param import Param
from utils import get_page_number


class ParamForm_Send(Form_Send):

    def get_namespace(self, resource, context):
        # FIXME
        namespace = Form_Send.get_namespace(self, resource, context)
        namespace['first_time'] = resource.is_first_time()
        return namespace


    def action_send(self, resource, context, form):
        message = INFO(u"Votre rapport a bien été envoyé.")
        context.message = message


    def action_export(self, resource, context, form):
        message = INFO(u"Votre rapport a bien été exporté.")
        context.message = message



class ParamForm(Param, Form):
    class_id = 'Param'
    class_title = MSG(u"Application de collecte")
    class_views = ['pageA'] + Form.class_views
    class_schema = merge_dicts(Form.class_schema, Param.class_schema,
            author=String(source='metadata', indexed=False, stored=True),
            ctime=DateTime(source='metadata', indexed=False, stored=True))

    # Views
    envoyer = ParamForm_Send()


    def __getattr__(self, name):
        page_number = get_page_number(name)
        page = self.get_formpage(page_number)
        if page is None:
            return super(ParamForm, self).__getattr__(name)
        hidden_fields = ['A100', 'A200'] if name == 'pageA' else []
        view = Form_View(page_number=page.get_page_number(),
                hidden_fields=hidden_fields,
                title=MSG(u"Commencer la saisie"))
        # TODO make it lazy
        self.__dict__[name] = view
        return view


    def get_form_handler(self):
        return self.get_resource('0').handler


    def is_ready(self):
        return self.get_workflow_state() == 'pending'


    def get_catalog_values(self):
        author = (self.get_property('author')
                or self.get_property('last_author'))
        ctime = self.get_property('ctime') or self.get_property('mtime')
        return merge_dicts(Param.get_catalog_values(self),
                Form.get_catalog_values(self), author=author, ctime=ctime)




class Root_BrowseContent(Folder_BrowseContent):
    template = '/ui/iscrib/root_view.xml'
    title = MSG(u"Voir")

    table_columns = [
            ('form', MSG(u"Formulaire")),
            ('file', MSG(u"Fichier")),
            ('author', MSG(u"Auteur")),
            ('ctime', MSG(u"Date de création"))]
    table_actions = []

    search_schema = merge_dicts(Folder_BrowseContent.search_schema,
            search_type=String(default=ParamForm.class_id))


    def get_items(self, resource, context, *args):
        return Folder_BrowseContent.get_items(self, resource, context,
                PhraseQuery('format', ParamForm.class_id), *args)


    def get_item_value(self, resource, context, item, column):
        brain, item_resource = item
        if column == 'form':
            return brain.title, brain.name
        elif column == 'file':
            ods = item_resource.get_resource('parameters')
            return (ods.get_property('filename'),
                    '%s/parameters/;download' % brain.name)
        elif column == 'author':
            author =  brain.author
            return context.root.get_user_title(author) if author else None
        elif column == 'ctime':
            return context.format_datetime(brain.ctime)
        return Folder_BrowseContent.get_item_value(self, resource, context,
                item, column)



Root.view = Root_BrowseContent()
