'''
Header

Name:
mm_sh_toolset.py

Created by: Matt Malley
E-mail: contact@radiant-entertainment.com

How to Run in Maya:  Copy/Paste this into Maya (or create as a button):
import maya.cmds as cmds
cmds.unloadPlugin("mm_sh_toolset.py")
cmds.loadPlugin("mm_sh_toolset.py")
cmds.mm_sh_toolset()


Project Description:
This script is to assist in asset creation.
   
Final Toolset:
There are multiple tabs: Modeling, Organization, UV Tools, Rigging, and SH Unique functions.
Each has a variety of useful buttons which fit their tab's description.


'''

__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
#-------------------------------------------------------------------------------
#Imports Maya command information

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import os
import sys
import maya.OpenMayaMPx as OpenMayaMPx

#-------------------------------------------------------------------------------
#Import all individual scripts

import mmAddAttr as mmAA
import mmConvert3DSMaxRigToMayaRig as mmCM2M
import mmCreateLocAndParent as mmCLAP
import mmExportAnimationAsJson as mmEAAJ
import mmExportSkeletonAsJson as mmESAJ
import mmGetWorldTrans as mmGWT
import mmScaleDownFrom3DSMax as mmSDF3M
import mmModelingFunctions as mmMF
import mmOrganizationFunctions as mmOF
import mmOverrideVisual as mmOV
import mmReplaceMeshWithObj as mmRMWO
import mmReturnFilepathOrFilename as mmRFOF
import mmRiggingFunctions as mmRF
import mmSelectAnimatingParts as mmSAP
import mmTransferAnimToDifferentRig as mmTATDR
import mmTransferAnimToReferencedRig as mmTATRR
import mmUVFunctions as mmUVF
import mmBubbleSoft as mmBS
import mmMassConversionFunctions as mmMCF
import mmSpaceMatcher as mmSM
import mmValueSwapper as mmVS



reload( mmAA )
reload( mmCM2M )
reload( mmCLAP )
reload( mmEAAJ )
reload( mmESAJ )
reload( mmGWT )
reload( mmSDF3M )
reload( mmMF )
reload( mmOF )
reload( mmOV )
reload( mmRMWO )
reload( mmRFOF )
reload( mmRF )
reload( mmSAP )
reload( mmTATDR )
reload( mmTATRR )
reload( mmUVF )
reload( mmBS )
reload( mmMCF )
reload( mmSM )
reload( mmVS )

######################################
############# CLASSES ################
######################################

mmPluginCmdName = "mm_sh_toolset"

# Command
class mmScriptedCommand(OpenMayaMPx.MPxCommand):
   def __init__(self):
      OpenMayaMPx.MPxCommand.__init__(self)
     
   # Invoked when the command is run.
   def doIt(self,argList):
      gui()


######################################
############# DEFINES ################
######################################


# Creator
def mmCreator():
   return OpenMayaMPx.asMPxPtr( mmScriptedCommand() )

# Initialize the script plug-in
def initializePlugin(mobject):
   mplugin = OpenMayaMPx.MFnPlugin(mobject)
   try:
      mplugin.registerCommand( mmPluginCmdName, mmCreator )
   except:
      sys.stderr.write( "Failed to register command: %s\n" % mmPluginCmdName )
      raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
   mplugin = OpenMayaMPx.MFnPlugin(mobject)
   try:
      mplugin.deregisterCommand( mmPluginCmdName )
   except:
      sys.stderr.write( "Failed to unregister command: %s\n" % mmPluginCmdName )


#-------------------------------------------------------------------------------


#Function which creates and displays GUI
def gui():
   mmCompareList = 0
   
   #Check to see if a window currently exists, and delete it if it does
   if (cmds.window("sh_toolset_window", exists=1)):
     cmds.deleteUI("sh_toolset_window")
     cmds.windowPref("sh_toolset_window", r=True)

   #Create window, and set top left corner
   cmds.window("sh_toolset_window", title = "Stonehearth Toolset",
     w = 400, h = 300, resizeToFitChildren = True)
   cmds.windowPref("sh_toolset_window", te = 0, le = 0)
   
   #Adds a Tab Functionality to the Main Window
   mmForm = cmds.formLayout("basicFormLayout")
   mmTabs = cmds.tabLayout("mmTabs", innerMarginWidth=5, innerMarginHeight=5, scr = 1, w = 500, h = 300,
     cc = setWinHeight)
   cmds.formLayout( mmForm, edit=True, attachForm=((mmTabs, 'top', 0), (mmTabs, 'left', 0),
     (mmTabs, 'bottom', 0), (mmTabs, 'right', 0)) )


#-------------------------------------------------------------------------------

#Stonehearth Buttons

#-------------------------------------------------------------------------------

   '''

   #Creates a new rowColumn Layout for design purposes
   #This is a larger set up than needed, and inside it should be multiple smaller UI menus
   cmds.rowColumnLayout("orgLayout2", numberOfColumns = 3, cw= [[1,150],[2,150],[3,150]],
     cal = [1,"center"])
   curWinHeight += cmds.rowColumnLayout("orgLayout2", q = 1, h = 1)

   '''

   #Creates a base window height value to determine the Tab's required Height
   #Subsequent additions to this value are adding up to the total height required
   curWinHeight = 0
   curWinHeightColumn1 = 0
   curWinHeightColumn2a = 0
   curWinHeightColumn2b = 0
   
   #Creates a Collapsable Shelf to Hide/Show the items inside
   SH_FrLayout = cmds.columnLayout("SH_BasicFrame")
   curWinHeightColumn1 += cmds.columnLayout("SH_BasicFrame", q = 1, h = 1)
   curWinHeightColumn1 += 30

   #Creates a new frame and rowColumn set for the Normal buttons and fields
   SH_RoCoLayout = cmds.frameLayout("SH_Buttons", label = "SH Buttons", cll = 1)
   curWinHeightColumn1 += cmds.frameLayout("SH_Buttons", q = 1, h = 1)
   curWinHeightColumn1 += 30
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_Overall", numberOfColumns = 2, cw= [[1, 150], [2, 300]])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout_Overall", q = 1, h = 1)

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnOne", numberOfColumns = 1, cw= [1, 150])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnOne", q = 1, h = 1)

   #Creates a new frame and rowColumn set for the Normal buttons and fields
   SH_RoCoLayout = cmds.frameLayout("Animation_Scripts", label = "Anim Scripts", cll = 1)
   curWinHeightColumn1 += cmds.frameLayout("Animation_Scripts", q = 1, h = 1)
   curWinHeightColumn1 += 30

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout", numberOfColumns = 2, cw= [[1,75],[2,75]])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout", q = 1, h = 1)

   #Button: Calls function to set up the UI as I want
   cmds.button ( label = "Viewport Fix", command = mmCM2M.mmFixUI, w = 75, h = 25)
   
   #Button: Calls function to set any selected object to world location
   cmds.button ( label = "Set to World", command = mmGWT.main, w = 75, h = 25)
   curWinHeightColumn1 += 10
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayoutB", numberOfColumns = 1, cw= [1,150])
   
   #Button: Calls function to add visibility toggling to a rig specifically created in the way described in this file.
   cmds.button ( label = "Toggle Vis of Self", command = mmCM2M.mmToggleVisOptionOnSelf, w = 75, h = 25)
   
   #Button: Calls function to add visibility toggling to a rig specifically created in the way described in this file.
   cmds.button ( label = "Toggle Vis of Children", command = mmCM2M.mmToggleVisOptionOnChildren, w = 75, h = 25)

   #End the previous rowColumn
   cmds.setParent("..")
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn1 += 10
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout2Title", numberOfColumns = 1, cw= [1,150])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout2Title", q = 1, h = 1)

   cmds.text("Animation Scripts")
   curWinHeightColumn1 += 50
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout2", numberOfColumns = 2, cw= [[1,75],[2,75]])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout2", q = 1, h = 1)

   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "Export Anim", command = mmEAAJ.mainCall, w = 75, h = 25)
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "Export Skele", command = mmESAJ.mainCall, w = 75, h = 25)

   #End the previous rowColumn
   cmds.setParent("..")
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout2B", numberOfColumns = 1, cw= [1,150])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout2B", q = 1, h = 1)

   #Button: Calls function to Transfer Animation from a 3DSMax Rig onto a Referenced Rig
   cmds.button ( label = "XFER Anim to Referenced Rig", command = mmTATRR.main, w = 150, h = 25)
      
   #Button: Calls function to Transfer Animation from a 3DSMax Rig onto a Different Rig
   cmds.button ( label = "XFER Anim to Different Rig", command = mmTATDR.main, w = 150, h = 25)

   #Button: Calls function to load any references which are currently not loaded - can do the same thing in the Reference Editor,
   #  This just saves some clicks.
   cmds.button ( label = "Load any non-loaded Refs", command = mmCM2M.mmLoadAllReferences, w = 150, h = 25)

   #Button: Calls function to load any references which are currently not loaded - can do the same thing in the Reference Editor,
   #  This just saves some clicks.
   cmds.button ( label = "SpaceMatcher Copy", command = mmSM.mmCopySpace, w = 150, h = 25)

   #Button: Calls function to load any references which are currently not loaded - can do the same thing in the Reference Editor,
   #  This just saves some clicks.
   cmds.button ( label = "SpaceMatcher Paste", command = mmSM.mmPasteSpace, w = 150, h = 25)

   ##############

   cmds.separator( height=10, style='in' )
   curWinHeightColumn1 += 10

   cmds.text("Select two items then\nclick button to swap\ntheir values.")
   curWinHeightColumn1 += 50

   #Creates a new rowColumn Layout for a value swapper purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout2C", numberOfColumns = 6, cw= [[1,25],[2,25],[3,25],[4,25],[5,25],[6,25]])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout2C", q = 1, h = 1)


   #Buttons for translation swapping
   #  This just saves some clicks.
   cmds.button ( label = "TX", command = mmVS.mmSwapTransX, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "TY", command = mmVS.mmSwapTransY, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "TZ", command = mmVS.mmSwapTransZ, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-TX", command = mmVS.mmNegativeTransX, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-TY", command = mmVS.mmNegativeTransY, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-TZ", command = mmVS.mmNegativeTransZ, w = 20, h = 25)


   #Buttons for rotation swapping
   #  This just saves some clicks.
   cmds.button ( label = "RX", command = mmVS.mmSwapRotX, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "RY", command = mmVS.mmSwapRotY, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "RZ", command = mmVS.mmSwapRotZ, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-RX", command = mmVS.mmNegativeRotX, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-RY", command = mmVS.mmNegativeRotY, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-RZ", command = mmVS.mmNegativeRotZ, w = 20, h = 25)


   #Buttons for scale swapping
   #  This just saves some clicks.
   cmds.button ( label = "SX", command = mmVS.mmSwapScaleX, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "SY", command = mmVS.mmSwapScaleY, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "SZ", command = mmVS.mmSwapScaleZ, w = 20, h = 25)

   cmds.button ( label = "-SX", command = mmVS.mmNegativeScaleX, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-SY", command = mmVS.mmNegativeScaleY, w = 20, h = 25)

   #  This just saves some clicks.
   cmds.button ( label = "-SZ", command = mmVS.mmNegativeScaleZ, w = 20, h = 25)


   #End the previous rowColumn
   cmds.setParent("..")
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn1 += 10

   #-------------------------------------------------------------------------------
   
   #Creates a new frame and rowColumn set for the Normal buttons and fields
   SH_RoCoLayout = cmds.frameLayout("Rigging_Scripts", label = "Rig Adjust Scripts", cll = 1)
   # Add "cl = 1" to have the collapsable windows start collapsed
   curWinHeightColumn1 += cmds.frameLayout("Rigging_Scripts", q = 1, h = 1)
   curWinHeightColumn1 += 30
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout3", numberOfColumns = 2, cw= [[1,75],[2,75]])
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout3", q = 1, h = 1)

   #Button: Calls function to Set the Visual Override of a piece of Geo to display properly.
   #-------This button is only needed in rare cicrumstances - this function will be called automatically
   #              during the Rig Converter script.
   cmds.button ( label = "Vis Override", command = mmOV.run, w = 75, h = 25)

   #Button: Calls function to toggle geo for manipulation or to lock it as a reference.  For most animations, should not be needed.
   cmds.button ( label = "Geo Lock Tog", command = mmCM2M.mmToggleGeoManipulation, w = 75, h = 25)

   #End the previous rowColumn
   cmds.setParent("..")
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout3A", numberOfColumns = 1, cw= [1,150])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout3A", q = 1, h = 1)
   
   #Button: Calls function to create a Locator at the selected object's pivot and then parent the object to the loc
   cmds.button ( label = "Add Selected Mesh to Rig", command = mmCLAP.main, w = 150, h = 25)

   
   #Button: Calls function to create a Locator at the selected object's pivot and then parent the object to the loc
   cmds.button ( label = "Group Selection in Place", command = mmOF.mmCallGroupInPlace, w = 150, h = 25)
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn1 += 10
   
   cmds.text("To add a View-Only item\nto main or offhand bone,\nfirst reference in meshes,\nselect bone, ref meshes,\nthen click add button.")
   curWinHeightColumn1 += 50

   #Button: Calls function to load in a mesh as a referenced file.
   cmds.button ( label = "Select an Item to Reference", command = mmCM2M.mmCallBringInReference, w = 75, h = 25)

   #Button: Calls function take selection of bone and referenced meshes, and adds referenced meshes to the rig as view-only meshes,
   #  with controls to only view one at a time.
   cmds.button ( label = "Add View-Only Helper to Rig", command = mmCM2M.mmAddItemToRig, w = 75, h = 25)

   #End the previous rowColumn
   cmds.setParent("..")

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout3B", numberOfColumns = 1, cw= [1,150])
   
   curWinHeightColumn1 += cmds.rowColumnLayout("mm_SH_RoCoLayout3B", q = 1, h = 1)
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn1 += 10
   
   cmds.text("Geo Modification")
   curWinHeightColumn1 += 50

   #Button: Calls function to replace the mesh objects of a rig file with an obj pulled in from some location.
   cmds.button ( label = "Select OBJ to replace Meshes", command = mmRMWO.main, w = 75, h = 25)

   #Button: Calls function to create a Locator at the selected object's pivot and then parent the object to the loc
   cmds.button ( label = "Select OBJ to Load into Scene", command = mmCM2M.mmBringInObj, w = 75, h = 25)

   #Button: Calls function to create a Locator at the selected object's pivot and then parent the object to the loc
   cmds.button ( label = "Clean Selected Meshes", command = mmCM2M.mmCleanMesh, w = 75, h = 25)

   #Bubble soft will make all selected meshes look poofy
   cmds.button ( label = "BubbleSoft", command = mmBS.main, w = 75, h = 25)
   curWinHeightColumn1 += 10
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #End the previous rowColumn
   cmds.setParent("..")

   #End the previous rowColumn
   cmds.setParent("..")
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #-------------------------------------------------------------------------------
   
   #Creates a new frame and rowColumn set for the Normal buttons and fields
   SH_RoCoLayout = cmds.frameLayout("Rig_Creation_Scripts", label = "Rig Creation Scripts", cll = 1)
   curWinHeightColumn2a += cmds.frameLayout("Rig_Creation_Scripts", q = 1, h = 1)
   curWinHeightColumn2a += 30
   
   #Button: Calls function to create a Locator at the selected object's pivot and then parent the object to the loc
   cmds.button ( label = "Select OBJ to Load into Scene", command = mmCM2M.mmBringInObj, w = 75, h = 25)

   cmds.separator( height=10, style='in' )
   curWinHeightColumn2a += 10

   #Column for setting up a file to be ready for the rig creators
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnTwoPreface", numberOfColumns = 2, cw= [[1, 150],[2, 150]])
      
   cmds.text("When creating a new rig:\nrun Set Up Function (to right),\nthen move your pivots, and\narrange your hierarchy.")
   curWinHeightColumn2a += 50

   #Button: Calls all Rig Creation Functions without extra input
   cmds.button ( label = "Set Up Scene for Rigging", command = mmCM2M.mmRigPrep, w = 75, h = 25)

   #Check Box Group to decide what should be included in Hand System
   cmds.checkBoxGrp("centerPivotsChkBox", numberOfCheckBoxes=1, label='Center Pivots?', label1='Center', v1 = 1, adj = 1, cw2 = [75,75], w = 150, cl2 = ["center","center"], vr =1)
   curWinHeight += 25
   
   #Button: Calls all Rig Creation Functions without extra input
   cmds.button ( label = "Clean Mesh Names if Needed", command = mmCM2M.mmMeshNameFixer, w = 75, h = 25)

   #End the previous rowColumn
   cmds.setParent("..")

   cmds.separator( height=10, style='in' )
   curWinHeightColumn2a += 10

   cmds.text("At this point, be sure to add a COG icon if you want one.")
   curWinHeightColumn2a += 50
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2a += 10

   cmds.text("When converting from Max to Maya, skip Set Up Function.")
   curWinHeightColumn2a += 50
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2a += 10

   #Column for creating "Human" Rigs - so Male, Female, Goblin
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnTwoHolder", numberOfColumns = 2, cw= [[1, 150],[2, 150]])
   
   curWinHeightColumn2a += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnTwoHolder", q = 1, h = 1)
   
   #Column for creating "Human" Rigs - so Male, Female, Goblin
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnTwo", numberOfColumns = 1, cw= [1, 150])
   
   curWinHeightColumn2a += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnTwo", q = 1, h = 1)

   cmds.text("Human Rig Creator:")
   curWinHeightColumn2a += 50
   
   cmds.text("Convert Rig from Max to Maya\nor Create a new Human Rig\nfrom an OBJ")
   curWinHeightColumn2a += 50
   
   #Button: Calls all Rig Creation Functions without extra input
   cmds.button ( label = "Run All", command = mmCM2M.mmHumanRigRunAll, w = 75, h = 25)
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2a += 10
   
   ####
   #Separating out the various steps
   ####

   #Can't figure out how to input various entries.. and doesn't matter atm, so skipping the step by step for now.
   cmds.text("Separating Out Steps:")
   curWinHeightColumn2a += 50
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "Step 1 - Prep", command = mmCM2M.mmHumanRigRunStep1, w = 75, h = 25)
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------

   cmds.text("Select Left Foot,\nthen Left Toe,\nthen Click:")
   curWinHeightColumn2a += 50
   
   cmds.button ( label = "Step 2 - Foot/Clav", command = mmCM2M.mmHumanRigRunStep2, w = 75, h = 25)

   #Button: Calls function to Transfer Animation from a 3DSMax Rig onto a Referenced Rig
   cmds.button ( label = "Step 3 - Place Rig", command = mmCM2M.mmHumanRigRunStep3, w = 75, h = 25)
      
   #Button: Calls function to Transfer Animation from a 3DSMax Rig onto a Referenced Rig
   cmds.button ( label = "Step 4 - Completion", command = mmCM2M.mmHumanRigRunStep4, w = 75, h = 25)
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2a += 10
   
   #Button: Calls function to Attach standard view-only models to human rigs.
   #  This is separated because you cannot undo the referencing in of models - which is important just from a rig creation standpoint (sanity).
   cmds.button ( label = "Load in Standard View Onlys", command = mmCM2M.mmLoadAllViewOnlyHelpersHumanRig, w = 75, h = 25)
   
   #Button: Calls function to add scale to a rig specifically created in the way described in this file.
   cmds.button ( label = "Add Scale to Rig", command = mmCM2M.mmAddScaleToRig, w = 75, h = 25)
     
   cmds.text("Remove VisLock\nso it can Toggle")
   curWinHeightColumn2a += 50

   #Button: Calls function to add scale to a rig specifically created in the way described in this file.
   cmds.button ( label = "Remove Vis Lock", command = mmCM2M.mmRemoveVisLock, w = 75, h = 25)
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2a += 10
   
   #Button: Calls function to add scale to a rig specifically created in the way described in this file.
   cmds.button ( label = "Dissassemble Rig", command = mmCM2M.mmDissassembleRig, w = 75, h = 25)
   
   #End the previous rowColumn
   cmds.setParent("..")

#-------------------------------------------------------------------------------

   #Column for creating all other rigs
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThree", numberOfColumns = 1, cw= [1, 150])
   
   curWinHeightColumn2b += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThree", q = 1, h = 1)

   cmds.text("Generic Rig Creator:")
   #curWinHeight += 50
   
   cmds.text("Convert Rig from Max to Maya\nor Create a new Generic Rig\nfrom an OBJ")
   #curWinHeight += 50
   
   #Button: Calls all Rig Creation Functions without extra input
   cmds.button ( label = "Run All", command = mmCM2M.mmGenericRunAll, w = 75, h = 25)
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2b += 10

   ####
   #Separating out the various steps
   ####

   #Can't figure out how to input various entries.. and doesn't matter atm, so skipping the step by step for now.
   cmds.text("Separating Out Steps:")
   curWinHeightColumn2b += 50
   
   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "Step 1 - Prep", command = mmCM2M.mmGenericRigRunStep1, w = 75, h = 25)
      
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2b += 10
   
   cmds.text("Optional Limb/Foot Creation")

   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "Create Trash Limb Locator", command = mmCM2M.mmCreateTrashLimbLoc, w = 75, h = 25)
   
   #Little Column for the chest and pelvis
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeA", numberOfColumns = 2, cw= [[1, 75],[2, 75]])
   curWinHeightColumn2b += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeA", q = 1, h = 1)

   cmds.text("Mirror Limb?")

   #Pin UVs option of Unfold Button
   cmds.radioButtonGrp( "mmLimb_MirrorCheckBox", nrb = 2, vr = 0, labelArray2 = ["Yes", "No"], sl = 1, ct2 = ["center","center"], cl2 = ["center","center"], adj = 1, co2 = [-3, 0] )
   curWinHeightColumn2b += cmds.radioButtonGrp("mmLimb_MirrorCheckBox", q = 1, h = 1)

   cmds.text("Include Foot?")

   #Pin UVs option of Unfold Button
   cmds.radioButtonGrp( "mmLimb_FootCheckBox", nrb = 2, vr = 0, labelArray2 = ["Yes", "No"], sl = 1, ct2 = ["center","center"], cl2 = ["center","center"], adj = 1, co2 = [-3, 0] )
   curWinHeightColumn2b += cmds.radioButtonGrp("mmLimb_FootCheckBox", q = 1, h = 1)

   cmds.text("Include Toe?")

   #Pin UVs option of Unfold Button
   cmds.radioButtonGrp( "mmLimb_ToeCheckBox", nrb = 2, vr = 0, labelArray2 = ["Yes", "No"], sl = 2, ct2 = ["center","center"], cl2 = ["center","center"], adj = 1, co2 = [-3, 0] )
   curWinHeightColumn2b += cmds.radioButtonGrp("mmLimb_ToeCheckBox", q = 1, h = 1)

   #End the previous rowColumn
   cmds.setParent("..")

   cmds.text("Select only LEFT limb pieces\nfrom furthest extremity to\npart closest to body.")

   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "Single Limb Primer", command = mmCM2M.mmGenericRigAddFeet, w = 75, h = 25)
   
   cmds.separator( height=10, style='in' )
   curWinHeightColumn2b += 10
   
   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "Step 2 - Partial Rig", command = mmCM2M.mmGenericRigRunStep2, w = 75, h = 25)

   cmds.separator( height=10, style='in' )
   curWinHeightColumn2b += 10
   
   #Little Column for the chest and pelvis
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeB", numberOfColumns = 2, cw= [[1, 75],[2, 75]])
   curWinHeightColumn2b += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeB", q = 1, h = 1)

   cmds.text("Define Group")

   #TextField to set which spine control we are working with
   cmds.intField("mmCreateSpineGroupValue", w = 75, h = 25, v = 1)
   curWinHeightColumn2b += 5

   #End the previous rowColumn
   cmds.setParent("..")

   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "Optional Spine Controls", command = mmCM2M.mmGenericRigAddSpine, w = 75, h = 25)

   #Little Column for the chest and pelvis
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeC", numberOfColumns = 2, cw= [[1, 75],[2, 75]])
   curWinHeightColumn2b += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeC", q = 1, h = 1)

   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Matcher", command = mmOF.mmCallMoveObject, w = 50, h = 25)
   curWinHeightColumn2b += 5

   cmds.text("Matcher will\nmatch the first\nselection to\nthe second's\nposition")

   #End the previous rowColumn
   cmds.setParent("..")

   cmds.text("Start should be +Z from End")

   #Little Column for the chest and pelvis
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeD", numberOfColumns = 3, cw= [[1, 50],[2, 50],[3, 50]])
   curWinHeightColumn2b += cmds.rowColumnLayout("mm_SH_RoCoLayout_ColumnThreeD", q = 1, h = 1)
   
   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Tag Start", command = mmCM2M.mmTagStartObject, w = 50, h = 25)
   curWinHeightColumn2b += 5

   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Tag Mid", command = mmCM2M.mmTagMidObject, w = 50, h = 25)
   curWinHeightColumn2b += 5

   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Tag End", command = mmCM2M.mmTagEndObject, w = 50, h = 25)
   curWinHeightColumn2b += 5

   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Tag S-Ctrl", command = mmCM2M.mmTagStartControl, w = 50, h = 25)
   curWinHeightColumn2b += 5

   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Tag M-Ctrl", command = mmCM2M.mmTagMidControl, w = 50, h = 25)
   curWinHeightColumn2b += 5

   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Tag E-Ctrl", command = mmCM2M.mmTagEndControl, w = 50, h = 25)
   curWinHeightColumn2b += 5

   #End the previous rowColumn
   cmds.setParent("..")

   cmds.text("Fix any parenting needed.")

   cmds.text("Don't NEED to tag head start.")

   cmds.separator( height=10, style='in' )
   curWinHeightColumn2b += 10
   
   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "Step 3 - Completion", command = mmCM2M.mmGenericRigRunStep3, w = 75, h = 25)
   

   #End the previous rowColumn
   cmds.setParent("..")
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #End the previous rowColumn
   cmds.setParent("..")

   #End the previous rowColumn
   cmds.setParent("..")

   cmds.separator( height=10, style='in' )
   curWinHeightColumn2b += 10
   
   #Creates a new frame and rowColumn set for the Normal buttons and fields
   SH_RoCoLayout = cmds.frameLayout("Mass Conversion Scripts", label = "Mass Conversion Scripts", cll = 1)
   curWinHeightColumn1 += cmds.frameLayout("Mass_Conversion_Scripts", q = 1, h = 1)
   curWinHeightColumn1 += 30
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mm_SH_RoCoLayout_Overall2", numberOfColumns = 2, cw= [[1, 150], [2, 300]])
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "QuickSaveFileAs", command = mmMCF.mmQuickSaveFileAs )
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   #cmds.button ( label = "Export All Anims from this Folder Structure", command = mmMCF.mmExportAllAnims )
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "Convert and Export All Anims from this Folder Structure", command = mmMCF.mmConvAndExportAllAnimsSequential_1 )
   curWinHeightColumn1 += 30
      
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "Fix Broken Viewport", command = mmMCF.mmFixBrokenViewport )
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "Only Export All Anims from this Folder Structure", command = mmMCF.mmExportAllAnimsSequential_1 )
   curWinHeightColumn1 += 30

   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "mmFreezeTransOnGeo", command = mmCM2M.mmFreezeTransOnGeo, w = 75, h = 25)
   
   #Button: Calls function to Export an animation from Maya to .JSON
   #--------------Currently is exporting to correct location with bad information---------------
   cmds.button ( label = "Transfer and Export All Anims from this Folder Structure", command = mmMCF.mmTransferAndExportAllAnims )
   curWinHeightColumn1 += 30

   #Button: Calls function to Export an animation from Maya to .JSON
   cmds.button ( label = "Select Anim Parts", command = mmSAP.main, w = 75, h = 25)
   
   
   #-------------------------------------------------------------------------------

   #End the previous rowColumn
   cmds.setParent(mmTabs)
   
   mmCompareList = [curWinHeightColumn1, curWinHeightColumn2a, curWinHeightColumn2b]

   curWinHeight = max(mmCompareList)

   #Store window Height to memory
   setSHWinHeight(curWinHeight)

#-------------------------------------------------------------------------------

#Basic Modeling Buttons

#-------------------------------------------------------------------------------
   #Creates a base window height value to determine the Tab's required Height
   #Subsequent additions to this value are adding up to the total height required
   curWinHeight = 0
   
   #Creates a Collapsable Shelf to Hide/Show the items inside
   basicFrLayout = cmds.columnLayout("basicFrame")
   curWinHeight += cmds.columnLayout("basicFrame", q = 1, h = 1)
   curWinHeight += 30

   #Creates a new frame and rowColumn set for the Normal buttons and fields
   normalRoCoLayout = cmds.frameLayout("normButtons", label = "Normal Buttons", cll = 1)
   curWinHeight += cmds.frameLayout("normButtons", q = 1, h = 1)
   curWinHeight += 30
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mmNormalRoCoLayout", numberOfColumns = 2, cw= [[1,75],[2,75]])
   
   curWinHeight += cmds.rowColumnLayout("mmNormalRoCoLayout", q = 1, h = 1)

   #Button: Shows and/or hides the normals of an object
   cmds.button ( label = "Toggle Vis", command = mmMF.toggleNormals, w = 75, h = 25)
   
   #Button: Allows user to reverse an object's normals
   cmds.button ( label = "Rev Norm", command = mmMF.toggleRevNormals, w = 75, h = 25) 

   #Button: Allows user to change the size of an object's normals
   cmds.floatField("normalSizeVal", value=.4, min=.001, step=.1, precision=3, w = 50)
   cmds.button ( label = "Norm Size", command = mmMF.dispNormalSize, w = 75, h = 25)
   
   #End the previous rowColumn
   cmds.setParent(basicFrLayout)
   
   #Creates a new frame and rowColumn set for the Edge buttons and fields
   edgeRoCoLayout = cmds.frameLayout("edgeButtons",  label = "Edge Buttons", cll = 1)
   curWinHeight += cmds.frameLayout("edgeButtons", q = 1, h = 1)
   curWinHeight += 30
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mmEdgeRoCoLayout", numberOfColumns = 2, cw= [[1,75],[2,75]])
   curWinHeight += cmds.rowColumnLayout("mmEdgeRoCoLayout", q = 1, h = 1)  
   
   #Button: Softens the selected edges
   cmds.button ( label = "Soften Edges", command = mmMF.softenEdge, w = 75, h = 25)
   
   #Button: Hardens the selected edges 
   cmds.button ( label = "Harden Edges", command = mmMF.hardenEdge, w = 75, h = 25)
   
   #Button: Show / hide border edges
   cmds.button ( label = "Toggle Vis", command = mmMF.toggleBorderEdges, w = 75, h = 25)

   #End the previous rowColumn
   cmds.setParent(edgeRoCoLayout)
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("mmBasicColumnLayout2", numberOfColumns = 2, cw= [[1,75],[2,75]])
   curWinHeight += cmds.rowColumnLayout("mmBasicColumnLayout2", q = 1, h = 1) 
   
   #Button: Change border edge thickness with a field
   cmds.floatField("borderEdgeThickVal", value=2, min=.001, step=.1, precision=3, w = 50)
   cmds.button ( label = "Set Width", command = mmMF.setBordEdgeThickness, w = 75, h = 25)
   
   #Button: Sets the selected edges softness to the value which the user provides
   cmds.floatField("edgeSoftVal", value=30, min=0, max = 180, step=1, precision=3, w = 50)
   cmds.button ( label = "Edge Size", command = mmMF.setEdgeSoftness, w = 75, h = 25)
   
   #End the previous rowColumn
   cmds.setParent(mmTabs)
   
   #Store window Height to memory
   setModWinHeight(curWinHeight)


#-------------------------------------------------------------------------------
#UV Buttons
#-------------------------------------------------------------------------------

   #Creates a base window height value to determine the Tab's required Height    
   #Subsequent additions to this value are adding up to the total height required
   curWinHeight = 0
   
   #Creates a new frame and rowColumn set for the UV buttons and fields
   uvFrLayout = cmds.frameLayout("uvLayout1", label = "UV Buttons", cll = 0)
   curWinHeight += cmds.frameLayout("uvLayout1", q = 1, h = 1)
   curWinHeight += 30
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("uvLayout2", numberOfColumns = 1, cw= [1,150])
   curWinHeight += cmds.rowColumnLayout("uvLayout2", q = 1, h = 1)

   #Button to open the UV editor
   cmds.button ( label = "UV Editor", command = mmUVF.uvWindow, w = 75, h = 25)
   
   #End the previous rowColumn
   cmds.setParent("..")

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("uvLayout3", numberOfColumns = 2, cw= [[1,75],[2,75]])
   curWinHeight += cmds.rowColumnLayout("uvLayout3", q = 1, h = 1)

   #Radio Buttons for positive or negative U coords 
   cmds.radioButtonGrp( "uCheckBox", nrb = 2, vr = 1, labelArray2 = ["+U", "-U"], cw = [[1, 35],[2, 35]])
   curWinHeight += cmds.radioButtonGrp("uCheckBox", q = 1, h = 1)
   
   #Radio Buttons for positive or negative V coords
   cmds.radioButtonGrp( "vCheckBox", nrb = 2, vr = 1, labelArray2 = ["+V", "-V"], cw = [[1, 35],[2, 35]])
   curWinHeight += cmds.radioButtonGrp("vCheckBox", q = 1, h = 1)
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #Button moves UV's to a negative U or V coordinate area
   cmds.button("button1", label = "Move UV", command = mmUVF.moveUVCords, w = 75, h = 25)
   curWinHeight += cmds.button("button1", q = 1, h = 1)
   
   #Creates a new frame and rowColumn set for the Unfold UV buttons and fields
   cmds.frameLayout("uvLayout4", label = "Unfold UVs", cll = 1)
   curWinHeight += cmds.frameLayout("uvLayout4", q = 1, h = 1)
   curWinHeight += 10
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("uvLayout5", numberOfColumns = 1, cw= [1,150])
   curWinHeight += cmds.rowColumnLayout("uvLayout5", q = 1, h = 1)
   
   #Unfold UV fields, radio selectors, and buttons
   #Weight Solver option of Unfold Button
   cmds.text("Weight Solver")
   cmds.floatSliderGrp("weightSolver", field=True, value=0.0, min=0, max = 1, step=.01, precision=3, cw = [[1,75], [2,75]])
   curWinHeight += cmds.floatSliderGrp("weightSolver", q = 1, h = 1)
   
   #Optimization option of Unfold Button
   cmds.text("Optimize to Original")
   cmds.floatSliderGrp("optimizeToOriginal", field=True, value=0.5, min=0, max = 1, step=.01, precision=3, cw = [[1,75], [2,75]])
   curWinHeight += cmds.floatSliderGrp("optimizeToOriginal", q = 1, h = 1)
   
   #Number of Maximum Iterations option of Unfold Button
   cmds.text("Max Iterations")
   cmds.intSliderGrp("unfoldMaxIterations", field=True, value=5000, min=0, max = 10000, cw = [[1,75], [2,75]])
   curWinHeight += cmds.intSliderGrp("unfoldMaxIterations", q = 1, h = 1)
   
   #Stopping Threshold option of Unfold Button
   cmds.text("Stopping Threshold")
   cmds.floatSliderGrp("stopThresh", field=True, value=.0010, min=0, max = 1, step=.01, precision=3, cw = [[1,75], [2,75]])
   curWinHeight += cmds.floatSliderGrp("stopThresh", q = 1, h = 1)
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("uvLayout6", numberOfColumns = 2, cw= [[1,75],[2,75]])
   curWinHeight += cmds.rowColumnLayout("uvLayout6", q = 1, h = 1)

   #Pin UVs option of Unfold Button
   cmds.text("Pin UVs")
   cmds.radioButtonGrp( "unfoldCheckBox", nrb = 3, vr = 1,
     labelArray3 = ["Border", "Selected", "None"], sl = 3)
   curWinHeight += cmds.radioButtonGrp("unfoldCheckBox", q = 1, h = 1)

   #End the previous rowColumn
   cmds.setParent("..")
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("uvLayout7", numberOfColumns = 1, cw= [1,150])
   curWinHeight += cmds.rowColumnLayout("uvLayout7", q = 1, h = 1)

   #Button which calls Unfold function
   cmds.button("button2", label = "Unfold", command = mmUVF.uvUnfold, w = 75, h = 25)
   curWinHeight += cmds.button("button2", q = 1, h = 1)
   
   #Creates a new frame and rowColumn set for the Relax UV buttons and fields
   cmds.frameLayout("uvLayout10", label = "Relax UVs", cll = 1)
   curWinHeight += cmds.frameLayout("uvLayout10", q = 1, h = 1)
   #curWinHeight += 10
   
   cmds.text("Max Iterations")
   cmds.intSliderGrp("relaxMaxIterations", field=True, value=90, min=0, max = 200, cw = [[1,75], [2,75]])

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("uvLayout11", numberOfColumns = 1, cw= [1,150])
   curWinHeight += cmds.rowColumnLayout("uvLayout11", q = 1, h = 1)
   
   cmds.text("Pin UVs")
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("uvLayout8", numberOfColumns = 2, cw= [[1,75],[2,75]])
   curWinHeight += cmds.rowColumnLayout("uvLayout8", q = 1, h = 1)
   
   #Relax Options
   cmds.radioButtonGrp( "relaxCheckBox", nrb = 3, vr = 1, labelArray3 = ["Border", "Selected", "None"], sl = 1)
   curWinHeight += cmds.radioButtonGrp("relaxCheckBox", q = 1, h = 1)

   #Button which calls Relax Function
   cmds.button("button3", label = "Relax", command = mmUVF.uvRelax, w = 75, h = 25)
   curWinHeight += cmds.button("button3", q = 1, h = 1)
   #curWinHeight += 10

   #Button to select UV Shell Border out of almost any selection
   cmds.button ( label = "Grab Border", command = mmUVF.selectUVBorder, w = 75, h = 25)
   #curWinHeight += 10
   
   #Button to select UV Shell out of almost any selection
   cmds.button ( label = "Grab Shell", command = mmUVF.selectUV, w = 75, h = 25)
   #curWinHeight += 10

   #End the previous rowColumn
   cmds.setParent("..")
   
   cmds.rowColumnLayout("uvLayout9", numberOfColumns = 2, cw= [1,75])
   curWinHeight += cmds.rowColumnLayout("uvLayout9", q = 1, h = 1)
   
   #Button: Sets the selected edges softness to the value which the user provides
   cmds.intField("uvAdjustVal", value=1, min=0, max = 10, step=1, w = 50)
   #curWinHeight += 10

   #Button to select UV Shell out of almost any selection
   cmds.button ( label = "UV Adj", command = mmUVF.adjUV, w = 75, h = 25)
   #curWinHeight += 10
   
   #End the previous rowColumn
   cmds.setParent(mmTabs)
   
   #Store window Height to memory
   setUVWinHeight(curWinHeight)

#-------------------------------------------------------------------------------    

#Organization Buttons

#-------------------------------------------------------------------------------

   #Creates a base window height value to determine the Tab's required Height
   #Subsequent additions to this value are adding up to the total height required
   curWinHeight = 0
   curWinHeightColumn1 = 0
   curWinHeightColumn2 = 0
   curWinHeightColumn3 = 0
   
   #Creates a Collapsable Shelf to Hide/Show the items inside
   orgFrLayout = cmds.frameLayout("orgLayout1", label = "Organization Options", cll = 1)
   curWinHeightColumn1 += cmds.frameLayout("orgLayout1", q = 1, h = 1)

   #Creates a new rowColumn Layout for design purposes
   #This is a larger set up than needed, and inside it should be multiple smaller UI menus
   orgMainLayout = cmds.rowColumnLayout("orgLayout2", numberOfColumns = 3, cw= [[1,150],[2,150],[3,150]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.rowColumnLayout("orgLayout2", q = 1, h = 1)

   #Creates a new rowColumn Layout for design purposes
   #This is a new rowColumn specifically for the Trans/Rot/Scale toggle options
   cmds.rowColumnLayout("orgLayout2sub1", numberOfColumns = 1, cw= [1,140], cal = [1,"center"])
   curWinHeightColumn1 += cmds.rowColumnLayout("orgLayout2sub1", q = 1, h = 1)

   #Creates a new rowColumn Layout for design purposes
   #This is a larger set up than needed, and inside it should be multiple smaller UI menus
   cmds.rowColumnLayout("orgLayout2sub2", numberOfColumns = 2, cw= [[1,150],[2,150],[3,150]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.rowColumnLayout("orgLayout2sub2", q = 1, h = 1)

   #Creates a new rowColumn Layout for design purposes
   #This is a new rowColumn specifically for the Trans/Rot/Scale toggle options
   cmds.rowColumnLayout("orgLayout2sub3", numberOfColumns = 2, cw= [[1,50],[2,90]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.rowColumnLayout("orgLayout2sub3", q = 1, h = 1)

   #Button which Selects or Deselects all Trans check boxes
   cmds.button ( label = "Trans", command = mmOF.selectAllTransToggle, w = 50, h = 25)
   
   #Check Boxes for Translate X, Y, and Z selection
   cmds.checkBoxGrp ( "chkBoxTrans", ncb = 3,
     labelArray3 = ["X", "Y", "Z"], cw = [[1, 30],[2, 30],[3, 30]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.checkBoxGrp("chkBoxTrans", q = 1, h = 1)

   #Button which Selects or Deselects all Trans check boxes
   cmds.button( label = "Rotate", command = mmOF.selectAllRotToggle, w = 50, h = 25)

   #Check Boxes for Rotate X, Y, and Z selection
   cmds.checkBoxGrp( "chkBoxRot", ncb = 3,
     labelArray3 = ["X", "Y", "Z"], cw = [[1, 30],[2, 30],[3, 30]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.checkBoxGrp("chkBoxRot", q = 1, h = 1)
   
   #Button which Selects or Deselects all Trans check boxes
   cmds.button( label = "Scale", command = mmOF.selectAllScaleToggle, w = 50, h = 25)

   #Check Boxes for Scale X, Y, and Z selection
   cmds.checkBoxGrp( "chkBoxScale", ncb = 3,
     labelArray3 = ["X", "Y", "Z"], cw = [[1, 30],[2, 30],[3, 30]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.checkBoxGrp("chkBoxScale", q = 1, h = 1)

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("orgLayout3", numberOfColumns = 2, cw= [[1,50],[2,75]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.rowColumnLayout("orgLayout3", q = 1, h = 1)

   #Button which Selects or Deselects all check boxes
   cmds.button( label = "Tog All", command = mmOF.selectAllToggle, w = 50, h = 25)

   #End the previous rowColumn
   cmds.setParent("..")

   #Check Boxes for Visibility selection
   cmds.checkBoxGrp( "chkBoxVis", label = "Vis", ncb = 1,
     l = "Vis", cw = [[1, 40],[2, 30]], cal = [1,"center"])
   curWinHeightColumn1 += cmds.checkBoxGrp("chkBoxVis", q = 1, h = 1)

   #End the previous rowColumn
   cmds.setParent("..")

   #End the previous rowColumn
   cmds.setParent("..")

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("orgLayout4", numberOfColumns = 2, cw= [[1,75],[2,75]])
   curWinHeightColumn1 += cmds.rowColumnLayout("orgLayout4", q = 1, h = 1)  
   
   #Lock and Hide Attributes Button
   cmds.button( label = "Lock/Hide", command = mmOF.lockNHide, w = 50, h = 25)

   #Unlock and Unhide Attributes Button
   cmds.button( label = "UnLock/Hide", command = mmOF.unlockUnhide, w = 50, h = 25)
   
   #Button changes display type to Reference for all selected objects
   cmds.button( label = "Ref Display", command = mmOF.refDisplayType, w = 50, h = 25)
   
   #Button changes display type to Normal for all selected objects
   cmds.button( label = "Norm Display", command = mmOF.normDisplayType, w = 50, h = 25)
   
   #End the previous rowColumn
   cmds.setParent(orgMainLayout)
   
   #-------------------------------------------------------------------------------
   
   #Adding a separator to see what happens
   #cmds.separator( height=1, style='single' )

   #Creates a new column set 
   cmds.rowColumnLayout("orgLayout5", numberOfColumns = 1, cw= [1,150])
   curWinHeightColumn2 += cmds.rowColumnLayout("orgLayout5", q = 1, h = 1)
   
   #Creates a Color Index Slider Group to change colors of selected objects
   cmds.colorIndexSliderGrp("colorField", min=0, max=20, value=0, w = 100 )
   cmds.button( label = "Color Changer", command = mmOF.changeColor, w = 50, h = 25)
   curWinHeightColumn2 += 50

   #Button to Mass Rename different selections
   cmds.text("Mass Rename Add Prefix")
   cmds.textFieldButtonGrp("massRenameField_Prefix", text='addedText_', buttonLabel='Add Pre', bc = mmOF.mmNameAddPrefix, cw = [[1,100],[2,50]] ) 
   curWinHeightColumn2 += 10

   #Button to Mass Rename different selections
   cmds.text("Mass Rename Add Suffix")
   cmds.textFieldButtonGrp("massRenameField_Suffix", text='_addedText', buttonLabel='Add Suf', bc = mmOF.mmNameAddSuffix, cw = [[1,100],[2,50]] ) 
   curWinHeightColumn2 += 10

   #Button causes the first selected object to move to the second & freeze transforms
   cmds.button( label = "Matcher", command = mmOF.mmCallMoveObject, w = 50, h = 25)
   curWinHeightColumn2 += 10

   cmds.text("Matcher will match\nthe first selection to\nthe second's position")

   #End the previous rowColumn
   cmds.setParent(orgMainLayout)

   #-------------------------------------------------------------------------------
   
   #Creates a Collapsable Shelf to Hide/Show the items inside
   cmds.frameLayout("orgLayout6", label = "Icon Creation", cll = 1)
   curWinHeightColumn3 += cmds.frameLayout("orgLayout6", q = 1, h = 1)
   curWinHeightColumn3 += 30

   #Creates a new rowColumn Layout for design purposes
   cmds.rowColumnLayout("orgLayout7", numberOfColumns = 2, cw= [[1,75],[2,75]], cal = [1,"center"])
   curWinHeightColumn3 += cmds.rowColumnLayout("orgLayout7", q = 1, h = 1)
   curWinHeightColumn3 += 30
   
   #Button creates a Box shaped Icon NURB
   cmds.button( label = "Box", command = mmOF.createCube, w = 50, h = 25)
   curWinHeightColumn3 += 5
   
   #Button creates a Belt shaped Icon NURB
   cmds.button( label = "Belt", command = mmOF.createBelt, w = 50, h = 25)
   
   #Button creates a Hand shaped Icon NURB
   cmds.button( label = "Hand", command = mmOF.createHand, w = 50, h = 25)
   
   #Button creates a Foot shaped Icon NURB
   cmds.button( label = "Foot", command = mmOF.createFoot, w = 50, h = 25)
   curWinHeightColumn3 += 5
   
   #Button creates an Arrow shaped Icon NURB
   cmds.button( label = "Move All", command = mmOF.createMoveAll, w = 50, h = 25)

   #Button creates a Cog shaped Icon NURB
   cmds.button( label = "COG", command = mmOF.createCog, w = 50, h = 25)
   curWinHeightColumn3 += 5
   
   #Button creates a Cog shaped Icon NURB
   cmds.button( label = "L", command = mmOF.createL, w = 50, h = 25)
   
   #Button creates a Cog shaped Icon NURB
   cmds.button( label = "R", command = mmOF.createR, w = 50, h = 25)
   curWinHeightColumn3 += 5
   
   #Button creates a Pin shaped Icon NURB
   cmds.button( label = "Pin", command = mmOF.createPin, w = 50, h = 25)
   
   #Button creates a Pin shaped Icon NURB
   cmds.button( label = "Orb", command = mmOF.createOrb, w = 50, h = 25)
   curWinHeightColumn3 += 5

   #Button creates a Pin shaped Icon NURB
   cmds.button( label = "FitAll", command = mmOF.createFitAll, w = 50, h = 25)
   
   #End the previous rowColumn
   cmds.setParent("..")
   
   #Button to Mass Rename different selections
   cmds.textFieldButtonGrp("createTextBox_TextField", text='text', buttonLabel='Text', bc = mmOF.createTextBox, cw = [[1,100],[2,50]] ) 
   curWinHeightColumn3 += 10

   #End the previous rowColumn
   cmds.setParent(mmTabs)
   
   mmCompareList = [curWinHeightColumn1, curWinHeightColumn2, curWinHeightColumn3]

   curWinHeight = max(mmCompareList)

   #Store window Height to memory
   setOrgWinHeight(curWinHeight)

   
#-------------------------------------------------------------------------------
#Rigging Buttons
#-------------------------------------------------------------------------------
   #Creates a base window height value to determine the Tab's required Height    
   #Subsequent additions to this value are adding up to the total height required
   curWinHeight = 0
   
   #Creates a new frame and rowColumn set for the UV buttons and fields
   rigFrLayout = cmds.frameLayout("rigLayout1", label = "Rig Buttons", cll = 0)
   curWinHeight += cmds.frameLayout("rigLayout1", q = 1, h = 1)
   curWinHeight += 30
   
   cmds.rowColumnLayout("rigLayout2", numberOfColumns = 1, cw= [1,150])
   curWinHeight += cmds.rowColumnLayout("rigLayout2", q = 1, h = 1)
   
   #Text area to describe how to run the function
   cmds.text("Select an icon, then\na 3 joint chain to effect.")
   
   #Check Box Group to decide what should be included in Hand System
   cmds.checkBoxGrp("ikfkSwitchChkBoxes", numberOfCheckBoxes=1, label='Include:', label1 = 'Stretchy', v1 = 1, adj = 1, cw2 = [75,75], w = 150, cal = [1,"center"], vr =1)
   curWinHeight += 50
   
   """
   #Old when I had bendy working
   #Check Box Group to decide what should be included in Hand System
   cmds.checkBoxGrp("ikfkSwitchChkBoxes", numberOfCheckBoxes=2, label='Include:', la2 = ['Bendy', 'Stretchy'], v1 = 0, v2 = 1, adj = 1, cw2 = [75,75], w = 150, cl2 = ["center","center"], vr =1)
   curWinHeight += 50
   """

   #create a new row column layout
   cmds.rowColumnLayout("rigLayout3", numberOfColumns = 2, cw= [(1,75),(2,75)])
   curWinHeight += cmds.rowColumnLayout("rigLayout3", q = 1, h = 1)
   
   """
   #Old when I had bendy working
   #Text area to describe how to run the function
   cmds.text("Bendy \n Divisions:")
   curWinHeight += 25
   
   #IntField to get the number of divisions for the arm
   cmds.intField("createIKSplineArmDivVal", w = 75, h = 25, v = 30)
   """

   #Text area to describe how to run the function
   cmds.text("Number of\nBones In IK:")
   curWinHeight += 25
   
   #IntField to get the number of divisions for the arm
   cmds.intField("createIKSplineArmNumBonesVal", w = 75, h = 25, v = 3)
   
   #set parent back to previous
   cmds.setParent("..")
   
   #Button to create an IK/FK switch and additional limbs to control it
   cmds.textFieldButtonGrp("ikfkSwitchLabel", buttonLabel = "IK/FK Auto", bc = mmRF.autoIKFK, w = 75, cw = [[1,75],[2,75]], text = "Switch Label")
   
   #Text area to describe how to run the function
   cmds.text("Ensure joints are oriented\nwith 'Y' down the chain,\na preferred angle is set for\nmid joint, and that names\nare unique. All conn-\nections to limb should\nbe made to last cluster.")
   curWinHeight += 130

   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   #Text area to describe how to run the function
   cmds.text("Select icon you want, \n then the joint to set-up.")
   curWinHeight += 25

   #Check Box Group to decide what should be included in Hand System
   cmds.radioButtonGrp("mmPadAndAlignRadioBoxes", nrb=4, label='Constraint Type:', labelArray4=['Point', 'Aim', 'Orient', 'Parent'], cl2 = ["center","center"], cw2 = [90,60], adj = 1, w = 100, vr =1, sl = 3)
   curWinHeight += 50
   
   #Button to pad an icon, align it, and orient constrain a joint to it
   cmds.button(label = "Pad, Align, and Orient", c = mmRF.padAndAlign)
   curWinHeight += 25
   
   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   #Text area to describe how to run the function
   cmds.text("Select curves you want, \n and type in new name.")
   curWinHeight += 25
   
   #Button to combine multiple Nurbs curves into one object
   cmds.textFieldButtonGrp("combineNurbsLabel", buttonLabel = "Combine", bc = mmOF.combineNurbCurves, w = 75, cw = [[1,75],[2,75]], text = "New_icon")
   curWinHeight += 50
   
   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   #Text area to describe how to run the function
   cmds.text("Select icon you want, then \n select each finger chain.")
   curWinHeight += 25
   
   #Check Box Group to decide what should be included in Hand System
   cmds.checkBoxGrp("handSystemChkBoxes", numberOfCheckBoxes=3, label='Include:', labelArray3=['Curl', 'Spread', 'Twist'], v1 = 1, v2 = 1, v3 = 1, adj = 1, cw2 = [75,75], w = 150, cl2 = ["center","center"], vr =1)
   curWinHeight += 25
   
   cmds.text("*does not connect 'fist' attr")
   curWinHeight += 25

   cmds.button(label = "Create Hand System", c = mmRF.handCreator)
   curWinHeight += 50
   
   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   cmds.text("Select Controller, \n Multiplier, then base\nthrough end pads of\none tentacle")
   curWinHeight += 50
   
   cmds.button(label = "Connect Tentacle Icon", c = mmRF.tentacleConnector)
   curWinHeight += 35
   
   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   #create a new row column layout
   cmds.rowColumnLayout("rigLayout4", numberOfColumns = 2, cw= [(1,75),(2,75)])
   curWinHeight += cmds.rowColumnLayout("rigLayout4", q = 1, h = 1)
   
   #End the previous rowColumn
   cmds.setParent(mmTabs)
   
   #Store window Height to memory
   setRigWinHeight(curWinHeight)
     
#-------------------------------------------------------------------------------
#Rigging Buttons 2
#-------------------------------------------------------------------------------
   #Creates a base window height value to determine the Tab's required Height    
   #Subsequent additions to this value are adding up to the total height required
   curWinHeight = 0
   
   #Creates a new frame and rowColumn set for the UV buttons and fields
   rig2FrLayout = cmds.frameLayout("rig2Layout1", label = "Rig Buttons", cll = 0)
   curWinHeight += cmds.frameLayout("rig2Layout1", q = 1, h = 1)
   curWinHeight += 30
   
   cmds.rowColumnLayout("rig2Layout2", numberOfColumns = 1, cw= [1,150])
   curWinHeight += cmds.rowColumnLayout("rig2Layout2", q = 1, h = 1)
   
   cmds.text("Select a Curve, and press\nCLUSTERIZER")
   curWinHeight += 25

   cmds.button(label = "The Clusterizer", c = mmRF.clusterMaker)
   #curWinHeight += 25
   
   cmds.text("*must be Cubic")

   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   cmds.text("Select ikSpline Curve,\nroot joint of chain,\nand select the axis which\ntravels down the chain.")
   curWinHeight += 25

   #Check Box Group to decide what should be included in Hand System
   cmds.radioButtonGrp("stretchySplineRadioBoxes", nrb=3, labelArray3=["X", "Y", "Z"], cl3 = ["center","center","center"], cw3 = [50, 50, 50], adj = 1, w = 100, vr =0, sl = 2)
   curWinHeight += 50
   
   cmds.button(label = "Make Spline Stretchy", c = mmRF.makeSplineStretchy)
   curWinHeight += 25
   
   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   cmds.text("Select the icon which\nwill control the switch,\nthen the pad which the\nconstraints will be on,\nthen each item which will\nbe constraining.")
   curWinHeight += 100
   
   #do i need multiple types?  parent is the only one that seems to work
   cmds.radioButtonGrp("switcherSystemChkBoxes", nrb=4, label='Constraint Type:', labelArray4=['Point', 'Orient', 'Parent', 'Scale'], cl2 = ["center","center"], cw2 = [90,60], adj = 1, w = 100, vr =1, sl = 3)
   curWinHeight += cmds.radioButtonGrp("switcherSystemChkBoxes", q = 1, h = 1)
   curWinHeight += 25
   
   cmds.button(label = "Create a Switcher System", c = mmRF.spaceSwitcherMulti)
   curWinHeight += 25
   
   cmds.button(label = "(Simple Switcher System)", c = mmRF.spaceSwitcherMultiSimple)
   curWinHeight += 25
   
   #Check Box Group to decide what should be included in Hand System
   cmds.checkBoxGrp("switcherSystemChkBoxes2", numberOfCheckBoxes=1, l='*Create Attributes?', v1 = 1, adj = 1, cw2 = [120, 30], w = 150, cal = (1,"right"), vr =1)
   curWinHeight += 25
   
   cmds.text("If not, proper attr must\nalready exist on icon.")
   curWinHeight += 50

   cmds.separator( height=10, style='in' )
   curWinHeight += 10
   
   cmds.text("Select curve and then\neach joint to effect\nfrom most to least influence")
   curWinHeight += 50

   #Check Box Group to decide what should be included in Hand System
   cmds.radioButtonGrp("mmMultiChainFKHelperRadioButtons", nrb=2, labelArray2=["Whole\nChain", "Selected\nJoints"], cl2 = ["center","center"], cw2 = [75, 75], adj = 1, w = 100, vr =0, sl = 1)
   curWinHeight += 50
   
   cmds.button(label = "Multi-Chain FK Helper", c = mmRF.multiChainFKHelper)
   curWinHeight += 25
   
   #End the previous rowColumn
   cmds.setParent(mmTabs)
   
   #Store window Height to memory
   setRig2WinHeight(curWinHeight)
   
   
#-------------------------------------------------------------------------------

   #Renames the Tabs to comprehensible Names
   cmds.tabLayout( mmTabs, edit=True, tabLabel=((SH_FrLayout, 'SH_Tools'), (basicFrLayout, 'Modeling'), (orgFrLayout, 'Organization'), (uvFrLayout, 'UVs'), (rigFrLayout, 'Rigging'), (rig2FrLayout, 'Rigging2')) )
   
   #Resizes window to default tab size
   #This "sti" actually sets the default tab to load on open.
   cmds.tabLayout("mmTabs", e = 1, sti = 1)
   setWinHeight()

   #Display everything
   cmds.showWindow("sh_toolset_window")

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

#FUNCTIONS


#-------------------------------------------------------------------------------

#UI Window Functions

#-------------------------------------------------------------------------------

#Function: Resizes Main Window to fit Tabs as they are selected
def setWinHeight(*args):
   curSelectedTab = cmds.tabLayout("mmTabs", q = 1, sti = 1)
   if (curSelectedTab == 1):
     cmds.window("sh_toolset_window", e = 1, h = SH_WinHeightNow)
     cmds.formLayout("basicFormLayout", e = 1, h = SH_WinHeightNow)
   elif (curSelectedTab == 2):
     cmds.window("sh_toolset_window", e = 1, h = modWinHeightNow)
     cmds.formLayout("basicFormLayout", e = 1, h = modWinHeightNow)
   elif (curSelectedTab == 3):
     cmds.window("sh_toolset_window", e = 1, h = uvWinHeightNow)
     cmds.formLayout("basicFormLayout", e = 1, h = uvWinHeightNow)
   elif (curSelectedTab == 4):
     cmds.window("sh_toolset_window", e = 1, h = orgWinHeightNow)
     cmds.formLayout("basicFormLayout", e = 1, h = orgWinHeightNow)
   elif (curSelectedTab == 5):
     cmds.window("sh_toolset_window", e = 1, h = rigWinHeightNow)
     cmds.formLayout("basicFormLayout", e = 1, h = rigWinHeightNow)
   elif (curSelectedTab == 6):
     cmds.window("sh_toolset_window", e = 1, h = rig2WinHeightNow)
     cmds.formLayout("basicFormLayout", e = 1, h = rig2WinHeightNow)

   else:
     print "invalid input";
   
#Stores Win Height of Particular Tab
def setSHWinHeight(shHeightCurrentVal):
   global SH_WinHeightNow
   SH_WinHeightNow = shHeightCurrentVal;

#Stores Win Height of Particular Tab
def setModWinHeight(modHeightCurrentVal):
   global modWinHeightNow
   modWinHeightNow = modHeightCurrentVal;

#Stores Win Height of Particular Tab
def setOrgWinHeight(orgHeightCurrentVal):
   global orgWinHeightNow
   orgWinHeightNow = orgHeightCurrentVal;

#Stores Win Height of Particular Tab
def setUVWinHeight(uvHeightCurrentVal):
   global uvWinHeightNow
   uvWinHeightNow = uvHeightCurrentVal;
   
#Stores Win Height of Particular Tab
def setRigWinHeight(rigHeightCurrentVal):
   global rigWinHeightNow
   rigWinHeightNow = rigHeightCurrentVal;
   
#Stores Win Height of Particular Tab
def setRig2WinHeight(rig2HeightCurrentVal):
   global rig2WinHeightNow
   rig2WinHeightNow = rig2HeightCurrentVal;




#End of Toolset
