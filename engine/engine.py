# vim:set et sts=4 sw=4:
#
# ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2007-2012 Peng Huang <shawn.p.huang@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from gi.repository import GLib
from gi.repository import IBus
from gi.repository import Pango

import sqlite3
import string

keysyms = IBus

class EngineUnicodeDb(IBus.Engine):
    __gtype_name__ = 'EngineUnicodeDb'
    
    __literal_mode = True

    def __init__(self):
        super(EngineUnicodeDb, self).__init__()
        self.__is_invalidate = False
        self.__preedit_string = u""
        self.__lookup_table = IBus.LookupTable.new(10, 0, True, True)
        self.__prop_list = IBus.PropList()
        self.__prop_list.append(IBus.Property(key="test", icon="ibus-local"))
        # initialize sqlite
        try:
            self.__dbconn = sqlite3.connect('/home/daniel/ibus-tmpl/data/char_db.s3')
        except sqlite3.OpeationalError:
            self.__dbconn = None
        print "Create EngineUnicodeDb OK"

    def do_process_key_event(self, keyval, keycode, state):
        print "process_key_event(%04x, %04x, %04x)" % (keyval, keycode, state)
        # ignore key release events
        is_press = ((state & IBus.ModifierType.RELEASE_MASK) == 0)
        if not is_press:
            return False
        
        ## todo -- literal mode needs fixing -- must not activate when other keys
        ## have also been activated.
        ## even better -- we can activate when...
        if keyval == keysyms.Shift_L or \
            keyval == keysyms.Shift_R:
            self.__literal_mode = not self.__literal_mode
            if self.__preedit_string:
                self.__invalidate()
                self.__lookup_table.clear()
            return True
        
        if self.__literal_mode:
            return False

        if self.__preedit_string:
            if keyval == keysyms.Return:
                self.__commit_string(self.__preedit_string)
                return True
            elif keyval == keysyms.Escape:
                self.__preedit_string = u""
                self.__update()
                return True
            elif keyval == keysyms.BackSpace:
                self.__preedit_string = self.__preedit_string[:-1]
                self.__invalidate()
                return True
#            elif keyval == keysyms.space:
#                if self.__lookup_table.get_number_of_candidates() > 0:
#                    self.__commit_string(self.__lookup_table.get_current_candidate().text)
#                else:
#                    self.__commit_string(self.__preedit_string)
#                return False
            elif keyval >= 49 and keyval <= 57:
                #keyval >= keysyms._1 and keyval <= keysyms._9
                index = keyval - 49 #keysyms._1
                length = self.__lookup_table.get_number_of_candidates()
                if index >= length:
                    return False
                candidate = self.__lookup_table.get_candidate(self.__lookup_table.cursor_pos + index)
                # commit only the first character
                self.__commit_string(candidate.text.decode('utf-8')[0].encode('utf-8'))
                return True
            elif keyval == keysyms.Page_Up or keyval == keysyms.KP_Page_Up:
                self.do_page_up()
                return True
            elif keyval == keysyms.Page_Down or keyval == keysyms.KP_Page_Down:
                self.do_page_down()
                return True
            elif keyval == keysyms.Up:
                self.do_cursor_up()
                return True
            elif keyval == keysyms.Down:
                self.do_cursor_down()
                return True
            elif keyval == keysyms.Left or keyval == keysyms.Right:
                return True
        if keyval in xrange(keysyms.a, keysyms.z + 1) or \
            keyval in xrange(keysyms.A, keysyms.Z + 1) or \
            keyval == keysyms.space:
            if state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK) == 0:
                self.__preedit_string += unichr(keyval)
                self.__invalidate()
                return True
        else:
            if keyval < 128 and self.__preedit_string:
                self.__commit_string(self.__preedit_string)

        return False

    def __invalidate(self):
        if self.__is_invalidate:
            return
        self.__is_invalidate = True
        GLib.idle_add(self.__update)


    def do_page_up(self):
        if self.__lookup_table.page_up():
            print "wait i page up"
            print self.__lookup_table.page_size
            print self.__pos
            
            self.__pos = max( self.__pos - self.__lookup_table.page_size, 0) 
            self.__lookup_table.clear()
            
            for candidate in self.__candidates[self.__pos: self.__pos + self.__lookup_table.page_size ]:
                self.__lookup_table.append_candidate(IBus.Text.new_from_string(candidate))
#            self.page_down_lookup_table()
            self.__update_lookup_table()
            return True
        return False

    def do_page_down(self):
        if self.__lookup_table.page_down():
            print "wait i page down"
            print self.__lookup_table.page_size
            print self.__pos
            
            self.__pos = min(self.__pos + self.__lookup_table.page_size, len(self.__candidates) / self.__lookup_table.page_size)
            self.__lookup_table.clear()
            
            for candidate in self.__candidates[self.__pos: self.__pos + self.__lookup_table.page_size ]:
                self.__lookup_table.append_candidate(IBus.Text.new_from_string(candidate))
#            self.page_down_lookup_table()
            self.__update_lookup_table()
            return True
        return False

    def do_cursor_up(self):
        if self.__lookup_table.cursor_up():
#            self.cursor_up_lookup_table()
            return True
        return False

    def do_cursor_down(self):
        if self.__lookup_table.cursor_down():
#            self.cursor_down_lookup_table()
            return True
        return False

    def __commit_string(self, text):
        self.commit_text(IBus.Text.new_from_string(text))
        self.__preedit_string = u""
        self.__update()
        
    __candidates = []
    __pos = 0
        
    def __update(self):
        preedit_len = len(self.__preedit_string)
        attrs = IBus.AttrList()
        self.__lookup_table.clear()
        self.__pos = 0
        self.__candidates=[]
        if preedit_len > 0:
            words = string.split( self.__preedit_string.upper().replace('\'', '\'\''), ' ')
            subqueries = [];
            query = 'SELECT character_desc.character, desc FROM character_desc INNER JOIN ('
            
            for word in words:
                subqueries += [ 'SELECT character FROM character_word WHERE word = \'' + word + '\'' ]
            
            query += string.join( subqueries, ' INTERSECT ')
            query += ')  AS chrs ON character_desc.character = chrs.character';
            
            print query;
        
            cur = self.__dbconn.cursor();
            cur.execute(query)
            
            data = cur.fetchone();
            while (data != None):
                self.__candidates += [ unichr(int(data[0], 16)) + " - \\u" + data[0] + " - " + data[1] ]
                data = cur.fetchone()
            
            for candidate in self.__candidates[0:10]:
                self.__lookup_table.append_candidate(IBus.Text.new_from_string(candidate))
                
        text = IBus.Text.new_from_string(self.__preedit_string)
        text.set_attributes(attrs)
        self.update_auxiliary_text(text, preedit_len > 0)

        attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE,
                IBus.AttrUnderline.SINGLE, 0, preedit_len))
        text = IBus.Text.new_from_string(self.__preedit_string)
        text.set_attributes(attrs)
        self.update_preedit_text(text, preedit_len, preedit_len > 0)
        self.__update_lookup_table()
        self.__is_invalidate = False

    def __update_lookup_table(self):
        visible = self.__lookup_table.get_number_of_candidates() > 0
        self.update_lookup_table(self.__lookup_table, visible)


    def do_focus_in(self):
        print "focus_in"
        self.register_properties(self.__prop_list)

    def do_focus_out(self):
        print "focus_out"

    def do_reset(self):
        print "reset"

    def do_property_activate(self, prop_name):
        print "PropertyActivate(%s)" % prop_name

