"""

Function: mmSelectAnimatingParts
Description: This function grabs all the animating parts of a rig file which we want to transfer around.
     NOT all the things which are exported.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

######################################
############# DEFINES ################
######################################

'''
This function should select all desired animating parts - of the types specified, rather than having a specific function for each type.
'''
def main( mmListOfSelectionType = ["locator", "mesh", "nurbsCurve"], *args ):

   mmDesiredSelection = []

   #Viable types allowed in List: "locator", "mesh", "nurbsCurve", "transform"
   #  Could be others, but these should work.

   if ( mmListOfSelectionType == [] ):
      print "Invalid selection requested of mmSAP.mmSelectAnimatingParts"
      return None

   #Select the various bones/locators/meshes which will have animation we want to keep
   #Doesn't matter what is selected to begin with as we clear the selection at the start
   #Returns a list of the selected parts and selects them as well

   #Store what the new meshes names are
   #Clear Selection
   cmds.select( clear=True )

   #####Need to make it so this grabs specifically what i want and nothing else.
   for mmType in mmListOfSelectionType:

      mmAnimatingInScene = cmds.ls( type = str(mmType) )

      #print mmSelectedLocatorsInScene

      #Find the parent (which should always be the transforms - and is the thing we actually want.)
      mmSelectedAnimatingTransformsInScene = cmds.listRelatives( mmAnimatingInScene, parent=True, fullPath=0 )

      mmCounter = 0

      if ( mmSelectedAnimatingTransformsInScene != None ):

         for mmTransform in mmSelectedAnimatingTransformsInScene:

            mmCheckParent = cmds.listRelatives( mmTransform, parent = True )

            if ( mmCheckParent != None ):
               mmCheckParentNameSplit = mmCheckParent[0].split("_")
               
               mmCheckParentNameSplitLen = len(mmCheckParentNameSplit)-1
               
               #Don't want any meshes which have been marked as "ExtraObject" - and therefore not part of the rig file itself.
               if ( mmCheckParentNameSplit[mmCheckParentNameSplitLen] == "ExtraObject" ):
                  mmSelectedAnimatingTransformsInScene[mmCounter] = ""

            mmCounter += 1

         #Need to remove all "" entries in the list of animated parts - this is to ensure that "ExtraObject"s are not selected
         mmSelectedAnimatingTransformsInScene = [ mmX for mmX in mmSelectedAnimatingTransformsInScene if mmX != "" ]

         #Grab each individual object from the different types and store them in one list
         for mmObject in mmSelectedAnimatingTransformsInScene:
            mmDesiredSelection.append( mmObject )

   cmds.select(mmDesiredSelection)

   #Need to verify that there is only one entry for each entry (no duplicates)
   #Need to remove duplicates and sort
   mmDesiredSelection = list(set(mmDesiredSelection))
   mmDesiredSelection.sort()


   return mmDesiredSelection