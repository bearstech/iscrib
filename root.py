# -*- coding: UTF-8 -*-
# Copyright (C) 2006-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2006-2008 ALPantin  <anne-laure.pantin@culture.gouv.fr>
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
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.root import Root as BaseRoot

# Import from scrib
from scrib2009 import Scrib2009


class Root(BaseRoot):
    class_id = 'Culture'
    class_title = MSG(u"Ministère de la Culture / Scrib")

    __fixed_handlers__ = BaseRoot.__fixed_handlers__ + [
            # Ajouter ici les applications/années successives
            'Scrib2009']


    # Skeleton
    @staticmethod
    def _make_resource(cls, folder, email, password):
        assert '@' in email
        root = BaseRoot._make_resource(cls, folder, email, password)
        # La première application/année créée en dur
        # Les suivantes devront être ajoutées depuis l'interface
        Scrib2009._make_resource(Scrib2009, folder, 'Scrib2009')
        return root



register_resource_class(Root)
