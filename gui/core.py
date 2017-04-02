#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  core.py
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

import traceback

import pyglet
import peng3d

import chemhelper

import pyfileselect

from . import renderer

FILE_TYPES = [("SMILES File","*.smi"),("SMILES File","*.smiles"),("InChI File","*.inchi"),("All Files","*.*")]

class Chemhelper(object):
    def __init__(self,peng):
        self.peng = peng
        
        self.fname = None
        
        self.curWorkspace = None
        self.curWorkspaceObj = None
        # 60,65,66 seems like a nice background color
        # Probably using 242,241,240 instead, default Ubuntu/GTK window background color
    
    # Initialization Code
    def initGUI(self):
        # Init GUI
        peng = self.peng
        self.window = window = peng.createWindow(caption="ChemHelper v%s"%chemhelper.version.VERSION,resizable=True,vsync=True)
        
        self.peng.resourceMgr.addCategory("gui")
        
        self.initMenuMain()
        
        peng.window.changeMenu("main")
    # Init Menus
    def initMenuMain(self):
        # Init Menu Main
        self.m_main = peng3d.GUIMenu("main",self.peng.window,self.peng)
        self.peng.window.addMenu(self.m_main)
        
        self.initSubMenuMainMain()
        
        self.m_main.changeSubMenu("main")
    # Init SubMenus
    def initSubMenuMainMain(self):
        # Init SubMenu Main Main
        self.mm_main = peng3d.SubMenu("main",self.m_main,self.peng.window,self.peng)
        self.m_main.addSubMenu(self.mm_main)
        
        #self.mm_main.setBackground([60,65,66])
        self.mm_main.setBackground([242,241,240])
        
        # Add Container toolbar
        self.wmm_toolbar = peng3d.gui.Container("toolbar",self.mm_main,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: [0,sh-bh],
                                size=lambda sw,sh: [sw,32+12],
                                )
        self.mm_main.addWidget(self.wmm_toolbar)
        
        self.wmm_toolbar.setBackground("oldshadow")
        
        # Toolbar buttons
        # Add toolbar load
        self.wmmt_load = peng3d.gui.Button("loadbtn",self.wmm_toolbar,self.peng.window,self.peng,
                                pos=lambda sw,sh,bw,bh: ((bw+2)*0+6,6),
                                size=[96,32],
                                label="Load",
                                borderstyle="oldshadow",
                                )
        self.wmm_toolbar.addWidget(self.wmmt_load)
        def f():
            fname = pyfileselect.openDialog(FILE_TYPES)
            print("Loaded from %s"%fname)
            self.loadFrom(fname)
                
        self.wmmt_load.addAction("click",f)
        
        # Add toolbar save
        self.wmmt_save = peng3d.gui.Button("savebtn",self.wmm_toolbar,self.peng.window,self.peng,
                                pos=lambda sw,sh,bw,bh: ((bw+2)*1+6,6),
                                size=[96,32],
                                label="Save",
                                borderstyle="oldshadow",
                                )
        self.wmm_toolbar.addWidget(self.wmmt_save)
        def f():
            if self.fname is None:
                self.fname = pyfileselect.saveDialog(FILE_TYPES)
            print("Saved to %s"%self.fname)
            self.saveAs(self.fname)
                
        self.wmmt_save.addAction("click",f)
        
        # Add toolbar export
        self.wmmt_export = peng3d.gui.Button("exportbtn",self.wmm_toolbar,self.peng.window,self.peng,
                                pos=lambda sw,sh,bw,bh: ((bw+2)*2+6,6),
                                size=[96,32],
                                label="Export",
                                borderstyle="oldshadow",
                                )
        self.wmm_toolbar.addWidget(self.wmmt_export)
        def f():
            fname = pyfileselect.saveDialog(FILE_TYPES)
            print("Exported to %s"%fname)
            self.saveAs(fname)
        self.wmmt_export.addAction("click",f)
        
        # Add toolbar convert
        self.wmmt_convert = peng3d.gui.Button("convertbtn",self.wmm_toolbar,self.peng.window,self.peng,
                                pos=lambda sw,sh,bw,bh: ((bw+2)*3+6,6),
                                size=[96,32],
                                label="Convert",
                                borderstyle="oldshadow",
                                )
        self.wmm_toolbar.addWidget(self.wmmt_convert)
        def f():
            self.curWorkspaceObj.visible=False
            self.reInitConvert()
        self.wmmt_convert.addAction("click",f)
        
        self.initSubMenuMainMain_Condensed()
        self.initSubMenuMainMain_IUPAC()
        self.initSubMenuMainMain_StructuralLewis()
        self.initSubMenuMainMain_StructuralSkeleton()
        self.initSubMenuMainMain_Convert()
        self.setWorkspace("iupac")
    # Init Workspaces
    def initSubMenuMainMain_Condensed(self):
        # Init Workspace Condensed
        self.wmm_condensed = renderer.condensed.CondensedRenderer(self,"w_condensed",self.mm_main,self.peng.window,self.peng,
                                pos=[0,0],
                                size=lambda sw,sh: [sw,sh-32-12],
                                )
        self.mm_main.addWidget(self.wmm_condensed)
        
        self.wmm_condensed.setBackground("oldshadow")
        self.wmm_condensed.visible=False
    def initSubMenuMainMain_IUPAC(self):
        # Init Workspace IUPAC
        self.wmm_iupac = renderer.iupac.IUPACRenderer(self,"w_iupac",self.mm_main,self.peng.window,self.peng,
                                pos=[0,0],
                                size=lambda sw,sh: [sw,sh-32-12],
                                )
        self.mm_main.addWidget(self.wmm_iupac)
        
        self.wmm_iupac.setBackground("oldshadow")
        self.wmm_iupac.visible=False
    def initSubMenuMainMain_StructuralLewis(self):
        # Init Workspace SLewis
        self.wmm_slewis = renderer.lewis.LewisRenderer(self,"w_slewis",self.mm_main,self.peng.window,self.peng,
                                pos=[0,0],
                                size=lambda sw,sh: [sw,sh-32-12],
                                )
        self.mm_main.addWidget(self.wmm_slewis)
        
        self.wmm_slewis.setBackground("oldshadow")
        self.wmm_slewis.visible=False
    def initSubMenuMainMain_StructuralSkeleton(self):
        # Init Workspace SSkeleton
        self.wmm_sskeleton = renderer.skeleton.SkeletonRenderer(self,"w_sskeleton",self.mm_main,self.peng.window,self.peng,
                                pos=[0,0],
                                size=lambda sw,sh: [sw,sh-32-12],
                                )
        self.mm_main.addWidget(self.wmm_sskeleton)
        
        self.wmm_sskeleton.setBackground("oldshadow")
        self.wmm_sskeleton.visible=False
    def initSubMenuMainMain_Convert(self):
        # Init Convert Menu
        self.wmm_convert = peng3d.gui.Container("w_convert",self.mm_main,self.peng.window,self.peng,
                                pos=[0,0],
                                size=lambda sw,sh: [sw,sh-32-12],
                                )
        self.mm_main.addWidget(self.wmm_convert)
        
        self.wmm_convert.setBackground("oldshadow")
        self.wmm_convert.visible=False
        
        # Add Button1
        self.wmmc_btn1 = peng3d.gui.Button("btn1",self.wmm_convert,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: [((sw*0.05)+(((sw*0.9)/3)*0))+((sw*0.9)/3-(sw*0.9)/3.1)/2,sh-bh-sh*0.1],
                                # TODO: simplify formulae, too lazy to do right now...
                                size=lambda sw,sh: [(sw*0.9)/3.1,64],
                                label="",
                                borderstyle="oldshadow",
                                )
        self.wmm_convert.addWidget(self.wmmc_btn1)
        
        self.wmmc_btn1._label.font_size=15
        self.wmmc_btn1.addAction("click",self.on_convertclick,1)
        
        # Add Button2
        self.wmmc_btn2 = peng3d.gui.Button("btn2",self.wmm_convert,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: [((sw*0.05)+(((sw*0.9)/3)*1))+((sw*0.9)/3-(sw*0.9)/3.1)/2,sh-bh-sh*0.1],
                                size=lambda sw,sh: [(sw*0.9)/3.1,64],
                                label="",
                                borderstyle="oldshadow",
                                )
        self.wmm_convert.addWidget(self.wmmc_btn2)
        
        self.wmmc_btn2._label.font_size=15
        self.wmmc_btn2.addAction("click",self.on_convertclick,2)
        
        # Add Button3
        self.wmmc_btn3 = peng3d.gui.Button("btn3",self.wmm_convert,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: [((sw*0.05)+(((sw*0.9)/3)*2))+((sw*0.9)/3-(sw*0.9)/3.1)/2,sh-bh-sh*0.1],
                                size=lambda sw,sh: [(sw*0.9)/3.1,64],
                                label="",
                                borderstyle="oldshadow",
                                )
        self.wmm_convert.addWidget(self.wmmc_btn3)
        
        self.wmmc_btn3._label.font_size=15
        self.wmmc_btn3.addAction("click",self.on_convertclick,3)
        
        # Add Cancel Button
        self.wmmc_cancel = peng3d.gui.Button("cancelbtn",self.wmm_convert,self.peng.window,self.peng,
                                pos=lambda sw,sh, bw,bh: [((sw*0.05)+(((sw*0.9)/3)*1))+((sw*0.9)/3-(sw*0.9)/3.1)/2,sh-bh*5-sh*0.1],
                                size=lambda sw,sh: [(sw*0.9)/3.1,64],
                                label="Cancel",
                                borderstyle="oldshadow",
                                )
        self.wmm_convert.addWidget(self.wmmc_cancel)
        
        def f():
            self.wmm_convert.visible=False
            self.curWorkspaceObj.visible=True
            # These are not necessary, they just prevent old labels from being shown in case of glitches
            self.wmmc_btn1.label=""
            self.wmmc_btn2.label=""
            self.wmmc_btn3.label=""
        self.wmmc_cancel.addAction("click",f)
    
    # Runtime code
    def reInitConvert(self):
        if self.wmm_convert.visible:
            return # Prevent it from being pressed too soon
        self.wmm_convert.visible = True
        if self.curWorkspace=="condensed":
            self.wmmc_btn1.label="IUPAC Name"
            self.wmmc_btn2.label="Lewis Structure"
            self.wmmc_btn3.label="Skeletal Formula"
        elif self.curWorkspace=="iupac":
            self.wmmc_btn1.label="Condensed Formula"
            self.wmmc_btn2.label="Lewis Structure"
            self.wmmc_btn3.label="Skeletal Formula"
        elif self.curWorkspace=="struct_lewis":
            self.wmmc_btn1.label="Condensed Formula"
            self.wmmc_btn2.label="IUPAC Name"
            self.wmmc_btn3.label="Skeletal Formula"
        elif self.curWorkspace=="struct_skeleton":
            self.wmmc_btn1.label="Condensed Formula"
            self.wmmc_btn2.label="IUPAC Name"
            self.wmmc_btn3.label="Lewis Structure"
        else:
            return # May cause errors later on
    
    def on_convertclick(self,btn):
        new_ws = None
        if self.curWorkspace=="condensed":
            if btn==1:
                new_ws="iupac"
            elif btn==2:
                new_ws="struct_lewis"
            elif btn==3:
                new_ws="struct_skeleton"
        elif self.curWorkspace=="iupac":
            if btn==1:
                new_ws="condensed"
            elif btn==2:
                new_ws="struct_lewis"
            elif btn==3:
                new_ws="struct_skeleton"
        elif self.curWorkspace=="struct_lewis":
            if btn==1:
                new_ws="condensed"
            elif btn==2:
                new_ws="iupac"
            elif btn==3:
                new_ws="struct_skeleton"
        elif self.curWorkspace=="struct_skeleton":
            if btn==1:
                new_ws="condensed"
            elif btn==2:
                new_ws="iupac"
            elif btn==3:
                new_ws="struct_lewis"
        
        self.wmm_convert.visible=False # Placed here to allow re-entering the dialog in case of error
        
        if new_ws is None:
            return # May cause errors later on
        
        self.setWorkspace(new_ws)
    
    def setWorkspace(self,workspace):
        if workspace==self.curWorkspace:
            return
        
        if self.curWorkspaceObj is not None:
            try:
                self.curWorkspaceObj.convert_to(workspace)
            except Exception:
                # Make the workspace visible again and print the stacktrace
                print("ERROR during conversion, aborting conversion:")
                self.curWorkspaceObj.visible=True
                traceback.print_exc()
                return
        
        if self.curWorkspace is None:
            pass
        else:
            self.curWorkspaceObj.visible=False
        
        if workspace=="condensed":
            self.wmm_condensed.visible = True
            self.curWorkspaceObj = self.wmm_condensed
        elif workspace=="iupac":
            self.wmm_iupac.visible = True
            self.curWorkspaceObj = self.wmm_iupac
        elif workspace=="struct_lewis":
            self.wmm_slewis.visible = True
            self.curWorkspaceObj = self.wmm_slewis
        elif workspace=="struct_skeleton":
            self.wmm_sskeleton.visible = True
            self.curWorkspaceObj = self.wmm_sskeleton
        else:
            self.curWorkspaceObj = None # may make it able to recover data
            return # Ignore, may hide current workspace
        self.curWorkspace = workspace
    
    def saveAs(self,fname):
        if fname is None:
            # In Case of Cancel
            return
        elif fname.endswith("smi") or fname.endswith("smiles"):
            # SMILES
            mimetype = "chemical/x-daylight-smiles"
        elif fname.endswith("inchi"):
            # InChI
            mimetype = "chemical/x-inchi"
        else:
            # Defaults to InChI
            mimetype = "chemical/x-inchi"
        
        print("Saving to mimetype %s"%mimetype)
        
        r = self.curWorkspaceObj.formula.dump(fname,mimetype)
        print(r)
    
    def loadFrom(self,fname):
        if fname is None:
            # In Case of Cancel
            return
        elif fname.endswith("smi") or fname.endswith("smiles"):
            # SMILES
            mimetype = "chemical/x-daylight-smiles"
        elif fname.endswith("inchi"):
            # InChI
            mimetype = "chemical/x-inchi"
        else:
            # Defaults to InChI
            mimetype = "chemical/x-inchi"
        
        print("Loading from mimetype %s"%mimetype)
        
        self.curWorkspaceObj.setFormula(self.curWorkspaceObj.formula.load(fname,mimetype))
        
        self.fname = fname # Makes exporting and saving easier
