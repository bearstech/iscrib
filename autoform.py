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

# Import from standard library
import urllib, urllib2

# Import from itools
from itools.datatypes import String, PathDataType
from itools.gettext import MSG
from itools.uri import Path
from itools.web import get_context
from itools.xml import XMLParser

# Import from ikaaro
from ikaaro.autoform import ImageSelectorWidget as BaseImageSelectorWidget
from ikaaro.autoform import Widget, make_stl_template, stl_namespaces
from ikaaro.file import Image

# Import from iscrib


# Shamelessly taken from shop.datatypes
class ImagePathDataType(PathDataType):
    """
    -> We check that the path correspond to an image
    -> Default value is 'None' not '.'.
    """

    default = None

    @staticmethod
    def is_valid(value):
        if not value:
            return True
        context = get_context()
        resource = context.resource
        image = resource.get_resource(value, soft=True)
        if image is None:
            return False
        if not isinstance(image, Image):
            return False
        return True


    @staticmethod
    def decode(value):
        if not value:
            return ''
        return Path(value)


    @staticmethod
    def encode(value):
        if not value:
            return ''
        return str(value)



# TODO move to Widget or CMSTemplate
class MultilingualWidget(Widget):

    def get_template(self):
        # Get the template
        template = self.template
        if template is None:
            msg = "%s is missing the 'template' variable"
            raise NotImplementedError, msg % repr(self)

        return make_stl_template(template.gettext().encode('utf8'))



# TODO merge with shop or ikaaro
class ImageSelectorWidget(MultilingualWidget, BaseImageSelectorWidget):
    template = MSG(u"""
    <input type="text" id="selector-${id}" size="${size}" name="${name}"
      value="${value}" />
    <button id="selector-button-${id}" class="button-selector"
      name="selector_button_${name}"
      onclick="return popup(';${action}?target_id=selector-${id}&amp;mode=input', 640, 480);">Browse...</button>
    <button id="erase-button-${id}" class="button-delete"
    name="erase_button_${name}"
      onclick="$('#selector-${id}').attr('value', ''); return false">Erase</button>
    <br/>
    ${workflow_state}
    <br/>
    <img src="${value}/;thumb?width=${width}&amp;height=${height}"
    stl:if="value"/>""")



# TODO reuse shop modules
class RecaptchaDatatype(String):
    # XXX hardcoded
    private_key = '6LehLb4SAAAAAAfRGDvbQ4BQ270UGE82WFOWuf8o'

    @classmethod
    def is_valid(cls, value):
        context = get_context()
        remote_ip = context.get_remote_ip() or '127.0.0.1'
        # Get Captcha fields
        recaptcha_challenge_field = context.get_form_value(
            'recaptcha_challenge_field', type=String)
        recaptcha_response_field = context.get_form_value(
            'recaptcha_response_field', type=String)
        # Test if captcha value is valid
        params = urllib.urlencode({
            'privatekey': cls.private_key,
            'remoteip' :  remote_ip,
            'challenge':  recaptcha_challenge_field,
            'response' :  recaptcha_response_field})

        request = urllib2.Request(
                url="http://api-verify.recaptcha.net/verify",
                data=params,
                headers={
                    'Content-type': "application/x-www-form-urlencoded",
                    'User-agent': "reCAPTCHA Python"})
        httpresp = urllib2.urlopen(request)
        return_values = httpresp.read().splitlines ();
        httpresp.close();
        return_code = return_values[0]
        return return_code == 'true'



# TODO reuse shop modules
class RecaptchaWidget(Widget):
    # XXX hardcoded
    public_key = '6LehLb4SAAAAANVJcthfw9cBR-G5SZfw7i2fFEU3'
    theme = ('red', 'white', 'blackglass', 'clean')

    template = list(XMLParser(
        """
        <input type="hidden" name="${name}" value="Check"/>
        <script type="text/javascript">
        var RecaptchaOptions = {
          theme : '${theme}'
        };
        </script>
        <script type="text/javascript"
            src="http://api.recaptcha.net/challenge?k=${public_key}"/>
        <noscript>
          <iframe src="http://api.recaptcha.net/noscript?k=${public_key}"
              height="300" width="500" frameborder="0"/><br/>
          <textarea name="recaptcha_challenge_field" rows="3" cols="40"/>
          <input type='hidden' name='recaptcha_response_field'
              value='manual_challenge'/>
        </noscript>
        """,
        stl_namespaces))


    def get_namespace(self, datatype, value):
        context = get_context()
        return {'name': self.name,
                'public_key': self.public_key,
                'theme': self.theme}
