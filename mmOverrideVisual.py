"""

Function: mmOverrideVisual
Description: These functions will override the visuals of mesh objects which have been 'sent to' from 3dsmax to maya.
     For some unknown reason this is an issue.  This script will not harm anything if the display is already correct.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

######################################
############# DEFINES ################
######################################


#---------------------------------------------
#Must call the function with a separate function so I can pass in the selected objects.
def run(*args):
   
   selectionList = cmds.ls(orderedSelection = True)
   main( selectionList )


#---------------------------------------------

#Set imported 3dsmax meshes to display geometry properly

def main( mmSelectedItems ):
   #print mmSelectedItems
   selectionList = list(mmSelectedItems)
   
   for objectName in selectionList:
      
      #print objectName
      
      cmds.setAttr(objectName+".overrideEnabled",1)
