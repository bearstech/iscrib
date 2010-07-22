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

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.folder_views import GoToSpecificDocument

# Import from iscrib
from form import Form
from form_views import Form_View
from param import Param
from utils import get_page_number


class ParamForm(Param, Form):
    class_id = 'Param'
    
    # Views
    view = GoToSpecificDocument(specific_document='.', specific_view='pageA')


    def __getattr__(self, name):
        print "ParamForm.__getattr__", name
        page_number = get_page_number(name)
        print "page_number", page_number
        page = self.get_formpage(page_number)
        if page is None:
            print "pas une page"
            return super(ParamForm, self).__getattr__(name)
        view = Form_View(page_number=page.get_page_number(),
                title=page.get_title())
        print "view", view
        # TODO make it lazy
        self.__dict__[name] = view
        return view


    def get_form_handler(self):
        return self.get_resource('0').handler



register_resource_class(ParamForm)
