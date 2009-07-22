# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Sylvain Taverne <sylvain@itaapy.com>
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

# Import from itools
from itools.web import STLView

# Import from scrib
from utils import get_bdp, get_bm

# XXX
#edit_password_form__label__ = u'Change password'

class User_Home(STLView):

    access = 'is_self_or_admin'
    title  = u'Home'
    template = '/ui/scrib/User_home.xml'

    def get_namespace(self, resource, context):
        root = context.root
        name = resource.name
        department, code = '', ''
        namespace = {}

        year = resource.get_year()
        if resource.is_BM():
            code = resource.get_BM_code()
            report = root.get_resource('BM%s/%s' % (year, code))
        elif resource.is_BDP():
            department = resource.get_department()
            report = root.get_resource('BDP%s/%s' % (year, department))
        else:
            report = None

        if report is not None:
            namespace['report_url'] = '%s/' % resource.get_pathto(report)
        else:
            namespace['report_url'] = None

        # The year
        namespace['year'] = year
        # The department or the BM Code
        namespace['dep'] = ''
        if department:
            bib = get_bdp(department)
            if bib:
                namespace['dep'] = bib.get_value('name')
        elif code:
            bib = get_bm(code)
            if bib:
                namespace['dep'] = bib.get_value('name')

        return namespace
