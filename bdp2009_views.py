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
from form_views import Form_View
from utils import reduce_generators
from utils_views import HelpView


class Form_BDP_PrintForm(HelpView):

    access = 'is_allowed_to_view'
    title = u'Imprimez votre rapport '
    template = '/ui/scrib/printable_template.xhtml'

    def get_namespace(self, resource, context):
        context.response.set_header('Content-Type',
                                    'text/html; charset=UTF-8')
        namespace = resource.get_namespace(context)
        forms = ['FormBDP_report%s' % i for i in range(0, 10)]
        forms.append('Form_comments')
        forms = [('%s.xml' % i, '%s_autogen.xml' % i, 'print_all')
                 for i in forms]
        forms = [Form_View(xml=n, autogen_xml=a, view=v).GET(resource, context)
                        for n, a, v in forms]
        namespace['body'] = reduce_generators(forms)
        namespace['title'] = resource.get_title()
        namespace['styles'] = context.root.get_skin(context).get_styles(context)
        return namespace
