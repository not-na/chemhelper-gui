#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  iupac.py
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

import chemhelper

class IUPACRenderer(peng3d.gui.Container):
    def __init__(self,ch,*args,**kwargs):
        super(IUPACRenderer,self).__init__(*args,**kwargs)
        
        self.ch = ch
        self.peng = ch.peng
        
        self.formula = chemhelper.notations.iupac.IUPACNotation(name="")
        
        self.initGUI()
    
    def initGUI(self):
        self.initWidgets()
    
    def initWidgets(self):
        # Add Textbox
        self.w_textbox = peng3d.gui.TextInput("textbox",self,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: (16,sh-bh-16),
                                size=lambda sw,sh: (sw-32,32),
                                borderstyle="material",
                                #border=[2,2],
                                default="Enter IUPAC-Conforming Formula here",
                                allow_overflow=True,
                                )
        self.addWidget(self.w_textbox)
        
        self.w_textbox.addAction("textchange",self.on_textchange)
        
        # Add Status Label
        self.w_statuslabel = peng3d.gui.Label("statuslabel",self,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: (16,sh-bh-64),
                                size=lambda sw,sh: (sw-32,32),
                                label="",
                                )
        self.addWidget(self.w_statuslabel)
        self.w_statuslabel._label.multiline = True
        self.w_statuslabel._label.content_valign = "center"
    
    def convert_to(self,other):
        if other == "condensed":
            pass
        elif other == "iupac":
            return
        elif other == "struct_lewis":
            pass
        elif other == "struct_skeleton":
            pass
        else:
            return # Ignore, should not happen, but possible
    
    def redraw_content(self):
        self.formula.name = self.w_textbox.text
        
        valid = False
        converted = False
        invalid = 0
        count = {}
        rev = ""
        
        try:
            c = self.formula.asStructuralFormula()
            converted = True
            
            invalid = len(c.checkValid())
            
            count = c.countAtoms()
            
            rev = c.asIUPACName().name
            
            valid = True
        except chemhelper.errors.UnsupportedFormulaTypeError:
            # TODO: detect if there is an actual error, and display it
            valid = False
        except Exception:
            valid = False
            # Ignore exception
            import traceback;traceback.print_exc()
        
        count["C"] = count.get("C",0)
        count["H"] = count.get("H",0)
        
        d = {"valid":valid,"converted":converted,"invalid":invalid,"count":count,"rev":rev}
        
        if self.formula.name == "":
            l = ""
        elif valid and converted:
            l = "Carbon: {count[C]} Hydrogen: {count[H]}".format(**d)
            if rev!=self.formula.name:
                l+="\nActual Name: {rev}".format(**d)
        else:
            l = "Invalid".format(**d)
        self.w_statuslabel.label = l
    
    def setFormula(self,formula):
        self.formula = formula
        self.w_textbox.text = formula.name
    
    def on_textchange(self):
        # Triggered every time the text changes
        # TODO: make asynchronous, e.g. prevent GUI from freezing during processing
        self.redraw_content()
