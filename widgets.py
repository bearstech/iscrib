# -*- coding: UTF-8 -*-
# Copyright (C) 2005  <jdavid@favela.(none)>
# Copyright (C) 2006 J. David Ibanez <jdavid@itaapy.com>
# Copyright (C) 2006 luis <luis@lucifer.localdomain>
# Copyright (C) 2006-2010 Hervé Cauwelier <herve@itaapy.com>
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
from itools.datatypes import XMLContent, XMLAttribute

# Import from ikaaro

# Import from iscrib
from datatypes import Numeric, Text, EnumBoolean, SqlEnumerate


NBSP = u"\u00a0".encode('utf8')
FIELD_PREFIX = u"#"


def is_mandatory_filled(datatype, name, value, schema, fields, context):
    if context.method != 'POST':
        return True
    if context.resource.is_disabled_by_dependency(name, schema, fields):
        return True
    if not datatype.mandatory:
        return True
    return bool(value)



def make_element(tagname, attributes={}, content=u""):
    element = [u"<", tagname]
    for key, value in attributes.iteritems():
        if isinstance(value, list):
            value = u" ".join(value)
        element.extend((u" ", key, u'="', value, u'"'))
    if tagname == 'input':
        element.extend((u"/>", content))
    else:
        element.extend((u">", content, u"</", tagname, u">"))
    return u"".join(element)



def _choice_widget(context, form, datatype, name, value, schema, fields,
        readonly, input_type):
    html = []

    # True -> '1' ; False -> '2'
    if readonly:
        if datatype.multiple:
            input = u"\n".join(make_element(u"div", content=value)
                for value in datatype.get_values(value))
        else:
            # '1' -> u"Oui" ; '2' -> u"Non"
            data = datatype.encode(value)
            input = datatype.get_value(data, value)
            input = XMLContent.encode(input)
        html.append(make_element(u"div", content=input))
    else:
        for option in datatype.get_namespace(value):
            attributes = {u"type": input_type,
                    u"id": u"field_{name}".format(name=name),
                    u"name": name, u"value": option['name']}
            if option['selected']:
                attributes[u"checked"] = u"checked"
            if form.is_disabled_by_dependency(name, schema, fields):
                attributes[u"disabled"] = u"disabled"
                attributes.setdefault(u"class", []).append(u"disabled")
            # 0005970: Le Javascript pour (dés)activer les autres champs
            if option['name'] == '1':
                disabled = u"false"
                toggle_class = u"removeClass"
            else:
                disabled = u"true"
                toggle_class = u"addClass"
            dep_names = form.get_dep_names(name, schema)
            for dep_name in dep_names:
                attributes.setdefault(u"onchange", []).append(
                    u"$('[name={name}]').attr('disabled', {disabled})"
                    u".{method}('disabled');".format(name=dep_name,
                        disabled=disabled, method=toggle_class))
            # 0005970 fin
            input = make_element(u"input", attributes, option['value'])
            if issubclass(datatype, EnumBoolean):
                # Oui/Non sur une seule ligne
                html.append(input)
            else:
                # Une option par ligne
                html.append(make_element(u"div", content=input))

    attributes = {}
    if name in context.bad_types:
        attributes[u"class"] = u"badtype"
    elif not is_mandatory_filled(datatype, name, value, schema, fields,
            context):
        attributes[u"class"] = u"mandatory"
    return make_element(u"div", attributes, u"".join(html))



def radio_widget(context, form, datatype, name, value, schema, fields,
        readonly):
    return _choice_widget(context, form, datatype, name, value, schema,
            fields, readonly, input_type=u"radio")



def checkbox_widget(context, form, datatype, name, value, schema, fields,
        readonly):
    return _choice_widget(context, form, datatype, name, value, schema,
            fields, readonly, input_type=u"checkbox")



def select_widget(context, form, datatype, name, value, schema, fields,
        readonly):
    if readonly:
        return make_element(u"div", content=datatype.get_value(value, value))

    options = []
    for option in datatype.get_namespace(value):
        attributes = {u"value": option['name']}
        if option['selected']:
            attributes[u"selected"] = u"selected"
        options.append(make_element(u"option", attributes, option['value']))
    options = u"\n".join(options)
    attributes = {u"name": name}
    # Check for "errors"
    if name in context.bad_types:
        attributes[u"title"] = u"Bad value"
        attributes[u"class"] = [u"badtype"]
    elif not is_mandatory_filled(datatype, name, value, schema, fields,
            context):
        attributes[u"title"] = u"Mandatory field"
        attributes[u"class"] = [u"mandatory"]
    if form.is_disabled_by_dependency(name, schema, fields):
        attributes[u"disabled"] = u"disabled"
        attributes.setdefault(u"class", []).append(u"disabled")
    return make_element(u"select", attributes, options)



def textarea_widget(context, form, datatype, name, value, schema, fields,
        readonly):
    if readonly:
        attributes = {u"style": u"white-space: pre", u"class": u"readonly"}
        content = XMLContent.encode(value)
        return make_element(u"div", attributes, content)

    attributes = {u"name": name, u"rows": u"15", u"cols": datatype.length}
    # special case for 'value'
    content = XMLContent.encode(value)
    return make_element(u"textarea", attributes, content)



def text_widget(context, form, datatype, name, value, schema, fields,
        readonly, tabindex=None):
    # Reçoit des int en GET
    if not isinstance(value, basestring):
        value = datatype.encode(value)
    # Reçoit des str en POST
    if not type(value) is unicode:
        value = unicode(value, 'utf8')
    if readonly:
        tagname = u"div"
        attributes = {u"class": [u"readonly"]}
        content = XMLContent.encode(value)
    else:
        tagname = u"input"
        attributes = {u"type": u"text",
                u"id": u"field_{name}".format(name=name),
                u"name": name, u"value": XMLAttribute.encode(value),
                u"size": str(datatype.length),
                u"maxlength": str(datatype.size)}
        if tabindex:
            attributes[u"tabindex"] = tabindex
        content = u""
    # Right-align numeric fields
    if isinstance(datatype, Numeric):
        attributes[u"class"] = [u"num"]
    # Check for errors
    if name in context.bad_types:
        attributes.setdefault(u"class", []).append(u"badtype")
        attributes[u"title"] = u"Bad value"
    elif not is_mandatory_filled(datatype, name, value, schema, fields,
            context):
        attributes.setdefault(u"class", []).append(u"mandatory")
        attributes[u"title"] = u"Mandatory field"
    if form.is_disabled_by_dependency(name, schema, fields):
        attributes[u"disabled"] = u"disabled"
        attributes.setdefault(u"class", []).append(u"disabled")
    return make_element(tagname, attributes, content)



def get_input_widget(name, form, schema, fields, context, tabindex=None,
        readonly=False, skip_print=False):
    # Always take data from the handler, we store wrong values anyway
    value = form.get_form().handler.get_value(name, schema)
    datatype = schema[name]
    widget = None
    if  isinstance(datatype, Numeric):
        widget = text_widget(context, form, datatype, name, value, schema,
                fields, readonly, tabindex)
    elif issubclass(datatype, Text):
        widget = textarea_widget(context, form, datatype, name, value,
                schema, fields, readonly)
    elif issubclass(datatype, SqlEnumerate):
        representation = datatype.representation
        if representation == 'select':
            widget = select_widget(context, form, datatype, name, value,
                    schema, fields, readonly)
        elif representation == 'radio':
            widget = radio_widget(context, form, datatype, name, value,
                    schema, fields, readonly)
        elif representation == 'checkbox':
            widget = checkbox_widget(context, form, datatype, name, value,
                    schema, fields, readonly)
        else:
            ValueError, representation
    else:
        widget = text_widget(context, form, datatype, name, value, schema,
                fields, readonly, tabindex)
    if skip_print is False:
        help = datatype.help
        if help:
            widget += (u'<img src="/ui/icons/16x16/help.png" '
                    u'title="{help}" class="online-help"/>'.format(help=help))
    return widget
