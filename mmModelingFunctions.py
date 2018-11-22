"""

Function: mmModelingFunctions
Description: This is a collection of functions which help out with Modeling in general.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

#Local
import mmUVFunctions
import mmOrganizationFunctions
import mmRiggingFunctions

######################################
############# DEFINES ################
######################################


#Function: Toggles the normal visibility of selected object's faces
def toggleNormals(*args):
   cmds.ToggleFaceNormalDisplay()
   
#Function: Changes the display size of normals
def dispNormalSize(*args):
   normVal = cmds.floatField("normalSizeVal", query=True, value= True)
   cmds.polyOptions(sn=normVal);

#Function: Reverses the normals of selected objects
def toggleRevNormals(*args):
   cmds.polyNormal(nm=0);
   
#Function: Soften Edges of selected faces
def softenEdge(*args):
   mmSelectedItems = cmds.ls(sl = 1)

   for mmItem in mmSelectedItems:
      cmds.select(mmItem)
      cmds.polySoftEdge(a=180);

   cmds.select(cl = 1)
   
#Function: Harden Edges of selected faces
def hardenEdge(*args):
   cmds.polySoftEdge(a=0);
   
#Function: Toggles visibility of Border Edges
def toggleBorderEdges(*args):
   cmds.ToggleBorderEdges();
   
#Function: Sets the thickness of Face Border Edges
def setBordEdgeThickness(*args):
   bordEdgeVal = cmds.floatField("borderEdgeThickVal", query=True, value= True)
   cmds.polyOptions(sb=bordEdgeVal);

#Function: Allows user to set the Softness of Edges by a value
def setEdgeSoftness(*args):
   edgeVal = cmds.floatField("edgeSoftVal", query=True, value=True)
   cmds.polySoftEdge(a=edgeVal);
