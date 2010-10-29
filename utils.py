# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Luis Belmar Letelier <luis@itaapy.com>
# Copyright (C) 2008-2010 Hervé Cauwelier <herve@itaapy.com>
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

# Import from the Standard Library
from socket import gethostname

# Import from itools

# Import from ikaaro

# Import from iscrib


# XXX heuristic
def is_production():
    return gethostname() == 'fidel'


class ProgressMeter(object):
    last_percent = 0

    def __init__(self, max):
        self.max = max


    def show(self, i):
        percent = i * 100 / self.max
        if percent % 10 == 0 and percent != self.last_percent:
            print "  %s %%" % percent
            self.last_percent = percent



def get_page_number(name):
    try:
        _, page_number = name.split('page')
    except ValueError:
        return None
    return page_number.upper()



def SI(condition, iftrue, iffalse=True):
    if condition:
        value = iftrue
    else:
        value = iffalse
    return value



def parse_control(title):
    """Découpe le titre du contrôle pour remplacer les patterns du type ::

        « A123 : mauvaise valeur [A123] »

    par ::

        « A123 : mauvaise valeur [toto] »
    """
    generator = enumerate(title)
    end = 0
    for start, char in generator:
        if char == u'[':
            yield False, title[end:start+1]
            for end, char2 in generator:
                if char2 == u']':
                    yield True, title[start + 1:end]
                    break
    yield False, title[end:]
