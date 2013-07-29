# vim:set et sts=4 sw=4:
#
# ibus-unicode-db - Unicode DB input method for IBus
#
# Using source code derived from
#   ibus-tmpl - The Input Bus template project
#
# Copyright (c) 2013 Daniel Sim <daniel.ssq89@gmail.com>
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

import string
import stat

from dataparse import DataParse

keysyms = IBus

class EngineUnicodeDb(IBus.Engine):
    __gtype_name__ = 'EngineUnicodeDb'
    
    
    __state = 0   # 0 -- literal mode, 1 -- ambiguous mode, 2 -- normal mode, 3 -- hex mode

    def __init__(self):
        super(EngineUnicodeDb, self).__init__()
        self.__is_invalidate = False
        self.__preedit_string = u""
        self.__lookup_table = IBus.LookupTable.new(10, 0, True, True)
        self.__prop_list = IBus.PropList()
        self.__prop_list.append(IBus.Property(key="test", icon="ibus-local"))
        
        # initialize mmap
        self.__data = DataParse()
        
        print "Create EngineUnicodeDb OK"

    def do_process_key_event(self, keyval, keycode, state):
#        print "process_key_event(%04x, %04x, %04x)" % (keyval, keycode, state)
        # ignore key release events
        is_press = ((state & IBus.ModifierType.RELEASE_MASK) == 0)
        if not is_press:
            return False
        
        ## todo -- literal mode needs fixing -- must not activate when other keys
        ## have also been activated.
        ## even better -- we can activate on... Ctrl+Shift+U
        if self.__state == 0:
            if state & IBus.ModifierType.CONTROL_MASK != 0 &&
            state & IBus.ModifierType.SHIFT_MASK != 0 and \
                keyval == keysyms.u or keyval == keysyms.U:
                self.__preedit_string = 'u'
                self.__state = 1        # ambiguous hex/desc mode
                self.__update()
                return True
            return False
        elif self.__state == 1 and keyval == keysyms.apostrophe: # transition to description
            ## TODO: preedit string should show: u'
            self.__preedit_string += '\''
            self.__state = 2
            self.__update()
            return True
        elif self.__state == 1 or self.__state == 3:
            ## TODO: handle the hex state
            if  state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK) != 0 and \
                (keyval >= keysyms.a and keyval <= keysyms.f) or \
                (keyval >= keysyms.A and keyval <= keysyms.F) or \
                (keyval >= 48 and keyval <= 57):  # transition to confirmed hex state
                self.__state = 3
            return self.handle_hex_state( keyval, state )
        elif self.__state == 2: # description state
            return self.handle_desc_state( keyval, state )
            
        return False
            
    def handle_hex_state(self, keyval, state):
    
        if state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK) != 0:
            return False
        
        if keyval == keysyms.Escape:
            self.__preedit_string = u""
            self.__state = 0
            self.__update()
            return True
        elif keyval == keysyms.BackSpace:
            self.__preedit_string = self.__preedit_string[:-1]
            self.__update()
            if len(self.__preedit_string) == 0:
                self.__state = 0
            return True  
        elif keyval == keysyms.Return or \
            keyval == keysyms.space: # commit the character
            self.__state = 0
            self.__commit_string( unichr(int(self.__preedit_string[1:], 16)) )
            self.__preedit_string = u''
            self.__update()
            return True
        elif (keyval >= keysyms.a and keyval <= keysyms.f) or \
            (keyval >= keysyms.A and keyval <= keysyms.F) or \
            (keyval >= 48 and keyval <= 57): # hex char
            
            # if passed as a control sequence e.g. Ctrl + F
            if len(self.__preedit_string) > 8:
                pass
            else:
                self.__preedit_string += chr(keyval)            
                self.__update()
            
            return True            
        
        return False
    
    def handle_desc_state(self, keyval, state):
        if self.__preedit_string:
            if keyval == keysyms.Return:
                self.__state = 0
                self.__commit_string(self.__preedit_string)
                return True
            elif keyval == keysyms.Escape:
                self.__preedit_string = u""
                self.__state = 0
                self.__update()
                return True
            elif keyval == keysyms.BackSpace:
                self.__preedit_string = self.__preedit_string[:-1]
                if len(self.__preedit_string) < 2:
                    self.__preedit_string = u''
                    self.__state = 0
                self.__invalidate()
                return True
#            elif keyval == keysyms.space:
#                if self.__lookup_table.get_number_of_candidates() > 0:
#                    self.__commit_string(self.__lookup_table.get_current_candidate().text)
#                else:
#                    self.__commit_string(self.__preedit_string)
#                return False
            elif keyval >= 49 and keyval <= 57 and \
                len(self.__preedit_string) > 2:
                #keyval >= keysyms._1 and keyval <= keysyms._9
                index = keyval - 49 #keysyms._1
                length = self.__lookup_table.get_number_of_candidates()
                if index >= length:
                    return False
                candidate = self.__lookup_table.get_candidate(index)
                # commit only the first character
                self.__state = 0
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
        if keyval < 128 and self.__preedit_string:
            if state & (IBus.ModifierType.CONTROL_MASK | IBus.ModifierType.MOD1_MASK) == 0:
                self.__preedit_string += unichr(keyval)
                self.__invalidate()
                return True

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
        self.__state = 0
        
    __candidates = []
    __pos = 0
        
    def __update(self):
        preedit_len = len(self.__preedit_string)
        attrs = IBus.AttrList()
        self.__lookup_table.clear()
        self.__pos = 0
        self.__candidates=[]
        
        if preedit_len > 2 and self.__state == 2:
            words = string.split( self.__preedit_string[2:].strip().upper().replace('\'', '\'\''), ' ')
            
            (cands, fuz_cands) = self.__data.find_candidates(words)
            sort_func = lambda x: int(x, 16)
            candidate_codes = sorted(list(cands), key=sort_func) + \
                            sorted(list(fuz_cands), key=sort_func)
            
            for code in candidate_codes:
                self.__candidates += [ unichr(int(code, 16)) + " - \\u" + code + \
                    " - " + self.__data.find_description(code) ]
            
            for candidate in self.__candidates[0:10]:
                self.__lookup_table.append_candidate(IBus.Text.new_from_string(candidate))
        elif preedit_len > 1 and (self.__state == 1 or self.__state == 3):
            pass
                
        text = IBus.Text.new_from_string(self.__preedit_string)
        text.set_attributes(attrs)
        self.update_auxiliary_text(text, self.__state == 2 and preedit_len > 0)

        attrs.append(IBus.Attribute.new(IBus.AttrType.UNDERLINE,
                IBus.AttrUnderline.SINGLE, 0, preedit_len))
        text = IBus.Text.new_from_string(self.__preedit_string)
        text.set_attributes(attrs)
        self.update_preedit_text(text, preedit_len, preedit_len > 0)
        self.__update_lookup_table()
        self.__is_invalidate = False
        

    def __update_lookup_table(self):
        if self.__state == 2:
            visible = self.__lookup_table.get_number_of_candidates() > 0
            self.update_lookup_table(self.__lookup_table, visible)
        else:
            print 'hiding the lookup table?'
            self.hide_lookup_table()

    def do_focus_in(self):
        print "focus_in"
        self.register_properties(self.__prop_list)

    def do_focus_out(self):
        print "focus_out"

    def do_reset(self):
        print "reset"

    def do_property_activate(self, prop_name):
        print "PropertyActivate(%s)" % prop_name
        
        
