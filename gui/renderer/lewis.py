#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  lewis.py
#  
#  Copyright 2017 notna <notna@apparat.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import peng3d

class LewisRenderer(peng3d.gui.Container):
    def __init__(self,ch,*args,**kwargs):
        super(LewisRenderer,self).__init__(*args,**kwargs)
        
        self.ch = ch
        
        self.initGUI()
    
    def initGUI(self):
        self.initWidgets()
    
    def initWidgets(self):
        pass
    
    def convert_to(self,other):
        if other == "condensed":
            pass
        elif other == "iupac":
            pass
        elif other == "struct_lewis":
            return
        elif other == "struct_skeleton":
            pass
        else:
            return # Ignore, should not happen, but possible
    
    def redraw_content(self):
        pass
