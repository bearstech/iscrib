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
from itools.core import merge_dicts
from itools.datatypes import String, Integer, Boolean, Unicode
from itools.gettext import MSG
from itools.stl import set_prefix
from itools.web import BaseView, STLForm, ERROR

# Import from ikaaro
from ikaaro.access import is_admin
from ikaaro.forms import TextWidget, BooleanRadio, MultilineWidget
from ikaaro.messages import MSG_NEW_RESOURCE
from ikaaro.resource_views import DBResource_Edit
from ikaaro.views_new import NewInstance

# Import from scrib
from form_views import Form_View
from utils import get_adresse_bm, get_adresse_bdp


class Base2009Form_View(Form_View):
    template = '/ui/scrib2009/Table_to_html.xml'
    page_template = '/ui/scrib2009/bm/Page%s.table.csv'


    def get_scrib_menu(self, resource, context):
        raise NotImplementedError


    def get_namespace(self, resource, context):
        namespace = Form_View.get_namespace(self, resource, context)
        namespace['menu'] = self.get_scrib_menu(resource, context)
        return namespace


    def action(self, resource, context, form):
        Form_View.action(self, resource, context, form)
        resource.set_property('is_first_time', False)



class Base2009Form_Send(STLForm):
    access = 'is_allowed_to_view'
    access_POST = 'is_allowed_to_edit'
    template = '/ui/scrib2009/Base2009Form_send.xml'
    title = MSG(u"Contrôle de saisie")
    query_schema = {'view': String}


    def get_namespace(self, resource, context):
        namespace = {}
        namespace['first_time'] = first_time = resource.is_first_time()
        # Errors
        errors = []
        warnings = []
        infos = []
        # Invalid fields
        for name, datatype in resource.get_invalid_fields():
            if datatype.sum:
                title = u"%s n'est pas égal à %s" % (name, datatype.sum)
            else:
                title = u"%s non valide" % name
            info = {'number': name,
                    'title': title,
                    'href': ';page%s#field_%s' % (datatype.pages[0], name),
                    'debug': str(type(datatype))}
            if datatype.is_mandatory:
                errors.append(info)
            else:
                warnings.append(info)
        # Failed controls
        for control in resource.get_failed_controls():
            control['href'] = ';page%s#field_%s' % (control['page'],
                    control['title'].split()[0])
            if control['level'] == '2':
                errors.append(control)
            else:
                warnings.append(control)
        # Informative controls
        for control in resource.get_info_controls():
            control['href'] = ';page%s#field_%s' % (control['page'],
                    control['title'].split()[0])
            infos.append(control)
        namespace['controls'] = {'errors': errors, 'warnings': warnings,
                'infos': infos}
        # ACLs
        user = context.user
        namespace['is_admin'] = is_admin(user, resource)
        # Workflow - State
        namespace['statename'] = statename = resource.get_statename()
        namespace['form_state'] = resource.get_form_state()
        # Workflow - Transitions
        namespace['can_send'] = statename == 'private' and not errors
        namespace['can_export'] = not errors
        # Debug
        namespace['debug'] = context.has_form_value('debug')
        # Print
        namespace['skip_print'] = False
        view = context.query['view']
        if view == 'printable' or user.is_voir_scrib():
            namespace['skip_print'] = True
        return namespace


    def action_send(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire est soumis.
        """
        raise NotImplementedError


    def action_export(self, resource, context, form):
        """Ce qu'il faut faire quand le formulaire est exporté.
        """
        raise NotImplementedError



class Base2009Form_Edit(DBResource_Edit):
    access = 'is_admin'
    schema = merge_dicts(DBResource_Edit.schema,
            code_ua=Integer(mandatory=True),
            departement=String(mandatory=True),
            is_first_time=Boolean(mandatory=True),
            content=String(mandatory=True))
    widgets = (DBResource_Edit.widgets
            + [TextWidget('code_ua', title=MSG(u"Code UA")),
                TextWidget('departement', title=MSG(u"Département")),
                BooleanRadio('is_first_time', title=MSG(u"Formulaire vide")),
                MultilineWidget('content', cols=100, rows=20,
                    title=MSG(u"Contenu brut /!\\ DANGEREUX /!\\ Toujours "
                        u"insérer une liste complète"))])


    def get_value(self, resource, context, name, datatype):
        if name == 'content':
            return resource.handler.to_str()
        return DBResource_Edit.get_value(self, resource, context, name, datatype)


    def action(self, resource, context, form):
        DBResource_Edit.action(self, resource, context, form)
        if not context.edit_conflict:
            resource.set_property('code_ua', form['code_ua'])
            resource.set_property('departement', form['departement'])
            resource.set_property('is_first_time', form['is_first_time'])
            resource.handler.load_state_from_string(form['content'])



class Base2009Form_New(NewInstance):
    title = MSG(u"Nouvelle bibliothèque")
    schema = merge_dicts(NewInstance.schema, title=Unicode(mandatory=True),
            code_ua=Integer(mandatory=True),
            departement=Integer(mandatory=True))
    widgets = [TextWidget('title', title=MSG(u"Nom de la ville")),
            TextWidget('code_ua', title=MSG(u"Code UA")),
            TextWidget('departement', title=MSG(u"Département"))]


    def action(self, resource, context, form):
        code_ua = form['code_ua']
        name = str(code_ua)
        app = context.site_root
        year = app.get_year_suffix()
        if resource.is_bm():
            get_adresse = get_adresse_bm
        else:
            get_adresse = get_adresse_bdp
        kw = get_adresse(code_ua, 'adresse%s' % year, context=context)
        if resource.is_bm():
            cls = app.bm_class
            kw['A100'] = code_ua
        else:
            cls = app.bdp_class
            kw = {'0': code_ua}
        handler = cls.class_handler(**kw)
        try:
            cls.make_resource(cls, resource, name, body=handler.to_str(),
                    code_ua=code_ua, departement=str(form['departement']),
                    title={'fr': form['title']})
        except RuntimeError, e:
            if str(e).endswith('busy.'):
                context.message = ERROR(u"Code UA déjà pris")
                return
            raise
        return context.come_back(MSG_NEW_RESOURCE, goto='./%s/' % name)



class Base2009Form_Help(BaseView):
    access = 'is_allowed_to_view'
    title = MSG(u"Aide à la saisie")


    def GET(self, resource, context):
        page = context.get_query_value('page')
        app = context.site_root
        if page:
            # Aide spécifique
            response = context.response
            response.set_header('Content-Type', 'text/html; charset=UTF-8')
            if resource.is_bm():
                folder = app.get_resource('aide_bm')
            else:
                folder = app.get_resource('aide_bdp')
            resource = folder.get_resource('Page' + page)
            return resource.handler.to_str()
        # Aide générale
        resource = app.get_resource('aide')
        prefix = resource.get_pathto(resource)
        return set_prefix(resource.get_html_data(), prefix)
