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

import sys
import threading

import pyglet
import peng3d

import chemhelper

class IUPACRenderer(peng3d.gui.Container):
    def __init__(self,ch,*args,**kwargs):
        super(IUPACRenderer,self).__init__(*args,**kwargs)
        
        self.ch = ch
        
        self.formula = chemhelper.notations.iupac.IUPACNotation(name="")
        
        self.parse_event = threading.Event()
        self.parse_event.clear()
        
        self.parse_thread = threading.Thread(name="IUPAC Name Parsing Thread",target=self._parseThread)
        self.parse_thread.daemon = True
        self.parse_thread.start()
        
        self.parse_lock = threading.Lock()
        
        self.parse_text = ""
        self.parse_valid = False
        
        self.initGUI()
    
    def initGUI(self):
        self.initWidgets()
    
    def initWidgets(self):
        # Add Textbox
        if len(sys.argv)>1:
            # Check if it is a file or option
            if not ("/" in sys.argv[1] or sys.argv[1].startswith("-")):
                text = sys.argv[1]
            else:
                text = ""
        else:
            text = ""
        self.formula.name=text
        self.w_textbox = peng3d.gui.TextInput("textbox",self,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: (16,sh-bh-16),
                                size=lambda sw,sh: (sw-32,32),
                                borderstyle="material",
                                #border=[2,2],
                                text=text,
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
                                label_cls=pyglet.text.HTMLLabel,
                                multiline=True,
                                )
        self.addWidget(self.w_statuslabel)
        self.w_statuslabel._label.content_valign = "center"
        
        self.on_textchange()
    
    def convert_to(self,other):
        if other == "condensed":
            pass
        elif other == "iupac":
            return
        elif other == "struct_lewis":
            o = self.ch.wmm_slewis
            
            if self.formula.name=="":
                o.setFormula(chemhelper.notations.structural.StructuralNotation())
                return
            
            o.setFormula(self.formula.asStructuralFormula())
        elif other == "struct_skeleton":
            pass
        else:
            return # Ignore, should not happen, but possible
    
    def redraw_content(self):
        self.formula.name = self.w_textbox.text
        
    def on_redraw(self):
        super(IUPACRenderer,self).on_redraw()
        
        if self.parse_lock.acquire(blocking=False):
            if self.w_statuslabel.label!=self.parse_text:
                self.w_statuslabel.label = self.parse_text
                self.w_statuslabel.redraw_label()
                self.ch.wmmt_convert.enabled = self.parse_valid
            self.parse_lock.release()
    
    def setFormula(self,formula):
        self.formula = formula
        self.w_textbox.text = formula.name
    
    def on_textchange(self):
        # Triggered every time the text changes
        # TODO: make asynchronous, e.g. prevent GUI from freezing during processing
        
        # Prevents locking this function if parsing is ongoing
        if self.parse_lock.acquire(blocking=False):
            self.redraw_content()
            self.w_statuslabel.label = "Calculating..."
            self.w_statuslabel.redraw_label()
            self.parse_lock.release()
        self.parse_event.set()
    
    def _parseThread(self):
        while True:
            try:
                self.parse_event.wait()
                self.parse_event.clear()
                
                self.parse_lock.acquire()
                l,valid = self._parseThread_parseSingle()
                self.parse_text = l
                self.parse_valid = valid
                self.redraw()
                self.parse_lock.release()
            except Exception:
                print("Exception in parse thread:")
                import traceback;traceback.print_exc()
                self.parse_text = "ERROR"
                self.parse_valid = False
    
    def _parseThread_parseSingle(self):
        valid = False
        converted = False
        invalid = 0
        count = {}
        rev = ""
        ereason = "Unknown"
        err = None
        
        try:
            c = self.formula.asStructuralFormula()
            converted = True
            
            invalid = len(c.checkValid())
            
            count = c.countAtoms()
            
            rev = c.asIUPACName().name
            
            valid = True
        except chemhelper.errors.UnsupportedFormulaTypeError as e:
            # TODO: detect if there is an actual error, and display it
            valid = False
            ereason = e.args[0]
            err = e
        except Exception as e:
            valid = False
            # Ignore exception
            ereason = e.args[0]
            err = e
            import traceback;traceback.print_exc()
        
        count["C"] = count.get("C",0)
        count["H"] = count.get("H",0)
        
        # Should be true if the error was not reported with a custom exception, as should be the case
        # This is just here to inform the user that the error is not directly the users fault
        # The locals check at the beginning is required since the err var seems to be deleted sometimes...
        internal_error = err.__class__ in [chemhelper.errors.InternalError,ValueError,TypeError,IndexError,RuntimeError,KeyError]
        
        # Generates data to be used in message formatting
        d = {"valid":valid,
             "converted":converted,
             "invalid":invalid,
             "count":count,
             "rev":rev,
             "ereason":ereason,
             "interror":" (Internal Error '%s')"%err.__class__.__name__ if internal_error else "",
             }
        
        l = ""
        if self.formula.name == "":
            pass
        elif valid and converted:
            # Disabled since element counts are displayed below
            #l+= "Carbon: {count[C]} Hydrogen: {count[H]}".format(**d)
            
            l+="<br/>Sum Formula: "
            for element in ["C","H","O"]:
                if count.get(element,0)==0:
                    continue
                elif count[element]==1:
                    l+=element
                else:
                    l+="%s<sub>%s</sub>"%(element,count[element])
            
            if rev!=self.formula.name:
                l+="<br/>Actual Name: {rev}".format(**d)
        else:
            l+= "Invalid<br/>Reason:<br/>{ereason}{interror}".format(**d)
        l+="</font>"
        
        return l,valid
