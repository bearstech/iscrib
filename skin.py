# -*- coding: UTF-8 -*-
# Copyright (C) 2007-2008 Hervé Cauwelier <herve@itaapy.com>
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

# Import from itools
from itools.core import get_abspath
from itools.web import get_context

# Import from ikaaro
from ikaaro.skins import Skin, register_skin, map

# Import from scrib
from widgets import UITable
from skin_views import ScribLocationTemplate


class ScribSkin(Skin):
    location_template = ScribLocationTemplate


    def get_styles(self, context):
        styles = [
            # BackOffice style
            '/ui/bo.css',
            # Calendar JS Widget (http://dynarch.com/mishoo/calendar.epl)
            '/ui/js_calendar/calendar-aruni.css',
            # Table
            '/ui/table/style.css',
            # Aruni
            '/ui/aruni/style.css',
            # Scrib
            '/ui/scrib2009/style.css']
        # Dynamic styles
        for style in context.styles:
            styles.append(style)
        return styles


    def get_template(self):
        context = get_context()
        # Marche aussi pour query
        if context.get_form_value('view') == 'printable':
            return self.get_resource('print.xhtml')
        return self.get_resource('template.xhtml')


    def build_namespace(self, context):
        namespace = Skin.build_namespace(self, context)
        app = context.site_root
        namespace['application_title'] = app.get_title()
        namespace['application_address'] = app.get_property('adresse')
        namespace['application_contacts'] = app.get_property('contacts')
        return namespace



#############################################################################
# Register
for mimetype in UITable.class_mimetypes:
    # XXX tous les formats CSV seront lus comme des tables
    # TODO enregistrer ".table.csv" comme ".tar.gz"
    map[mimetype] = UITable
path = get_abspath('ui/scrib2009')
register_skin('scrib2009', ScribSkin(path))
