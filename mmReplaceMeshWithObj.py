"""

Function: mmReplaceMeshWithObj
Description: This function will take an existing rig and replace all the meshes with a new set of meshes from an OBJ.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.mel as mel

#local
import mmReturnFilepathOrFilename as mmRFOF
import mmConvert3DSMaxRigToMayaRig as mmCM2M

######################################
############# DEFINES ################
######################################



def main(*args):
   
   #Ask user where the OBJ is that they want to import
   #Create default path
   mmImportObjFilePath = "C:/Radiant/stonehearth-assets/assets/models/entities/humans/male/voxels/civ.obj"


   mmStartingDirectory = "C:/Radiant/stonehearth-assets/assets/models/entities"
   mmDialogueCaption = "Please select a name and location for OBJ you would like to import."
   mmfileFilterName = 'OBJ'
   mmfileFilterType = '.obj'
   mmFilepathAndFilename = ""
   mmDesiredReturn = 0
   
   #Open a dialogue box where user can input information
   mmImportObjFilePath = cmds.fileDialog2( cap = mmDialogueCaption, fm = 1, fileFilter = mmfileFilterName + ' (*' + mmfileFilterType + ')', selectFileFilter = mmfileFilterName + ' (*' + mmfileFilterType + ')', dir = mmStartingDirectory)

   #------------------------------------------

   #Hold on import so that we can find all the things to replace.
   #Find all the existing mesh pieces
   
   #Separate out only transform nodes
   #Clear Selection
   cmds.select( clear=True )

   #Separate out only Meshes
   mmSelectedMeshesInScene = cmds.ls( type = "mesh" )

   #Find the parent (which should always be the transforms)
   mmSelectedTransformsInScene = cmds.listRelatives( mmSelectedMeshesInScene, parent=True, fullPath=True )

   #Clear Selection
   cmds.select( clear=True )

   #------------------------------------------

   #Store what the old meshes are currently parented to for replacing later.
   #Clear Selection
   cmds.select( clear=True )

   #Separate out only Meshes
   mmSelectedMeshesInScene = cmds.ls( type = "mesh" )

   #Find the parent (which should always be the transforms)
   mmSelectedTransformsInScene = cmds.listRelatives(mmSelectedMeshesInScene, parent=True, fullPath=True)


   #Clear Selection
   cmds.select( clear=True )

   #Create a list to store all the Constraint information
   mmStoredConstraintInfo = []
   mmStoredParentInfo = []
   mmTempList = []
   mmExtraBool = False
   mmOriginalBool = False

   # print "mmSelectedTransformsInScene", mmSelectedTransformsInScene

   for mmTransformName in mmSelectedTransformsInScene:

      #Clear Selection
      cmds.select( clear=True )

      #Select the Transforms
      cmds.select( mmTransformName )

      #Remove the | from the name (not sure where it came from)
      mmTransformNameSplit = mmTransformName.split('|')

      #Check for a mesh inside the 'extra object' group, if you find it, ignore it, then reset checker
      for mmName in mmTransformNameSplit:
         if( mmName == "_Group_ExtraObject"):
            mmExtraBool = True
      
      if ( mmExtraBool ):
         # print "mmTransformName", mmTransformNameSplit
         # print "found extra object: " + mmTransformName
         mmExtraBool = False

      else:

         mmTransformNameLen = len(mmTransformNameSplit)-1

         mmTransformName = mmTransformNameSplit[mmTransformNameLen]

         mmParentName = cmds.listRelatives( p = 1 )
         '''
         #This is old - back when things were parented individually, we had to remove parent and re-parent, but we aren't doing that anymore.
         #Now we need to simply store the parent (or recreate the name later), delete the old mesh and replace it with the new mesh.
         mmParentName = cmds.listRelatives( p = 1 )

         cmds.select( mmParentName, r = 1 )

         mmConstraintName = cmds.listRelatives( type = 'constraint')
         #print mmConstraintName[0]

         
         print "mmTransformName", mmTransformName
         print "mmConstraintName", mmConstraintName
         
         

         mmConstraintConnections = cmds.listConnections( mmConstraintName[0] + ".target" )
         #print "unflattened constraints: "
         #print mmConstraintConnections

         #Need to find and remove duplicates of constraint names
         #Create a list of actual constraint names
         mmConstraintConnectionsFlattened = []

         #Create external counter
         mmCounter = 0

         #For every constraint name, compare it to previous unique names, if it is the same ignore it
         #     if it is new, store it and compare it to future names.
         for mmConstraint in mmConstraintConnections:
            #print "for loop "  + str(mmCounter)

            if (mmCounter != 0):

               #Check versus all other strings
               for mmChecker in mmConstraintConnectionsFlattened:
                  
                  if (mmChecker == mmConstraint):
                     break
                  else:
                     mmConstraintConnectionsFlattened.append(mmConstraint)
                     #print mmConstraintConnectionsFlattened
           
            #Otherwise this is the first iteration and simply append the constraint    
            else:
               mmConstraintConnectionsFlattened.append(mmConstraint)
               #print "first time through"

            #Advance counter
            mmCounter += 1
           
         #print "final flattened constraints: "
         #print mmConstraintConnectionsFlattened

         #Create a temp list with the order: Child, Parent, Type of Constraint
         #-----Assumes that there is only one constraint on each mesh.
         mmTempList = [mmTransformName] + mmConstraintConnectionsFlattened
         #print mmTempList

         #Store the temp list for each transform all in one place
         mmStoredConstraintInfo.append( mmTempList )
         '''
         mmTempList = [mmTransformName, mmParentName]

         #Store the temp list for each transform all in one place
         mmStoredParentInfo.append( mmTempList )
         
         #This code should work - seems designed for it in fact - but doesn't because it cannot think about strings and arrays
         #mmConstraintConnectionsFlattened = mel.eval("stringArrayRemoveDuplicates( " + mmConstraintConnections + " )")
         #print mmConstraintConnectionsFlattened
       
       
   #Clear Selection
   cmds.select( clear=True )

   #print mmStoredConstraintInfo

   #------------------------------------------
   mmImportNamespace = mmRFOF.main( mmImportObjFilePath, 1 )
   #Import in OBJ of user's choosing
   cmds.file( mmImportObjFilePath, i = True, type = "OBJ", ignoreVersion = True, ra = True, mergeNamespacesOnClash = False, namespace = mmImportNamespace, options = "mo=1;lo=0", pr = True )

   #------------------------------------------

   #Store OBJ imported names

   #Store what the new meshes names are
   #Clear Selection
   cmds.select( clear=True )

   #Separate out only Meshes
   mmSelectedMeshesInScene = cmds.ls( type = "mesh" )

   #Find the parent (which should always be the transforms)
   mmSelectedTransformsInScene = cmds.listRelatives(mmSelectedMeshesInScene, parent=True, fullPath=True)

   #Clear Selection
   cmds.select( clear=True )

   #Create a list to store all the imported mesh names
   mmStoredImportedTransformNames = []
   mmStoredModifiedTransformNames = []
   mmNewTransformList = []
   mmTempList = []

   #Want to store the prefix we are removing
   mmPrefixRemoved = ""

   # print "mmSelectedTransformsInScene", mmSelectedTransformsInScene

   for mmTransformName in mmSelectedTransformsInScene:

      # print ""
      # print "starting loop"
      # print "mmTransformName", mmTransformName
      

      #Remove the | from the name (not sure where it came from)
      mmTransformNameSplit = mmTransformName.split('|')

      #Check for a mesh inside the '_Group_ExtraObject' group, if you find it, ignore it, then reset checker
      for mmName in mmTransformNameSplit:
         if( mmName == "_Group_ExtraObject"):
            mmExtraBool = True

         #Also need to check for an original mesh, which would be inside the '_Group_Geometry' group, if you find it, ignore it, then reset checker
         if( mmName == "_Group_Geometry"):
            mmOriginalBool = True

      
      if ( mmExtraBool ):
         # print "found extra object: " + mmTransformName
         mmExtraBool = False

      elif ( mmOriginalBool ):
         # print "found original object: " + mmTransformName
         mmOriginalBool = False

      else:

         #Clear Selection
         cmds.select( clear=True )

         #Select the Transforms
         cmds.select( mmTransformName )

         #Store name
         #mmStoredImportedTransformNames.append( mmTransformName )

         #Remove the ':' from the name and take the second portion of it
         #     This grabs only the newly imported meshes
         mmTransformName = mmTransformNameSplit[1]
         mmNewTransformList = mmTransformName.split(':')

         if ( len(mmNewTransformList) > 1 ):

            mmPrefixRemoved = mmNewTransformList[0]
            mmNewTransformName = mmNewTransformList[1]

            #Store new name we want
            mmStoredModifiedTransformNames.append( mmNewTransformName )

            #Delete the old mesh
            #Need to find if old mesh exists
            #     (it should, but don't want to rely on that)
            if ( cmds.objExists( mmNewTransformName ) ):
               cmds.delete( mmNewTransformName )

               # print "mmNewTransformName", mmNewTransformName
               # print "mmTransformName", mmTransformName

               #Rename the imported mesh to what the original was named (we are taking off the pre-fix name of the file)
               cmds.rename( mmTransformName, mmNewTransformName )

   #Delete any unused nodes - otherwise more and more are created each time script is run
   #  This is things like material nodes and what not
   mel.eval( 'MLdeleteUnused;' )


   #------------------------------------------

   #Want to brighten material's Ambient color so it looks like it is supposed to

   #setAttr "civ1:civ_simpletex1.ambientColor" -type double3 1 1 1 ;
   # print ""
   # print "Trying to fix the material brought in to be the proper ambient color."
   # print "mmPrefixRemoved", mmPrefixRemoved
   # print "mmImportNamespace", mmImportNamespace
   cmds.setAttr( mmPrefixRemoved + ":" + mmImportNamespace + "_simpletex1.ambientColor", 1,1,1, type = "double3")

   #------------------------------------------
   '''
   #Parent constrain the newly renamed imported mesh to the same thing the original was

   #print mmStoredConstraintInfo

   #Check all stored names
   for mmStoredName in mmStoredModifiedTransformNames:

      #Compare stored names to all stored constraint names
      for mmToBeChecked in mmStoredConstraintInfo:

         if ( mmToBeChecked[0] == mmStoredName ):
            mmCreatedParentConstraint = cmds.parentConstraint( mmToBeChecked[1], mmToBeChecked[0], w=1.0, mo=1)
   '''


   #No longer parent constrain the newly renamed imported mesh to the same thing the original was, now just parent.

   #print mmStoredConstraintInfo

   #Check all stored names
   for mmStoredName in mmStoredModifiedTransformNames:

      #Compare stored names to all stored constraint names
      for mmToBeChecked in mmStoredParentInfo:

         if ( mmToBeChecked[0] == mmStoredName ):
            cmds.parent( mmToBeChecked[0], mmToBeChecked[1])

   #------------------------------------------

   #Deselect everything
   cmds.select( cl = 1 )

   #------------------------------------------

   #Save the file.
   #-----Disabling an auto-save, don't want to accidentally save something which is bad.
   #cmds.file( force = 1, save = 1, type = 'mayaAscii' )
   #Yeah, not going to re-enable.  This is a script which is attempting to fix something,
   #  If it breaks everything instead, then the user is screwed.

   #------------------------------------------

   #Do need to toggle geo lock, as this is disabling what was there.. should we check and then restore to what it was?
   #  No, just disable.  99% of the time, we want geo manipulation disabled.
   mmCM2M.mmToggleGeoManipulation(1)


   #------------------------------------------
