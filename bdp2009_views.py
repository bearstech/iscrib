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

# Import from scrib
from base2009_views import Base2009Form_View, Base2009Form_Send


class BDP2009Form_View(Base2009Form_View):
    page_template = '/ui/scrib2009/bdp/Page%s.table.csv'


    def get_scrib_menu(self, resource, context):
        menu = []
        code_ua = resource.get_code_ua()
        form = context.site_root.get_resource('bdp/%s' % code_ua)
        for name, title in [('page0', u"Identité"),
                            ('pageA', u"A-Finances"),
                            ('pageB', u"B-Locaux"),
                            ('pageC', u"C-Personnel"),
                            ('pageD', u"D-Collections"),
                            ('pageE', u"E-Acquisitions"),
                            ('pageF', u"F-Réseau tout public"),
                            ('pageG', u"G-Réseau spécifique"),
                            ('pageH', u"H-Services"),
                            ('pageI', u"I-Actions culturelles"),
                            ('pageL', u"L-Commentaires")]:
            menu.append({'href': '%s/;%s' % (context.get_link(form), name),
                         'title': title,
                         'active': 'nav-active' if context.view_name == name
                                                else None})
        return menu



class BDP2009Form_Send(Base2009Form_Send):
    pass
