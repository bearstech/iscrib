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
from itools.csv import CSVFile
from itools.datatypes import String
from itools.gettext import MSG
from itools.web import BaseView, STLForm, INFO, ERROR

# Import from scrib
from datatypes import Numeric, EnumBoolean
from widgets import is_mandatory_filled


# Messages
MSG_ERREUR_SAUVEGARDE = ERROR(u"ATTENTION ! IL Y A DES RUBRIQUES MANQUANTES "
        u"ET/OU INVALIDES")
MSG_SAUVEGARDE = INFO(u"La page est enregistrée, veuillez vérifier votre "
        u"saisie dans l'onglet Contrôle de saisie")


class Form_View(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    query_schema = {'view': String}
    schema = {'page_number': String}


    def get_namespace(self, resource, context):
        try:
            # Return from POST
            bad_types = context.bad_types
        except AttributeError:
            # Fresh GET: not bad yet
            context.bad_types = []
        user = context.user
        skip_print = user.is_voir_scrib()
        view = context.query['view']
        if view == 'printable':
            skip_print = True
        ac = resource.get_access_control()
        readonly = not ac.is_allowed_to_edit(context.user, resource)
        table = resource.get_resource(self.page_template % self.n)
        namespace = table.get_namespace(resource, self, context,
                skip_print=skip_print, readonly=readonly)
        return namespace


    def action(self, resource, context, form):
        page_number = form['page_number']
        handler = resource.handler
        bad_types = []
        for key in handler.pages[page_number]:
            value = ''
            # Can't use "if not/continue" pattern here
            datatype = handler.schema[key]
            if context.has_form_value(key):
                # Do not use form schema, only default String
                data = context.get_form_value(key).strip()
                try:
                    value = datatype.decode(data)
                except Exception:
                    # Keep invalid values
                    value = data
                # Compare sums
                if datatype.sum:
                    expected = handler.sum(datatype, datatype.sum,
                            # Raw form, not the filtered one
                            **context.request.get_form())
                    # Sum inputed
                    if data and value != expected:
                        # What we got was OK so blame the user
                        if expected is not None:
                            bad_types.append(key)
                    # Sum deduced
                    else:
                        # Got it right!
                        if expected is not None:
                            value = expected
                        # Got it wrong!
                        else:
                            bad_types.append(key)
                # Mandatory
                elif datatype.is_mandatory and not data:
                    bad_types.append(key)
                # Invalid (0008102 and mandatory -> and filled)
                elif data and not datatype.is_valid(data):
                    bad_types.append(key)
            # First skip instance datatypes:
            #   TypeError: issubclass() arg 1 must be a class
            elif isinstance(datatype, Numeric):
                pass
            # Now detect unchecked checkboxes
            elif issubclass(datatype, EnumBoolean):
                if not is_mandatory_filled(datatype, key, value, context):
                    bad_types.append(key)
            handler.set_value(key, value)
        # Reindex
        context.server.change_resource(resource)
        # Transmit list of errors when returning GET
        if bad_types:
            context.message = MSG_ERREUR_SAUVEGARDE
            context.bad_types = bad_types
        else:
            context.message = MSG_SAUVEGARDE



class Form_Export(BaseView):
    access = 'is_allowed_to_view'
    title = MSG(u"Téléchargement du rapport")


    def GET(self, resource, context):
        if not resource.is_ready():
            return u"Votre rapport n'est pas encore terminé.".encode('utf8')

        # construct the csv
        csv = CSVFile()
        csv.add_row(["Chapitre du formulaire", "rubrique", "valeur"])
        handler = resource.handler
        schema = handler.schema
        for name, datatype in sorted(schema.iteritems()):
            value = handler.get_value(name)
            try:
                value = datatype.encode(value, 'cp1252')
            except TypeError:
                value = datatype.encode(value)
            if not isinstance(value, str):
                raise "pas encode", str(type(datatype))
            csv.add_row([datatype.pages[0], name, value])

        response = context.response
        response.set_header('Content-Type', 'text/comma-separated-values')
        response.set_header('Content-Disposition',
                'attachment; filename="scrib%s_BM%s.csv"' % (
                    context.site_root.get_property('annee'),
                    resource.get_code_ua()))

        return csv.to_str(separator=';')
