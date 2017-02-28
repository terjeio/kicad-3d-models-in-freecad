# -*- coding: utf8 -*-
#!/usr/bin/python
#
# This is derived from a cadquery script for generating QFP models in X3D format.
#
# from https://bitbucket.org/hyOzd/freecad-macros
# author hyOzd
#
# Dimensions are from Jedec MS-026D document.

## requirements
## cadquery FreeCAD plugin
##   https://github.com/jmwright/cadquery-freecad-module

## to run the script just do: freecad make_qfn_export_fc.py modelName
## e.g. c:\freecad\bin\freecad make_qfn_export_fc.py QFN16

## the script will generate STEP and VRML parametric models
## to be used with kicad StepUp script

#* These are a FreeCAD & cadquery tools                                     *
#* to export generated models in STEP & VRML format.                        *
#*                                                                          *
#* cadquery script for generating QFP/SOIC/SSOP/TSSOP models in STEP AP214  *
#*   Copyright (c) 2015                                                     *
#* Maurice https://launchpad.net/~easyw                                     *
#* All trademarks within this guide belong to their legitimate owners.      *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU Lesser General Public License (LGPL)     *
#*   as published by the Free Software Foundation; either version 2 of      *
#*   the License, or (at your option) any later version.                    *
#*   for detail see the LICENCE text file.                                  *
#*                                                                          *
#*   This program is distributed in the hope that it will be useful,        *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
#*   GNU Library General Public License for more details.                   *
#*                                                                          *
#*   You should have received a copy of the GNU Library General Public      *
#*   License along with this program; if not, write to the Free Software    *
#*   Foundation, Inc.,                                                      *
#*   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA           *
#*                                                                          *
#****************************************************************************

__title__ = "make Radial Caps 3D models"
__author__ = "maurice and hyOzd"
__Comment__ = 'make Radial Caps 3D models exported to STEP and VRML for Kicad StepUP script'

___ver___ = "1.3.2 10/02/2017"

# thanks to Frank Severinsen Shack for including vrml materials

# maui import cadquery as cq
# maui from Helpers import show
from math import tan, radians, sqrt
from collections import namedtuple

import sys, os
import datetime
from datetime import datetime
sys.path.append("./exportVRML")
import exportPartToVRML as expVRML
import shaderColors

body_color_key = "blue body"
body_color = shaderColors.named_colors[body_color_key].getDiffuseFloat()
base_color_key = "black body"
base_color = shaderColors.named_colors[base_color_key].getDiffuseFloat()
pins_color_key = "metal grey pins"
pins_color = shaderColors.named_colors[pins_color_key].getDiffuseFloat()
mark_color_key = "light brown label"
mark_color = shaderColors.named_colors[mark_color_key].getDiffuseFloat()
top_color_key = "metal grey pins"
top_color = shaderColors.named_colors[mark_color_key].getDiffuseFloat()


# maui start
import FreeCAD, Draft, FreeCADGui
import ImportGui


outdir=os.path.dirname(os.path.realpath(__file__))
sys.path.append(outdir)

if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui

# Licence information of the generated models.
#################################################################################################
STR_licAuthor = "kicad StepUp"
STR_licEmail = "ksu"
STR_licOrgSys = "kicad StepUp"
STR_licPreProc = "OCC"
STR_licOrg = "FreeCAD"   

LIST_license = ["",]
#################################################################################################

#checking requirements
#######################################################################
FreeCAD.Console.PrintMessage("FC Version \r\n")
FreeCAD.Console.PrintMessage(FreeCAD.Version())
FC_majorV=FreeCAD.Version()[0];FC_minorV=FreeCAD.Version()[1]
FreeCAD.Console.PrintMessage('FC Version '+FC_majorV+FC_minorV+'\r\n')

if int(FC_majorV) <= 0:
    if int(FC_minorV) < 15:
        reply = QtGui.QMessageBox.information(None,"Warning! ...","use FreeCAD version >= "+FC_majorV+"."+FC_minorV+"\r\n")


# FreeCAD.Console.PrintMessage(all_params_soic)
FreeCAD.Console.PrintMessage(FreeCAD.ConfigGet("AppHomePath")+'Mod/')
file_path_cq=FreeCAD.ConfigGet("AppHomePath")+'Mod/CadQuery'
if os.path.exists(file_path_cq):
    FreeCAD.Console.PrintMessage('CadQuery exists\r\n')
else:
    file_path_cq=FreeCAD.ConfigGet("UserAppData")+'Mod/CadQuery'
    if os.path.exists(file_path_cq):
        FreeCAD.Console.PrintMessage('CadQuery exists\r\n')
    else:
        msg="missing CadQuery Module!\r\n\r\n"
        msg+="https://github.com/jmwright/cadquery-freecad-module/wiki"
        reply = QtGui.QMessageBox.information(None,"Info ...",msg)

#######################################################################

# CadQuery Gui
from Gui.Command import *

# Import cad_tools
import cq_cad_tools
# Reload tools
reload(cq_cad_tools)
# Explicitly load all needed functions
from cq_cad_tools import FuseObjs_wColors, GetListOfObjects, restore_Main_Tools, \
 exportSTEP, close_CQ_Example, exportVRML, saveFCdoc, z_RotateObject, Color_Objects, \
 CutObjs_wColors

# Gui.SendMsgToActiveView("Run")
Gui.activateWorkbench("CadQueryWorkbench")
import FreeCADGui as Gui

try:
    close_CQ_Example(App, Gui)
except: # catch *all* exceptions
    print "CQ 030 doesn't open example file"


# from export_x3d import exportX3D, Mesh
import cadquery as cq
from Helpers import show
# maui end

#check version
cqv=cq.__version__.split(".")
#say2(cqv)
if int(cqv[0])==0 and int(cqv[1])<3:
    msg = "CadQuery Module needs to be at least 0.3.0!\r\n\r\n"
    reply = QtGui.QMessageBox.information(None, "Info ...", msg)
    say("cq needs to be at least 0.3.0")
    stop

if float(cq.__version__[:-2]) < 0.3:
    msg="missing CadQuery 0.3.0 or later Module!\r\n\r\n"
    msg+="https://github.com/jmwright/cadquery-freecad-module/wiki\n"
    msg+="actual CQ version "+cq.__version__
    reply = QtGui.QMessageBox.information(None,"Info ...",msg)

import cq_params_radial_smd_cap  # modules parameters
from cq_params_radial_th_cap import *

all_params = all_params_radial_th_cap
# all_params = kicad_naming_params_radial_th_cap

def make_radial_th(params):

    L = params.L    # overall height
    D = params.D    # body diameter
    d = params.d     # lead diameter
    F = params.F     # lead separation (center to center)
    ll = params.ll   # lead length
    la = params.la   # extra lead length of the anode
    bs = params.bs   # board separation

    bt = 1.        # flat part before belt
    bd = 0.2       # depth of the belt
    bh = 1.        # height of the belt
    bf = 0.3       # belt fillet

    tc = 0.2       # cut thickness for the bottom&top
    dc = D*0.7     # diameter of the bottom&top cut
    ts = 0.1       # thickness of the slots at the top in the shape of (+)
    ws = 0.1       # width of the slots

    ef = 0.2       # top and bottom edges fillet
    rot = params.rotation
    dest_dir_pref = params.dest_dir_prefix

    bpt = 0.1        # bottom plastic thickness (not visual)
    tmt = ts*2       # top metallic part thickness (not visual)

    # TODO: calculate width of the cathode marker bar from the body size
    ciba = 45.  # angle of the cathode identification bar

    # TODO: calculate marker sizes according to the body size
    mmb_h = 2.       # lenght of the (-) marker on the cathode bar
    mmb_w = 0.5      # rough width of the marker

    ef_s2 = ef/sqrt(2)
    ef_x = ef-ef/sqrt(2)
    
    def bodyp():
        return cq.Workplane("XZ").move(0, bs).\
               move(0, tc+bpt).\
               line(dc/2., 0).\
               line(0, -(tc+bpt)).\
               line(D/2.-dc/2.-ef, 0).\
               threePointArc((D/2.-(ef_x), bs+(ef_x)), (D/2., bs+ef)).\
               line(0, bt).\
               threePointArc((D/2.-bd, bs+bt+bh/2.), (D/2., bs+bt+bh)).\
               lineTo(D/2., L+bs-ef).\
               threePointArc((D/2.-(ef_x), L+bs-(ef_x)), (D/2.-ef, L+bs)).\
               lineTo(dc/2., L+bs).\
               line(0, -(tc+tmt)).\
               line(-dc/2., 0).\
               close()

    body = bodyp().revolve(360-ciba, (0,0,0), (0,1,0))
    bar = bodyp().revolve(ciba, (0,0,0), (0,1,0))

    # # fillet the belt edges
    BS = cq.selectors.BoxSelector
    # note that edges are selected from their centers
    body = body.edges(BS((-0.5,-0.5, bs+bt-0.01), (0.5, 0.5, bs+bt+bh+0.01))).\
           fillet(bf)
    b_r = D/2.-bd # inner radius of the belt
    bar = bar.edges(BS((b_r/sqrt(2), 0, bs+bt-0.01),(b_r, -b_r/sqrt(2), bs+bt+bh+0.01))).\
          fillet(bf)

    body = body.rotate((0,0,0), (0,0,1), 180-ciba/2)
    bar = bar.rotate((0,0,0), (0,0,1), 180+ciba/2)

    # draw the plastic at the bottom
    bottom = cq.Workplane("XY").workplane(offset=bs+tc).\
             circle(dc/2).extrude(bpt)

    # draw the metallic part at the top
    top = cq.Workplane("XY").workplane(offset=bs+L-tc-ts).\
         circle(dc/2).extrude(tmt)

    # draw the slots on top in the shape of plus (+)
    top = top.faces(">Z").workplane().move(ws/2,ws/2).\
          line(0,D).line(-ws,0).line(0,-D).\
          line(-D,0).line(0,-ws).line(D,0).\
          line(0,-D).line(ws,0).line(0,D).\
          line(D,0).line(0,ws).close().cutBlind(-ts)

    # draw the (-) marks on the bar
    n = int(L/(2*mmb_h)) # number of (-) marks to draw
    points = []
    first_z = (L-(2*n-1)*mmb_h)/2
    for i in range(n):
        points.append((0, (i+0.25)*2*mmb_h+first_z))
    mmb = cq.Workplane("YZ", (-D/2,0,bs)).pushPoints(points).\
          box(mmb_w, mmb_h, 2).\
          edges("|X").fillet(mmb_w/2.-0.001)

    mmb = mmb.cut(mmb.translate((0,0,0)).cut(bar))
    bar = bar.cut(mmb)

    # draw the leads
    leads = cq.Workplane("XY").workplane(offset=bs+tc).\
            center(-F/2,0).circle(d/2).extrude(-(ll+tc)).\
            center(F,0).circle(d/2).extrude(-(ll+tc+la+0.1)).translate((0,0,0.1)) #need overlap for fusion

    
    #show(body)
    #show(mmb)
    #show(bar)
    #show(leads)
    #show(top)
    #stop
    return (body, mmb, bar, leads, top) #body, base, mark, pins, top

    
#import step_license as L
import add_license as Lic

if __name__ == "__main__":
    expVRML.say(expVRML.__file__)
    FreeCAD.Console.PrintMessage('\r\nRunning...\r\n')

# maui     run()
    color_pin_mark=True
    if len(sys.argv) < 3:
        FreeCAD.Console.PrintMessage('No variant name is given! building qfn16')
        model_to_build='L10_D5'
    else:
        model_to_build=sys.argv[2]
        if len(sys.argv)==4:
            FreeCAD.Console.PrintMessage(sys.argv[3]+'\r\n')
            if (sys.argv[3].find('no-pinmark-color')!=-1):
                color_pin_mark=False
            else:
                color_pin_mark=True
    if model_to_build == "all":
        variants = all_params.keys()
    else:
        variants = [model_to_build]

    for variant in variants:
        FreeCAD.Console.PrintMessage('\r\n'+variant)
        if not variant in all_params:
            print("Parameters for %s doesn't exist in 'all_params', skipping." % variant)
            continue
        ModelName = all_params[variant].modelName
        CheckedModelName = ModelName.replace('.', '')
        CheckedModelName = CheckedModelName.replace('-', '_')
        Newdoc = FreeCAD.newDocument(CheckedModelName)
        App.setActiveDocument(CheckedModelName)
        Gui.ActiveDocument=Gui.getDocument(CheckedModelName)
        #body, base, mark, pins = make_radial_th(all_params[variant])
        body, base, mark, pins, top = make_radial_th(all_params[variant]) #body, base, mark, pins, top
        
        
        show(body)
        show(base)
        show(pins)
        show(mark)
        show(top)
        
        
        doc = FreeCAD.ActiveDocument
        objs = GetListOfObjects(FreeCAD, doc)

        Color_Objects(Gui,objs[0],body_color)
        Color_Objects(Gui,objs[1],base_color)
        Color_Objects(Gui,objs[2],pins_color)
        Color_Objects(Gui,objs[3],mark_color)
        Color_Objects(Gui,objs[4],top_color)

        col_body=Gui.ActiveDocument.getObject(objs[0].Name).DiffuseColor[0]
        col_base=Gui.ActiveDocument.getObject(objs[1].Name).DiffuseColor[0]
        col_pin=Gui.ActiveDocument.getObject(objs[2].Name).DiffuseColor[0]
        col_mark=Gui.ActiveDocument.getObject(objs[3].Name).DiffuseColor[0]
        col_top=Gui.ActiveDocument.getObject(objs[4].Name).DiffuseColor[0]
        material_substitutions={
            col_body[:-1]:body_color_key,
            col_base[:-1]:base_color_key,
            col_pin[:-1]:pins_color_key,
            col_mark[:-1]:mark_color_key,
            col_top[:-1]:top_color_key
        }
        expVRML.say(material_substitutions)

        del objs
        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[2].Name, objs[3].Name)
        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)    
        objs=GetListOfObjects(FreeCAD, doc)
        FuseObjs_wColors(FreeCAD, FreeCADGui, doc.Name, objs[0].Name, objs[1].Name)    
        #stop
        doc.Label=ModelName
        objs=GetListOfObjects(FreeCAD, doc)
        objs[0].Label=ModelName
        restore_Main_Tools()
        #rotate if required
        if (all_params[variant].rotation!=0):
            rot= all_params[variant].rotation
            z_RotateObject(doc, rot)
        #out_dir=destination_dir+all_params[variant].dest_dir_prefix+'/'
        script_dir=os.path.dirname(os.path.realpath(__file__))
        expVRML.say(script_dir)
        out_dir=script_dir+os.sep+destination_dir+os.sep+all_params[variant].dest_dir_prefix
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        #out_dir="./generated_qfp/"
        # export STEP model
        exportSTEP(doc, ModelName, out_dir)
        Lic.addLicenseToStep(out_dir+'/', ModelName+".step", LIST_license,\
                           STR_licAuthor, STR_licEmail, STR_licOrgSys, STR_licOrg, STR_licPreProc)

        # scale and export Vrml model
        scale=1/2.54
        #exportVRML(doc,ModelName,scale,out_dir)
        objs=GetListOfObjects(FreeCAD, doc)
        expVRML.say("######################################################################")
        expVRML.say(objs)
        expVRML.say("######################################################################")
        export_objects, used_color_keys = expVRML.determineColors(Gui, objs, material_substitutions)
        export_file_name=out_dir+os.sep+ModelName+'.wrl'
        colored_meshes = expVRML.getColoredMesh(Gui, export_objects , scale)
        if LIST_license[0]=="":
            LIST_license=Lic.LIST_int_license
            LIST_license.append("")
        expVRML.writeVRMLFile(colored_meshes, export_file_name, used_color_keys, LIST_license)
        # Save the doc in Native FC format
        saveFCdoc(App, Gui, doc, ModelName,out_dir)
        #display BBox
        #FreeCADGui.ActiveDocument.getObject("Part__Feature").BoundingBox = True
        Gui.activateWorkbench("PartWorkbench")
        Gui.SendMsgToActiveView("ViewFit")
        Gui.activeDocument().activeView().viewAxometric()