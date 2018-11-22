"""

Function: mmScaleDownFrom3DSMax
Description: This function fixes the strange scale issue which happens when coming from 3dsmax to maya.
     It is also important to do this so the new rig matches the .obj which Qubicle exports.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

######################################
############# DEFINES ################
######################################



def main( mmRootFound ):

   #Grab the root
   cmds.select( mmRootFound )
   
   #First need to ensure there are no keys in scale because we are adjusting the scale
   cmds.cutKey( cl = 1, at = ("sx", "sy", "sz") )

   #Find the current position and divide by 2.54 (the arbitrary 3dsmax weird value)
   mmRootScaleX = cmds.getAttr( mmRootFound + '.scaleX')

   if ( mmRootScaleX != 1 ):

      #Find the current position and divide by 2.54 (the arbitrary 3dsmax weird value)
      mmRootTransX = cmds.getAttr( mmRootFound + '.translateX')/2.54
      mmRootTransY = cmds.getAttr( mmRootFound + '.translateY')/2.54
      mmRootTransZ = cmds.getAttr( mmRootFound + '.translateZ')/2.54

      #Set the values to what they should be.
      cmds.move( mmRootTransX, mmRootTransY, mmRootTransZ, worldSpace = 1, absolute = 1 )
      cmds.scale( 1, 1, 1 )

