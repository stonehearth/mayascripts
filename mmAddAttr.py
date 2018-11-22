"""

Function: mmAddAttr
Description: Adds the required Attributes to any selected objects.
     Currently isn't needed for anything - will re-use this script later.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

######################################
############# DEFINES ################
######################################


def main(*args):
    print "This does nothing."


def mmFootAttrs(*args):

   i = 0
   mmSelectedInScene = cmds.ls(sl=1)
   
   #Runs through the selected objects and adds the required attributes to all of them.
   # - Please note, it does not check to see if the attributes are already there.
   
   while (i<(len(mmSelectedInScene))):
   
     #Example: cmds.addAttr(nameOfIcon, ln = currentConstraintName, at = "double", min = 0, max = 10, dv = 0, k = 1)
     
     cmds.select(mmSelectedInScene[i], r = 1)
         
     #Creates a "Long" Variable - which stays on 
     #cmds.addAttr(ln = "ID", at = "long", dv = -1, k = 1)
     
     #example of parenting attributes:
     #cmds.addAttr( longName='sampson', numberOfChildren=5, attributeType='compound' )
     #cmds.addAttr( longName='homeboy', attributeType='matrix', parent='sampson' )
     #cmds.setAttr((multDivNodeName+".input2X"), finalMultiple)
     
     """
     #This is for creating some sort of parented property stuff
     cmds.addAttr( longName="ParentID", numberOfChildren=3, attributeType='double3' )
     #(looks like this isn't needed): cmds.setAttr((mmSelectedInScene[i]+".ParentID"), (0, 0, 0), type="double3" )
     
     cmds.addAttr( longName="ParentIDX", attributeType='double', parent='ParentID', k = 1 )
     cmds.addAttr( longName="ParentIDY", attributeType='double', parent='ParentID', k = 1 )
     cmds.addAttr( longName="ParentIDZ", attributeType='double', parent='ParentID', k = 1 )
     """
     
     #Creating reverse foot attributes needed
     cmds.addAttr( longName="FootRoll", attributeType='double', min = -10, max = 10, dv=0, k = 1 )
     cmds.addAttr( longName="FootBank", attributeType='double', min = 0, max = 10, dv=0, k = 1 )
     cmds.addAttr( longName="ToeBend", attributeType='double', min = 0, max = 10, dv=0, k = 1 )
     cmds.addAttr( longName="ToeSwivel", attributeType='double', min = 0, max = 10, dv=0, k = 1 )


     #Create Set Driven Keys for various values
     #Connect the Foot Roll to the Heel and Toe both rotating up to 90 degrees
     
     #Connect the Foot Bank to the Inner and Outer Locators
     
     #Connect the Toe Bend to the Toe Bend Locator
     
     #Connect the Toe Swivel
     
     
     
     
     
     
     i+=1
     













