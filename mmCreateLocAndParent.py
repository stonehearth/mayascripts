"""

Function: mmCreateLocAndParent
Description: This function will add the selected objects to the rig file which you are in.
               It should put everything into the proper folders as well.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

#Local
import mmConvert3DSMaxRigToMayaRig as mmCM2M
import mmGetWorldTrans as mmGWT
import mmOrganizationFunctions as mmOF

######################################
############# DEFINES ################
######################################


def main(*args):

   #Find or create all groups for organization
   mmCM2M.mmCreateRigGroups()
   
   mmGroup_Hidden = "_Group_Hidden"
   mmGroup_Controls = "_Group_Controls"
   mmGroup_Geo = "_Group_Geometry"
   mmGroup_ExportLocator = "_Group_ExportLocators"

   #Create lists for storing information later
   mmItemFor_Hidden = []
   mmItemFor_Controls = []
   mmItemFor_Geo = []
   mmItemFor_ExportLocator = []

   #Select all items we want in the scene

   #---------------------------------------------

   #Grab the selected objects in scene
   selectionList = cmds.ls( sl = 1 )

   #Store selection list for later
   originalSelectionList = list(selectionList)

   #---------------------------------------------

   #---------------------------------------------

   #Create a locator, and then create and destroy a parent constraint to get the locator to the place it should be at.

   #RigStoreArray will hold on to each newly created Locator Bone and its Parent bone to be (if it has one)
   mmNewRigStoreArray = []
   #OldRigStoreArray will hold on to the old rig bones
   mmOldRigStoreArray = []

   mmCounterA = 0

   for objectName in selectionList:

      #Each new bone is given an array to store its name and its parent
      mmNewBoneStoreArray = []
      #Need to store the old bones as well
      mmOldBoneStoreArray = []

      #Store the name of the bone into the two arrays
      mmNewBoneStoreArray.append(objectName)
      mmOldBoneStoreArray.append(objectName)
      
      objectParent = cmds.listRelatives( objectName, p = 1 )

      #If there is a parent of the current bone, store it here.
      if ( objectParent != None ):
         objectParent[0] += '_loc'
      
         mmNewBoneStoreArray.append(objectParent)
         mmOldBoneStoreArray.append(objectParent)
               
      elif ( objectName == "root" ):
         mmNewBoneStoreArray.append(None)
         mmOldBoneStoreArray.append(None)

      else:
         mmNewBoneStoreArray.append("root_loc")
         mmOldBoneStoreArray.append("root_loc")

      mmNewRigStoreArray.append(mmNewBoneStoreArray)
      mmOldRigStoreArray.append(mmOldBoneStoreArray)
      
      #Creates a Locator and name it _loc of the thing it is copying off of.
      locatorName = cmds.spaceLocator( name = "%s_loc" % (objectName))[0]
      
      # print "objectName", objectName
      # print "locatorName", locatorName

      #Parent constrain the locator to the object without maintaining offset.
      createdParentConstraint = cmds.parentConstraint( objectName, locatorName, w=1.0, mo=0 )
      
      #Delete Parent contraint so the locator is not being held in place anymore
      cmds.delete( createdParentConstraint )

      #Update the new array with the new locator name
      mmNewRigStoreArray[mmCounterA][0] = locatorName
      
      cmds.parent( locatorName, mmGroup_ExportLocator )
    
      mmCounterA += 1

    
   #---------------------------------------------

   #Take the created array which has all the names of Locators and what should be their Parents
   #     and parent them appropriately

   #print mmNewRigStoreArray

   objectStoredArray= []


   for objectCounter in mmNewRigStoreArray:

      objectStoredArray = objectCounter
      
      #print objectStoredArray
      
      if ( objectStoredArray[1] != None ):
         cmds.parent( objectStoredArray[0], objectStoredArray[1])
      

   #---------------------------------------------

   #Need to parent the geo bones to the locator bones which were created.

   # print "mmNewRigStoreArray", mmNewRigStoreArray
   # print "mmOldRigStoreArray", mmOldRigStoreArray

   mmCounterA = 0

   #First need to unparent all old bones
   for mmObjectName in mmOldRigStoreArray:

      #objectParent = cmds.listRelatives( mmObjectName[1], p = 1 )
      # print "mmObjectName", mmObjectName
      # print "mmObjectName[1]", mmObjectName[1]

      #If there is a parent of the current bone, then deparent.
      if ( mmObjectName[1] != None and mmObjectName[1] != "root_loc" ):
      
         #Remove Parent (set to world)
         cmds.parent( mmObjectName[0], w = 1 )

      elif ( mmObjectName[1] == "root_loc" ):

         #Double check that there is a parent
         mmParent = cmds.listRelatives( mmObjectName[0], p = 1 )
      
         if (mmParent != None):
            #Remove Parent (set to world)
            cmds.parent( mmObjectName[0], w = 1 )

      #Next need to parent constrain all the old bones to the new locators
      #Parent constrain the old bone to the new bone without maintaining offset.
      #    Offset shouldn't actually matter at this point.

      #Need to re-create the locator version of the bone
      locatorVersion = mmObjectName[0] + "_loc"
      mmPadVersion = mmObjectName[0] + "_pad"
      mmControlVersion = mmObjectName[0] + "_Control"

      #Need to add some pad groups to the meshes
      #First create a trash locator for support
      mmMeshPad = cmds.group( em = True )
      mmMeshPad = cmds.rename( mmMeshPad, mmPadVersion )

      #Parent Constrain in the group (to get the location), then delete the constraint, then parent in the original object
      mmTrashPConstraint = cmds.parentConstraint( mmObjectName[0], mmMeshPad )
      cmds.delete(mmTrashPConstraint)

      cmds.select(mmMeshPad)

      cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

      #Set the meshpad to world transforms
      mmGWT.main()

      cmds.DeleteHistory()

      createdParentConstraint = cmds.parentConstraint( locatorVersion, mmMeshPad, w=1.0, mo=0 )
      
      cmds.parent( mmObjectName[0], mmMeshPad )

      cmds.select( mmObjectName[0] )

      #Freezing rotations only
      cmds.makeIdentity( apply = True, t = 0 , r = 1 , s = 0 , n = 0, pn = 1)
       
      #Setting the mmObjectName (the mesh) to world transforms
      mmGWT.main()

      cmds.DeleteHistory()

      cmds.parent( mmMeshPad, mmGroup_Geo )
    
      #---------------------------------------------
         #Create control for meshes, just standard fitall
      #---------------------------------------------

      #Grab the first four letters of the name for checking purposes
      mmTempSideChecker = mmObjectName[0][0:4]
      mmCreatedController = mmCM2M.mmCreateController( mmObjectName[0], "fitall" )

      cmds.parentConstraint( mmCreatedController, locatorVersion )

      #Organize various pieces into proper groups
      #cmds.parent( mmCreatedController, mmGroup_Controls )

      #If there is a parent of the current _loc, then parent it back in, if not, parent it to the control group.
      if ( mmObjectName[1] != None ):
         mmNameSplitter = mmObjectName[1].split("_")

         mmControlParentVersion = mmNameSplitter[0] + "_Control"
      
         #Remove Parent (set to world)
         cmds.parent( mmControlVersion, mmControlParentVersion )

      else:
         cmds.parent( mmCreatedController, mmGroup_Controls )

      #Set values of controller to 0,0,0
      cmds.select( mmCreatedController )
      cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
      
      #Color the controls as appropriate
      if ( mmTempSideChecker == "left" ):
         mmOF.changeColor( 6 )    
      elif ( mmTempSideChecker == "righ" ):
         mmOF.changeColor( 13 )
      else:
         mmOF.changeColor( 14 )

      mmCounterA += 1

   #---------------------------------------------

   #Toggle geo manipulation - we don't want anything selectable.
   mmCM2M.mmToggleGeoManipulation(1)

   #---------------------------------------------
