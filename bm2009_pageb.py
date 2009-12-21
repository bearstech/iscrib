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
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class

# Import from scrib
from bm2009 import BM2009Form
from bm2009_views import BM2009Form_View
from bm2009_pageb_views import GoToBM2009Form
from form import MultipleForm


class MultipleForm_PageB(MultipleForm):
    class_id = 'MultipleForm_PageB'
    class_views = ['view']

    # Views
    view = GoToBM2009Form()


    ######################################################################
    # Security
    def is_bm(self):
        return self.parent.is_bm()


    def get_code_ua(self):
        name = self.name.replace('-pageb', '')
        return self.parent.get_resource(name).get_code_ua()



class BM2009Form_PageB(BM2009Form):
    class_id = 'BM2009_PageB'
    class_views = ['pageB']

    # Views
    pageB = BM2009Form_View(title=MSG(u"saisie de bibliothèque"), n='B')


    def get_title(self, language=None):
        return self.handler.get_value('B101') or self.name


    ######################################################################
    # Security
    def is_bm(self):
        return self.parent.is_bm()


    def get_code_ua(self):
        return self.parent.get_code_ua()


    ######################################################################
    # API
    def get_invalid_fields(self):
        for result in BM2009Form.get_invalid_fields(self, pages=['B'],
                exclude=[]):
            yield result


    def get_failed_controls(self):
        for result in BM2009Form.get_failed_controls(self, pages=['B'],
                exclude=[]):
            yield result


    ######################################################################
    # Workflow
    def get_statename(self):
        return self.parent.get_statename()


    def get_state(self):
        return self.parent.get_state()


    def do_trans(self, transname, *args, **kw):
        raise NotImplementedError



###########################################################################
# Register
register_resource_class(MultipleForm_PageB)
register_resource_class(BM2009Form_PageB)
