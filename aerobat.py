#!/usr/bin/env python2

'''
Aerobat - a simple battery application for the system tray

Copyright (C) 2014  Christian Zommerfelds

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import gtk
import math
import time
import gobject
import subprocess

# icon dimension
width = 12
height = 18
border = 1

# battery level thresholds for color changes
low_threshold      = 0.3
critical_threshold = 0.1

# colors           0xRRGGBBAA
border_color     = 0x000000ff # color of the border
background_color = 0x333333ff # color of the empty part of the battery 
normal_color     = 0x33ff00ff # color of the "energy" bar (normal state)
low_color        = 0xffbf00ff # color of the "energy" bar (low state)
critical_color   = 0xff0000ff # color of the "energy" bar (critical state)
disabled_color   = 0xaaaaaaff # color of battery when no data is availlable

sleep = 5 # the number of seconds to sleep between every refresh

assert width > 2*border
assert height > 2*border

# Returns a tuple containing the battery level between 0.0 and 1.0 (or None) and a more verbose text
def get_battery_level():
    p = subprocess.Popen(['acpi', '-b'], stdout=subprocess.PIPE)
    text = "".join(p.stdout.readlines()).strip()
    p.stdout.close()

    i = text.find("%")
    value = 0
    if (i != -1):
        try:
            percent = int(text[i-3:i])
        except ValueError:
            value = None
        else:
            value = percent/100.0
    else:
        value = None
        text = "No battery data availlable"
        
    return value, text

def gen_pixbuf(color, w, h):
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, has_alpha=True,
                            bits_per_sample=8, width=w, height=h)
    pixbuf.fill(color)
    return pixbuf
    
class Aerobat (object):
    def __init__(self):
        
        self.statusicon = gtk.StatusIcon()

        while not self.statusicon.is_embedded():
            gtk.main_iteration()

        self.bkgr_pixbuf = gen_pixbuf(border_color, width, height)
        tmp_pixbuf = gen_pixbuf(background_color, width-2*border, height-2*border)
        tmp_pixbuf.copy_area(src_x=0, src_y=0, width=width-2*border, height=height-2*border,
                               dest_pixbuf=self.bkgr_pixbuf, dest_x=border, dest_y=border)
                               
        self.normal_pixbuf   = gen_pixbuf(normal_color, width-2*border, height-2*border)
        self.low_pixbuf      = gen_pixbuf(low_color, width-2*border, height-2*border)
        self.critical_pixbuf = gen_pixbuf(critical_color, width-2*border, height-2*border)
        
        self.disabled_pixbuf = gen_pixbuf(border_color, width, height)
        tmp_pixbuf = gen_pixbuf(disabled_color, width-2*border, height-2*border)
        tmp_pixbuf.copy_area(src_x=0, src_y=0, width=width-2*border, height=height-2*border,
                               dest_pixbuf=self.disabled_pixbuf, dest_x=border, dest_y=border)
        
        self.update()

        gobject.timeout_add_seconds(sleep, self.update)

        self.statusicon.connect("popup-menu", self.right_click_event)


    def draw_battery(self, value):
        if (value == None):
            pixbuf = self.disabled_pixbuf.copy()
        else:
            pixbuf = self.bkgr_pixbuf.copy()
            h = int(value*(height-2*border) + 0.5)
            if h == 0:
                h = 1 # the bar should always be visible
            
            if value < low_threshold:
                if value < critical_threshold:
                    color_pixbuf = self.critical_pixbuf
                else:
                    color_pixbuf = self.low_pixbuf
            else:
                color_pixbuf = self.normal_pixbuf
                
            color_pixbuf.copy_area(src_x=0, src_y=0, width=width-2*border, height=h,
                                   dest_pixbuf=pixbuf, dest_x=border, dest_y=height-border-h)
        self.statusicon.set_from_pixbuf(pixbuf)
    
    def update(self):   
        value, text = get_battery_level()
        self.statusicon.set_tooltip(text)
    
        if value != None:
            assert value >= 0.0 and value <= 1.0
        self.draw_battery(value)
        return True
        
    def right_click_event(self, icon, button, time):
        menu = gtk.Menu()
        quit = gtk.MenuItem("Quit")     
        quit.connect("activate", gtk.main_quit)     
        menu.append(quit)       
        menu.show_all()     
        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

if __name__ == "__main__":
    tray = Aerobat()
    gtk.main()
