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

import math
import collections

import pyglet
from pyglet.gl import *

import peng3d
from peng3d.gui.widgets import mouse_aabb

import chemhelper

from . import common

BUTTON_SIZE = 64

BOND_LENGTH = 32 # Only 32px visible

LAYOUT_SLOT_INVERT = {
    "up":"down",
    "down":"up",
    "left":"right",
    "right":"left",
    }

class LayoutError(RuntimeError):pass

class LewisRenderer(peng3d.gui.Container):
    def __init__(self,ch,*args,**kwargs):
        self.ready = False
        super(LewisRenderer,self).__init__(*args,**kwargs)
        
        self.ch = ch
        
        self.formula = chemhelper.notations.structural.StructuralNotation()
        
        self.element_buttons = []
        self.element_buttons_dict = {}
        
        self.activeElement="C"
        self.mode="draw"
        self.curPressed="C"
        self.n_bindings=1
        
        self.initGUI()
        self.peng.registerEventHandler("on_resize",self.on_resize)
    
    def initGUI(self):
        self.initWidgets()
    
    def initWidgets(self):
        self.initSidebarButtons()
        
        # Add Drawing Area Widget
        self.w_drawarea = DrawingArea("drawarea",self,self.peng.window,self.peng,
                                pos=[BUTTON_SIZE+8,8],
                                size=lambda sw,sh: [sw-BUTTON_SIZE-16,sh-16],
                                )
        self.addWidget(self.w_drawarea)
    
    def initSidebarButtons(self):
        # Add Erase Button
        self.ws_erase = ElementButton("erasebtn",self,self.peng.window,self.peng,
                                pos=[0,0],
                                size=[BUTTON_SIZE,BUTTON_SIZE],
                                label="Erase",
                                borderstyle="oldshadow",
                                )
        self.addWidget(self.ws_erase)
        self.element_buttons_dict["erase"]=self.ws_erase
        
        self.ws_erase.addAction("click",self.on_click_element,"erase")
        
        # Add BindChange Button
        # DISABLED until double/triple binds are supported by the algorithm/GUI
        #self.ws_bindchange = peng3d.gui.Button("bindchangebtn",self,self.peng.window,self.peng,
        #                        pos=[0,0],
        #                        size=[BUTTON_SIZE,BUTTON_SIZE],
        #                        label="Bindings",
        #                        borderstyle="oldshadow",
        #                        )
        #self.addWidget(self.ws_bindchange)
        #
        #self.ws_bindchange.addAction("click",self.on_click_element,"bindchange")
        
        # Add Element Buttons
        for element in common.DEFAULT_ELEMENT_ORDER:
            b = ElementButton("element_%s"%element,self,self.peng.window,self.peng,
                                pos=[0,0],
                                size=[BUTTON_SIZE,BUTTON_SIZE],
                                label=element,
                                borderstyle="oldshadow",
                                )
            self.addWidget(b)
            
            if element==self.activeElement:
                b.pressed=True
            
            b.addAction("click",self.on_click_element,element)
            self.element_buttons.append(b)
            self.element_buttons_dict[element]=b
        
        self.ready = True
        self.updateSidebarButtons()
    
    def updateSidebarButtons(self):
        if not self.ready:
            return # Needed to prevent event handler from calling this too soon
        
        w,h = self.size
        n_buttons = int(h/BUTTON_SIZE)
        n_elements = min(n_buttons-2,len(self.element_buttons))
        
        # Update Bindchange and Erase
        self.ws_erase.pos=[4,h-4-(2*BUTTON_SIZE)]#[4,h-4-(n_buttons*BUTTON_SIZE)]
        # DISABLED see initSidebarButtons
        #self.ws_bindchange.pos=[4,h-4-((n_buttons-1)*BUTTON_SIZE)]
        
        if n_elements <=0:
            # No elements visible
            for e in self.element_buttons:
                e.pos=[-1000,-1000]
        else:
            # Update all visible elements
            for i in range(n_elements):
                e = self.element_buttons[i]
                e.pos=[4,h-4-(i*BUTTON_SIZE+BUTTON_SIZE)]
            # Hide all invisible elements
            for i in range(n_elements,len(self.element_buttons)):
                e = self.element_buttons[i]
                e.pos=[-1000,-1000]
    
    def on_click_element(self,element):
        if element.lower()=="erase":
            self.mode="erase"
            self.setElementPressed("erase")
        elif element.lower()=="bindchange":
            self.n_bindings+=1
            self.n_bindings=max(1,self.n_bindings%4) # Limits to 3, then wraps over
        elif element in common.DEFAULT_ELEMENT_ORDER:
            self.mode="draw"
            self.setElementPressed(element)
            self.activeElement=element
        print(self.activeElement,self.mode,self.n_bindings)
    def setElementPressed(self,element):
        if element==self.curPressed:
            return # Optimization
        self.element_buttons_dict[self.curPressed].pressed=False
        self.element_buttons_dict[element].pressed=True
        self.curPressed=element
     
    def convert_to(self,other):
        if other == "condensed":
            pass
        elif other == "iupac":
            o = self.ch.wmm_iupac
            
            if len(self.formula.atoms)==0:
                notation = chemhelper.notations.iupac.IUPACNotation()
            else:
                notation = self.formula.asIUPACName()
            
            o.setFormula(notation)
        elif other == "struct_lewis":
            return
        elif other == "struct_skeleton":
            pass
        else:
            return # Ignore, should not happen, but possible
    
    def redraw_content(self):
        self.w_drawarea.redraw()
    
    def setFormula(self,formula):
        self.w_drawarea.cleanup()
        self.formula = formula
        self.w_drawarea.layout_formula()
        self.redraw_content()
    
    def on_resize(self,width,height):
        self.updateSidebarButtons()
        if self.ready:
            self.bg.redraw_bg()

class ElementButton(peng3d.gui.ToggleButton):
    def on_mouse_press(self,x,y,button,modifiers):
        if not self.clickable:
            return
        elif mouse_aabb([x,y],self.size,self.pos):
            if button == pyglet.window.mouse.LEFT:
                self.doAction("click")
                # Do not change press state, done by handler
                #self.pressed = not self.pressed
                #if self.pressed:
                #    self.doAction("press_down")
                #else:
                #    self.doAction("press_up")
            elif button == pyglet.window.mouse.RIGHT:
                self.doAction("context")
            self.redraw()

class DrawingArea(peng3d.gui.Widget):
    def __init__(self,*args,**kwargs):
        super(DrawingArea,self).__init__(*args,**kwargs)
        
        self.next_id = 0
        
        self.batch_font = pyglet.graphics.Batch()
        self.batch_bg = pyglet.graphics.Batch()
        self.batch_bonds = pyglet.graphics.Batch()
        
        self.atoms={} # map of id:atom
        
        self.bg_vlists = set()
        self.bg_radius = 10#int(self.window.width*0.05)
        self.bg_vertices = self.genBgVertices()
        
        self.atom_radius = 16
        
        # DISABLED until multiple elements are supported/sidebar is populated
        # Border set to 0px
        self.setBackground(DrawingAreaBackground(self,borderstyle="oldshadow",border=[0,0]))
        
        #self.peng.registerEventHandler("on_resize",self.on_resize)
        pyglet.clock.schedule_interval(lambda dt:self.checkConsistency(),2)
    
    def cleanup(self):
        for atom in self.submenu.formula.atoms:
            self.cleanupAtom(atom)
    def cleanupAtom(self,atom):
        if hasattr(atom,"_drawinfo"):
            dinfo = atom._drawinfo
            try:
                if "layout_slots" in dinfo:
                    # Free the slots to allow new atoms to occupy them
                    for slot,other in dinfo["layout_slots"].items():
                        if other is None:
                            # Skip if there is no other atom
                            continue
                        # Free the slot
                        other._drawinfo["layout_slots"][LAYOUT_SLOT_INVERT[slot]]=None
                    del dinfo["layout_slots"]
                if "label" in dinfo:
                    # Label needs to be manually deleted to remove its vlist from the batch
                    dinfo["label"].delete()
                    del dinfo["label"]
                if "id" in dinfo:
                    # Deletes the atom from the dict used by checkConsistency
                    del self.atoms[dinfo["id"]]
                if "bg_vlist" in dinfo:
                    # BG VList also needs to be manually deleted
                    self.bg_vlists.discard(dinfo["bg_vlist"])
                    dinfo["bg_vlist"].delete()
                    del dinfo["bg_vlist"]
                if "bg_group" in dinfo:
                    # Probably unneccessary
                    del dinfo["bg_group"]
                
                if "bond_vlists" in dinfo:
                    # Delete all bond vlists in both this atom and the respective neighbour
                    for first,second,vlist in dinfo["bond_vlists"]:
                        if atom is first:
                            if hasattr(second,"_drawinfo") and "bond_vlists" in second._drawinfo and [first,second,vlist] in second._drawinfo["bond_vlists"]:
                                del second._drawinfo["bond_vlists"][second._drawinfo["bond_vlists"].index([first,second,vlist])]
                        elif atom is second:
                            if hasattr(first,"_drawinfo") and "bond_vlists" in first._drawinfo and [first,second,vlist] in first._drawinfo["bond_vlists"]:
                                del first._drawinfo["bond_vlists"][first._drawinfo["bond_vlists"].index([first,second,vlist])]
                        vlist.delete()
                    del dinfo["bond_vlists"]
            except Exception:
                print("Ignoring error during cleanup of atom %s"%atom.name)
                print("Ignored error:")
                import traceback;traceback.print_exc()
            
            del atom._drawinfo
    
    def on_redraw(self):
        super(DrawingArea,self).on_redraw()
        for atom in self.submenu.formula.atoms:
            self.redraw_atom(atom)
    def draw(self):
        super(DrawingArea,self).draw()
        self.batch_bonds.draw()
        self.batch_bg.draw()
        self.batch_font.draw()
    
    def genBgVertices(self):
        cc = [0,0]
        c0,c1,c2,c3,c4,c5,c6,c7,c8,c9 = [self._posAtAngle(self.bg_radius,theta) for theta in range(0,360,36)]
        
        # Creates a circle-approximation with 10 corners
        return (
            cc+c1+c0+
            cc+c2+c1+
            cc+c3+c2+
            cc+c4+c3+
            cc+c5+c4+
            cc+c6+c5+
            cc+c7+c6+
            cc+c8+c7+
            cc+c9+c8+
            cc+c0+c9
            )
    def _posAtAngle(self,d,theta):
        # d is the distance
        # theta is the angle in degrees
        theta = math.radians(theta)
        return [d*math.cos(theta),d*math.sin(theta)]
    def _angleFromPos(self,origin,point):
        # origin is the offset
        # point is the point
        x,y = point[0]-origin[0],point[1]-origin[1]
        return math.degrees(math.atan2(x,y))
    
    def assertAtom(self,atom):
        if not hasattr(atom,"_drawinfo"):
            atom._drawinfo = {}
        dinfo = atom._drawinfo
        
        if "id" not in dinfo:
            # TODO: make this safer
            dinfo["id"]=self.next_id
            self.atoms[dinfo["id"]]=atom
            self.next_id+=1
        
        if "label" not in dinfo:
            dinfo["label"]=pyglet.text.Label(text=atom.symbol,color=[62,67,73,255],font_name="Arial",font_size=16,anchor_x="center",anchor_y="center",batch=self.batch_font)
        
        if "bg_group" not in dinfo:
            dinfo["bg_group"] = _AtomBackgroundGroup(self,atom)
        if "bg_vlist" not in dinfo:
            # Vertex list for the background "circle"
            # Consists of 10 slices, e.g. 30 vertices
            dinfo["bg_vlist"]=self.batch_bg.add(30,GL_TRIANGLES, dinfo["bg_group"], 
                                ("v2f",self.bg_vertices),
                                ("c3B",self.bg.getColors()[0]*30), # Only works if a button-style background is used
                                )
            self.bg_vlists.add(dinfo["bg_vlist"])
        if "bond_vlists" not in dinfo:
            dinfo["bond_vlists"] = []
        if "layout_slots" not in dinfo:
            dinfo["layout_slots"] = {"up":None,"left":None,"right":None,"down":None}
        if "pos" not in dinfo:
            dinfo["pos"]=self.window.width/2,self.window.height/2
    def layout_formula(self):
        # Layout algorithm for singly-branched alkane
        # Will produce unexpected results if branches on a branch are found or if the alkane is invalid
        # Note that the layout is not chemically correct
        
        struct = self.submenu.formula
        # Some safety checks
        if struct.checkValid() != []:
            raise LayoutError("Formula not valid")
        elif struct.countAtoms() == {}:
            # Empty formula
            return # No layout needed
        
        # Make sure all atoms are initialized
        # Makes it easier and safer later, as all atoms have already been vetted
        for atom in struct.atoms:
            self.assertAtom(atom)
        
        # First, extract the backbone
        bbone = struct.getCarbonBackbone()
        # The carbon backbone is displayed along the vertical axis
        # Calculate space needed, inclusive hydrogen
        # TODO: add support for portrait screens
        # TODO: add support for dynamic height of backbone via side chain length
        # Length of the backbone
        totlen = len(bbone)+2 # +2 for hydrogen
        # Viewport width
        maxwidth = self.size[0]-8-16-32 # -8 for the border, -16 for padding and -32/2=-16 until the center of the first atom
        
        if maxwidth/totlen<BOND_LENGTH and False:
            raise LayoutError("Backbone to long")
        
        sx,sy = BOND_LENGTH*totlen,32 # Size of the formula/backbone
        # Base offset, centers structure of sx,sy on the widget
        ox,oy = self.size[0]/2-sx/2, int(self.size[1]/2) # half of the above, dynamic
        # Adds own position
        ox,oy = ox+self.pos[0],oy+self.pos[1]
        
        # Place all base carbons
        prev = None
        for c in bbone:
            if prev is None:
                # First atom gets special treatment
                c._drawinfo["pos"]=[ox,oy]
            else:
                # All other atoms are placed relative to their predecessor
                self.layout_pos_at_slot(prev,c,"right")
            prev = c
        
        # Place side chains
        for c in bbone:
            for neighbour in c.bindings:
                if neighbour in bbone:
                    # Neighbour is part of the backbone
                    continue
                elif neighbour.symbol=="H":
                    continue
                elif neighbour.symbol=="C":
                    # Found a branch
                    self.layout_branch(bbone,neighbour,c)
                else:
                    raise errors.UnsupportedElementError("Element '%s' is not currently supported"%neighbour.symbol)
        
        # Place all hydrogen
        for atom in struct.atoms:
            if atom.symbol=="H":
                #dinfo = atom._drawinfo
                
                parent = list(atom.bindings.keys())[0] # The Carbon it is bound to
                #p_dinfo = parent._drawinfo
                
                slot = self.layout_atom_at_base(parent,atom)
                
                if parent in bbone:
                    print("H at %s is %s"%(parent.name,atom))
                    print("Parent slots: %s"%parent._drawinfo["layout_slots"])
                    print("Adding to slot %s"%slot)
                
                # Fill the slot
                #dinfo["pos"]=self.layout_get_pos_from_slot(parent,slot)
                #p_dinfo["layout_slots"][slot]=atom
    def layout_branch(self,bbone,start,c):
        print("Starting branch at %s"%(bbone.index(c)+1))
        print("Starting atom is %s"%c.name)
        self.assertAtom(start)
        if start.symbol!="C":
            return
        
        visited = set([c])
        
        atom = start
        prev = c
        while True:
            self.assertAtom(atom)
            print("Processing %s"%atom.name)
            visited.add(atom)
            dinfo = atom._drawinfo
            
            #slot = self.layout_find_sidechain_slot(prev)
            #pos = self.layout_get_pos_from_slot(prev,slot)
            #dinfo["pos"]=pos
            
            print("Layout Prev: %s"%prev._drawinfo["layout_slots"])
            #prev._drawinfo["layout_slots"][slot]=atom
            #dinfo["layout_slots"][LAYOUT_SLOT_INVERT[slot]]=prev
            slot = self.layout_atom_at_base(prev,atom,self.layout_find_sidechain_slot)
            print("Adding to slot %s"%slot)
            print("Layout Prev: %s"%prev._drawinfo["layout_slots"])
            
            s = False
            for neighbour in atom.bindings:
                if neighbour.symbol!="C":
                    continue
                elif neighbour == prev:
                    continue
                elif neighbour in visited:
                    continue
                prev = atom
                atom = neighbour
                s = True
            
            # End of chain reached
            if not s:
                break
        print("Finished")
        
    def layout_find_free_slot(self,atom,order=None):
        self.assertAtom(atom)
        dinfo = atom._drawinfo
        
        order = order if order is not None else dinfo["layout_slots"].keys()
        slots = [i for i in order if dinfo["layout_slots"][i] is None]
        
        if len(slots)==0:
            raise ValueError("Not enough slots")
        return slots[0]
    def layout_find_sidechain_slot(self,atom):
        self.assertAtom(atom)
        dinfo = atom._drawinfo
        
        if dinfo["layout_slots"]["up"] is None:
            return "up"
        elif dinfo["layout_slots"]["down"] is None:
            return "down"
        else:
            raise ValueError("Sidechain slots already occupied")
        
    def layout_get_pos_from_slot(self,base,slot):
        self.assertAtom(base)
        px,py = base._drawinfo["pos"]
        if slot=="up":
            return px,py+BOND_LENGTH
        elif slot=="left":
            return px-BOND_LENGTH,py
        elif slot=="right":
            return px+BOND_LENGTH,py
        elif slot=="down":
            return px,py-BOND_LENGTH
        else:
            raise ValueError("Unsupported slot %s"%slot)
    def layout_pos_at_slot(self,base,atom,slot):
        self.assertAtom(atom)
        pos = self.layout_get_pos_from_slot(base,slot)
        
        atom._drawinfo["pos"]=pos
        atom._drawinfo["layout_slots"][LAYOUT_SLOT_INVERT[slot]]=base
        base._drawinfo["layout_slots"][slot]=atom
    def layout_atom_at_base(self,base,atom,alloc=None):
        if alloc is None:
            alloc = self.layout_find_free_slot
        self.assertAtom(atom)
        slot = alloc(base)
        self.layout_pos_at_slot(base,atom,slot)
        return slot
    
    def redraw_atom(self,atom):
        self.assertAtom(atom)
        dinfo = atom._drawinfo
        
        dinfo["label"].x,dinfo["label"].y = dinfo["pos"]
        #print(dinfo["label"].x,dinfo["pos"])
        
        others = []
        for first,second,vlist in dinfo["bond_vlists"]:
            if first is atom:
                others.append(second)
                vlist.vertices[:2]=dinfo["pos"]
            elif second is atom:
                others.append(first)
                vlist.vertices[2:]=dinfo["pos"]
            else:
                raise ValueError("Unknown bond")
        
        for other in atom.bindings:
            if other in others:
                continue
            self.assertAtom(other)
            vlist = self.batch_bonds.add(2,GL_LINES,None,
                                ("v2f",(dinfo["pos"][0],dinfo["pos"][1],other._drawinfo["pos"][0],other._drawinfo["pos"][1])),
                                ("c3B",[0,0,0]*2),
                                )
            #print(atom,other)
            #print(list(vlist.vertices))
            dinfo["bond_vlists"].append([atom,other,vlist])
            other._drawinfo["bond_vlists"].append([atom,other,vlist])
    
    def on_resize(self,width,height):
        super(DrawingArea,self).on_resize(width,height)
        return # Currently disabled
        if int(width*0.05)==self.bg_radius:
            return # Optimization, skips if the radius would stay the same
        self.bg_radius = int(width*0.05)
        
        self.bg_vertices = self.genBgVertices()
        
        for vlist in self.bg_vlists:
            vlist.vertices = self.bg_vertices
    
    def on_mouse_press(self,x,y,button,modifiers):
        super(DrawingArea,self).on_mouse_press(x,y,button,modifiers)
        if not self.clickable:
            return
        
        for atom in list(self.submenu.formula.atoms):
            if not hasattr(atom,"_drawinfo"):
                continue # was probably collected by checkConsistency in an earlier iteration, but is still in the list
            ax,ay = atom._drawinfo["pos"]
            if (ax-x)**2+(ay-y)**2<self.atom_radius**2: # Simple pythagorean equation
                #print(ax,ay)
                #print(atom._drawinfo.get("layout_slots",{}))
                #print("Bonds")
                #for first,second,vlist in atom._drawinfo.get("bond_vlists",[]):
                #    print("Bond from %s to %s with vlist %s"%(first.name if first.symbol!="H" else "H",second.name if second.symbol!="H" else "H",hex(id(vlist))))
                #    print("VList: %s"%list(vlist.vertices))
                #o_c = atom._drawinfo["bg_vlist"].colors[:3]
                #if o_c == [0,0,0]:
                #    print("Switch to bg")
                #    c = self.bg.getColors()[0]
                #else:
                #    print("Switch to black")
                #    c = [0,0,0]
                #atom._drawinfo["bg_vlist"].colors=c*30
                self.on_click_atom(atom,x,y,button,modifiers)
                break # Prevents accidental multi-clicks
    
    def on_click_atom(self,atom,x,y,button,modifiers):
        print("Clicked atom %s n=%s with button %s"%(atom.name,atom._drawinfo["id"],button))
        if button == pyglet.window.mouse.LEFT:
            if self.submenu.mode=="erase":
                self.eraseAtom(atom)
            elif self.submenu.mode=="draw":
                self.drawAtomAtAtom(atom)
        elif button == pyglet.window.mouse.RIGHT:
            if self.submenu.mode=="erase":
                self.drawAtomAtAtom(atom)
            elif self.submenu.mode=="draw":
                self.eraseAtom(atom)
    
    def drawAtomAtAtom(self,atom):
        if atom.symbol=="H":
            self._drawAtomReplaceHydrogen(atom)
        else:
            self._drawAtomAdd(atom)
        
    def _drawAtomAdd(self,atom):
        # Called if the clicked atom is not a hydrogen atom
        
        # First, check if there are any available bindings or hydrogen
        n = atom.max_bindings-atom.num_bindings
        for other,binds in atom.bindings.items():
            # Hydrogen atoms may be replaced
            if other.symbol=="H":
                n+=binds
        
        # Some safety checks
        if n<self.submenu.n_bindings:
            return # If there is no place available
        
        # Remove as many hydrogen as necessary
        while atom.max_bindings-atom.num_bindings<self.submenu.n_bindings:
            for other in list(atom.bindings):
                if other.symbol=="H":
                    other.erase()
                    self.cleanupAtom(other)
                    break
        
        # Create atom
        a = chemhelper.elements.ELEMENTS[self.submenu.activeElement](self.submenu.formula,name="%s #%s"%(self.submenu.activeElement,self.next_id))
        self.submenu.formula.addAtom(a)
        a.bindToAtom(atom,self.submenu.n_bindings)
        self.assertAtom(a)
        
        # Find a suitable slot
        # Works by trying to find the longest chain starting from the base atom
        ends = [other for other in atom.bindings if other.symbol=="C" and other is not a]
        if len(ends)<=1:
            print("SHORT")
            # In case there is only one or fewer connected atoms
            ends = [atom]
        
        # Finds the first atom of the longest chain that is not the starting atom itself
        
        # Built-In Structure formula method
        #chain = self.submenu.formula._longestChain(ends)
        
        # Finds the first neighbour that also has other C neighbours that are not the start atom itself
        # Only "looks" down the tree for two atoms
        pre_atom = None
        for neighbour in atom.bindings:
            if neighbour.symbol!="C":
                continue
            for neighbour2 in neighbour.bindings:
                if neighbour2.symbol=="C" and neighbour2 is not atom:
                    pre_atom=neighbour
                    break
            if pre_atom is None:
                break
        
        # Bellman Ford algorithm ported from NetworkX
        # Currently does not work, requires conversion to be directed
        #pred,dist = self._bellmanFord(self.submenu.formula.atoms,atom)
        #pre_atom = pred[atom]
        #print("BELLMAN FORD")
        #print(pred)
        #print(dist)
        #print(pre_atom)
        
        # Checks if the chain needs to be flipped
        
        if pre_atom is None:
            # There was only the atom itself there, probably methane
            order = None
        else:
            s = None
            for sname,satom in pre_atom._drawinfo["layout_slots"].items():
                print(sname,satom)
                if satom==atom:
                    s = sname
                    break
            
            if s is None:
                raise ValueError("Could not find origin while searching for extension direction, algorithmic error")
            elif s=="up":
                # The base atom is in the up slot, simply extend the line
                order = ["up","down","left","right"]
            elif s=="down":
                order = ["down","up","left","right"]
            elif s=="left":
                order = ["left","right","up","down"]
            elif s=="right":
                order = ["right","left","up","down"]
            else:
                raise ValueError("Encountered unsupported slot %s"%s)
        slot = self.layout_find_free_slot(atom,order)
        
        # Layout the atom
        self.layout_pos_at_slot(atom,a,slot)
        self.fillWithHydrogen()
        self.redraw_atom(a)
    
    def _bellmanFord(self,graph,start):
        if start not in graph:
            raise ValueError("Base atom not in graph")
        
        dist = {start: 0}
        pred = {start: None}
        
        if len(graph) == 1:
            return pred, dist
        
        return self._bellmanFordRelaxation(graph, pred, dist, [start])
    
    def _bellmanFordRelaxation(self,graph,pred,dist,source):
        inf = float('inf')
        n = len(graph)

        count = {}
        q = collections.deque(source)
        in_q = set(source)
        while q:
            u = q.popleft()
            in_q.remove(u)
            # Skip relaxations if the predecessor of u is in the queue.
            if pred[u] not in in_q:
                dist_u = dist[u]
                for v in u.bindings:
                    dist_v = dist_u + (-1)
                    if dist_v < dist.get(v, inf):
                        if v not in in_q:
                            q.append(v)
                            in_q.add(v)
                            count_v = count.get(v, 0) + 1
                            if count_v == n:
                                raise RuntimeError(
                                    "Negative cost cycle detected.")
                            count[v] = count_v
                        dist[v] = dist_v
                        pred[v] = u

        return pred, dist
    
    def _drawAtomReplaceHydrogen(self,atom):
        # Replaces the given hydrogen
        if atom.symbol!="H":
            raise ValueError("Cannot Hydrogen-Replace non-Hydrogen")
        self.assertAtom(atom)
        
        # Get the atom the hydrogen is attached to
        base,slot = None,None
        for s,n in atom._drawinfo["layout_slots"].items(): # Only works if the hydrogen is initialized
            if n is not None and n.symbol!="H":
                base = n
                slot = s
                break
        if base is None:
            raise ValueError("Cannot replace non-connected hydrogen")
        
        self.assertAtom(base)
        slot = LAYOUT_SLOT_INVERT[slot] # Needs to be inverted since the original is from the perspective of the hydrogen
        
        # Erase the old atom
        atom.erase()
        self.cleanupAtom(atom)
        
        # Add the new atom
        a = chemhelper.elements.ELEMENTS[self.submenu.activeElement](self.submenu.formula,name="%s #%s"%(self.submenu.activeElement,self.next_id))
        self.submenu.formula.addAtom(a)
        a.bindToAtom(base,1) # Always 1-bind
        self.assertAtom(a)
        
        # Layout the new atom
        # Should assume the position of the input atom
        self.layout_pos_at_slot(base,a,slot)
        
        # Some other maintenance required
        self.fillWithHydrogen()
        self.redraw_atom(a)
        
    def eraseAtom(self,atom):
        if atom.symbol=="H":
            return # Do not delete hydrogen, would be automatically replaced anyways
        
        # Delete atom
        atom.erase()
        self.cleanupAtom(atom)
        
        # Check consistency of the rest of the network
        self.checkConsistency()
        self.fillWithHydrogen()
        
        # Update convert clickability, prevents conversion if the formula is invalid
        self.submenu.ch.wmmt_convert.enabled = self.submenu.formula.checkConnected()
    
    def fillWithHydrogen(self):
        for atom in list(self.submenu.formula.atoms):
            # Fill the atom with hydrogen while automatically layouting them
            while atom.num_bindings<atom.max_bindings:
                # Add the hydrogen
                h = chemhelper.elements.Hydrogen(self.submenu.formula)
                self.submenu.formula.addAtom(h)
                atom.bindToAtom(h)
                
                # Position it correctly
                self.layout_atom_at_base(atom,h)
    
    def checkConsistency(self):
        for a_id,atom in list(self.atoms.items()):
            if atom not in self.submenu.formula.atoms:
                # Was probably deleted by some other means
                atom.erase()
                self.cleanupAtom(atom)

class _AtomBackgroundGroup(pyglet.graphics.Group):
    def __init__(self,darea,atom,*args,**kwargs):
        super(_AtomBackgroundGroup,self).__init__(*args,**kwargs)
        
        self.darea = darea
        self.atom = atom
    
    def set_state(self):
        self.darea.assertAtom(self.atom)
        
        pos = self.atom._drawinfo["pos"]
        glTranslatef(pos[0],pos[1],0)
    def unset_state(self):
        self.darea.assertAtom(self.atom)
        
        pos = self.atom._drawinfo["pos"]
        glTranslatef(-pos[0],-pos[1],0)

class DrawingAreaBackground(peng3d.gui.ButtonBackground):
    change_on_press = False
    def getColors(self):
        bg,o,i,s,h = super(DrawingAreaBackground,self).getColors()
        return bg,o,bg,s,h
    
    def bs_oldshadow(self,bg,o,i,s,h):
        if self.change_on_press and self.widget.pressed:
            i = s
            s,h = h,s
        elif self.change_on_press and self.widget.is_hovering:
            i = [min(i[0]+6,255),min(i[1]+6,255),min(i[2]+6,255)]
            s = [min(s[0]+6,255),min(s[1]+6,255),min(s[2]+6,255)]
        cb1 = s+s+s+s
        cb2 = h+h+h+h
        cb3 = h+h+h+h
        cb4 = s+s+s+s
        cc  = i+i+i+i
        
        return cb1+cb2+cb3+cb4+cc
