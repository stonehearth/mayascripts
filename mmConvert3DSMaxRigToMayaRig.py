"""

Function: mmConvert3DSMaxRigToMayaRig
Description: This function will take a base rig which has been 'sent to' from 3dsmax to maya and convert it into a rig within maya.


"""
#This treats everything as a float if it matters (during division only)
from __future__ import division

__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.mel as mel
import time
import collections

#Local
import mmScaleDownFrom3DSMax as mmSDF3M
import mmReturnFilepathOrFilename as mmRFOF
import mmOrganizationFunctions as mmOF
import mmSelectAnimatingParts as mmSAP
import mmRiggingFunctions as mmRF
import mmGetWorldTrans as mmGWT
import mmCreateLocAndParent as mmCLAP

######################################
############# GLOBALS ################
######################################

mmRigOffsetX = 0
mmRigOffsetZ = 0

#Need to Organize!
#Create empty groups to store stuff in

mmGroup_Hidden = None
mmGroup_MainBones = None
mmGroup_Controls = None
mmGroup_ExtraControls = None
mmGroup_BuildLocator = None
mmGroup_Geo = None
mmGroup_ExportLocator = None
mmGroup_ExtraObject = None

######################################
############# DEFINES ################
######################################

    
'''
#Need to create basic groups to store things in
'''
def mmCreateRigGroups(*args):

    '''
    mmCreateRigGroups()

    #Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''

    #Grab Global Group Variables
    #   Declare 'global' so we can manipulate their values
    global mmGroup_Hidden
    global mmGroup_MainBones
    global mmGroup_Controls
    global mmGroup_ExtraControls
    global mmGroup_BuildLocator
    global mmGroup_Geo
    global mmGroup_ExportLocator
    global mmGroup_ExtraObject

    mmGroup_Hidden = mmEnsureGroupExists( "_Group_Hidden" )
    mmGroup_MainBones = mmEnsureGroupExists( "_Group_MainBones" )
    mmGroup_Controls = mmEnsureGroupExists( "_Group_Controls" )
    mmGroup_ExtraControls = mmEnsureGroupExists( "_Group_ExtraControls" )
    mmGroup_BuildLocator = mmEnsureGroupExists( "_Group_BuildLocators" )
    mmGroup_Geo = mmEnsureGroupExists( "_Group_Geometry" )
    mmGroup_ExportLocator = mmEnsureGroupExists( "_Group_ExportLocators" )
    mmGroup_ExtraObject = mmEnsureGroupExists( "_Group_ExtraObject" )

    #Attempts to parent the groups properly - don't like that it tosses warnings.
    if (mmGroup_ExtraControls != None):
        mmParentChecker = cmds.listRelatives(mmGroup_ExtraControls, p = 1)
        if ( mmParentChecker == None or len(mmParentChecker) > 0 and mmParentChecker[0] != mmGroup_Controls):
            try:
                cmds.parent(mmGroup_ExtraControls, mmGroup_Controls)
            except:
                pass

    return None

'''
#This function will check if a name of an object exists, and if not - create it.
'''
def mmEnsureGroupExists( mmActualName = "", *args):

    mmGroup_Checker = cmds.objExists(mmActualName)
    if ( not mmGroup_Checker ):
        mmGlobalName = cmds.group( em = True, n = mmActualName )
    else:
        mmGlobalName = mmActualName

    return str(mmGlobalName)

'''
#This function will convert a 3dsmax file (converted into maya) of an animated mesh into a useful maya file.
'''
def main(*args):
    
    #Grab Global Group Variables
    global mmGroup_Hidden
    global mmGroup_MainBones
    global mmGroup_Controls
    global mmGroup_BuildLocator
    global mmGroup_Geo
    global mmGroup_ExportLocator


    mmGroup_Hidden = "_Group_Hidden"
    mmGroup_MainBones = "_Group_MainBones" 
    mmGroup_Controls = "_Group_Controls"
    mmGroup_BuildLocator = "_Group_BuildLocators"
    mmGroup_Geo = "_Group_Geometry"
    mmGroup_ExportLocator = "_Group_ExportLocators"

    #Select all items we want in the scene

    #---------------------------------------------

    #Store what the new mesh's names are
    #Clear Selection
    cmds.select( clear=True )

    #Grab all locators and meshes in the scene
    mmAnimatingInScene = cmds.ls( type = ("locator", "mesh") )

    #Grab their Parents (the transforms)
    selectionList = cmds.listRelatives(mmAnimatingInScene, parent=True, fullPath=0)

    #---------------------------------------------
    
    #Need to remove duplicates and sort
    selectionList = list(set(selectionList))
    selectionList.sort()

    #---------------------------------------------

    #Select the transforms
    cmds.select(selectionList)

    #Store selection list for later
    originalSelectionList = list(selectionList)

    #---------------------------------------------

    #Remove all animations which already exist - its a rig, there should be no animations
    cmds.cutKey( cl = 1 )
    
    #---------------------------------------------
    
    #Create a locator, and then create and destroy a parent constraint to get the locator to the place it should be at.
    
    #RigStoreArray will hold on to each newly created Locator Bone and its Parent bone to be (if it has one)
    mmNewRigStoreArray = []

    #OldRigStoreArray will hold on to the old rig meshes
    mmOldRigStoreArray = []

    mmCounterA = 0
    
    for objectName in selectionList:

        #Each new bone is given an array to store its name and its parent
        mmNewBoneStoreArray = []
        #Need to store the old bones and their parents as well
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
        
        else:
            mmNewBoneStoreArray.append(None)
            mmOldBoneStoreArray.append(None)
        
        mmNewRigStoreArray.append(mmNewBoneStoreArray)
        mmOldRigStoreArray.append(mmOldBoneStoreArray)
        
        #Creates a Locator and name it _loc of the thing it is copying off of.
        locatorName = cmds.spaceLocator( name = "%s_loc" % (objectName))[0]
        
        #Parent constrain the locator to the object without maintaining offset.
        mmTempPC = cmds.pointConstraint( objectName, locatorName, w=1.0, mo=0 )
        
        #Delete Parent contraint so the locator is not being held in place anymore
        cmds.delete( mmTempPC )

        if ( locatorName == "root_loc" ):
            mmRootLocHolder = locatorName

        #Update the new array with the new locator name
        mmNewRigStoreArray[mmCounterA][0] = locatorName
        
        mmCounterA += 1

    #---------------------------------------------

    #Take the created array which has all the names of Locators and what should be their Parents
    #     and parent them appropriately

    for objectCounter in mmNewRigStoreArray:
    
        if ( objectCounter[1] != None ):
            cmds.parent( objectCounter[0], objectCounter[1])
        

    #---------------------------------------------
    
    #Need to parent the geo bones to the locator bones which were created.

    #First need to unparent all old bones
    for objectName in mmOldRigStoreArray:

        #If there is a parent of the current bone, then deparent.
        if ( objectName[1] != None ):
        
            #Remove Parent (set to world)
            cmds.parent( objectName[0], w = 1 )

        #Next need to parent constrain all the old bones to the new locators
        #Parent constrain the old bone to the new bone without maintaining offset.
        #    Offset shouldn't actually matter at this point.

        #Need to re-create the locator named version of the bone
        locatorVersion = objectName[0] + "_loc"
        mmPadVersion = objectName[0] + "_pad"

        #Need to add some pad groups to the meshes
        #First create a trash locator for support
        mmMeshPad = cmds.group( em = True )
        mmMeshPad = cmds.rename( mmMeshPad, mmPadVersion )

        #Parent Constrain in the group (to get the location), then delete the constraint, then parent in the original object
        mmTrashPConstraint = cmds.parentConstraint( objectName[0], mmMeshPad )
        cmds.delete(mmTrashPConstraint)

        cmds.select(mmMeshPad)

        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

        #Set the meshpad to world transforms
        mmGWT.main()

        cmds.DeleteHistory()

        createdParentConstraint = cmds.parentConstraint( locatorVersion, mmMeshPad, w=1.0, mo=1 )

        cmds.parent( objectName[0], mmMeshPad )

        cmds.select( objectName[0] )

        #Freezing rotations only
        cmds.makeIdentity( apply = True, t = 0 , r = 1 , s = 0 , n = 0, pn = 1)
        
        #Setting the objectName (the mesh) to world transforms
        mmGWT.main()

        cmds.DeleteHistory()


        cmds.parent( mmMeshPad, mmGroup_Geo )


        
    #---------------------------------------------
    
    #Next we need to create an ATOM template for bringing animations across onto this rig.
    #Don't need this, we're doing it by name, but saving the code here just in case
    '''
    #Need to grab the selection which we will want in the long run
    originalSelectionList = mmSAP.main()
    
    #Python version of Atom Template Creator - saves it as the file name specified
    #***This automatically exports it as the hardcoded name, but need user to control where it goes.
    #mel.eval('atomTemplateCallback  OptionBoxWindow|formLayout242|tabLayout37|formLayout244|tabLayout38|columnLayout172 1; hideOptionBox;')
    
    #Ask the user what location the Character Template should be saved to.
    mmStartingDirectory = "C:/Users/mmalley/Documents/Work/CharacterTemplates"
    mmDialogueCaption = "Please select a name and location for the Character Template."
    mmTemplateName = "HumanMaleOriginal"
    
    #Open a dialogue box where user can input information
    mmTemplateFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 0, fileFilter = 'Template (*.template)', selectFileFilter = 'template (*.template)', dir = mmStartingDirectory)
    #print mmTemplateFilename[0]
    
    mmTemplateName = mmRFOF.main( mmTemplateFilename, 1 )

    if (mmTemplateFilename[0]):
        #cmds.containerTemplate( "HumanMaleOriginal", force = 1, edit = 1, layoutMode = 1, addView = 0, fromSelection = 1, useHierarchy = 1, allKeyable = 1, save = 1, fileName = mmTemplateFilename[0] )
        cmds.containerTemplate( mmTemplateName, force = 1, fromSelection = 1, useHierarchy = 1, allKeyable = 1 )
        cmds.containerTemplate( mmTemplateName, save = 1, fileName = mmTemplateFilename[0] )
        cmds.containerTemplate( mmTemplateName, force = 1, edit = 1, layoutMode = 1, addView = 0, fromSelection = 1, useHierarchy = 1, allKeyable = 1 )
        cmds.containerTemplate( mmTemplateName, save = 1, fileName = mmTemplateFilename[0] )
    
    '''

    #---------------------------------------------
    
    #Need to save out the file as .MA
    
    #Ask the user where to save the rig.

    mmStartingDirectory = "C:/Radiant/stonehearth-assets/assets/models/"
    mmDialogueCaption = "Please choose a name and decide where to save the new Rig."
    
    #Open a dialogue box where user can input information
    mmRigFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 0, fileFilter = 'MA (*.ma)', selectFileFilter = 'MA (*.ma)', dir = mmStartingDirectory )
    
    if (mmRigFilename):
        cmds.file( rename = mmRigFilename[0] )
        
        cmds.file( force = 1, save = 1, type = 'mayaAscii' )


    #Need to move the rig to 0,0, and store its offset for setting it back later
    # global mmRigOffsetX
    # mmRigOffsetX = cmds.getAttr( mmRootLocHolder + ".translateX" )
    # global mmRigOffsetZ
    # mmRigOffsetZ = cmds.getAttr( mmRootLocHolder + ".translateZ" )

    # cmds.setAttr( mmRootLocHolder + ".translateX", 0 )
    # cmds.setAttr( mmRootLocHolder + ".translateZ", 0 )

    #---------------------------------------------

    #Organization
    #had to turn this off because it was erroring without calling the other script - should set this up so there wont be errors (however that is done).
    #cmds.parent( mmMeshPad, mmGroup_Geo )

    cmds.parent( "root_loc", mmGroup_ExportLocator )

    cmds.select(cl = 1)

'''
#For when you want to create a new rig out of an existing one, this will clean everything up for you.

#? **** This function does not work if scale has been added - must fix at some point.
'''
def mmDissassembleRig(*args):

    #Grab all meshes - 'root' should also be grabbed
    mmMeshesInScene = mmSAP.main(["mesh"])
    mmMeshesInScene.append("root")

    #Grab their locs and save their parents out based on name
    mmLocTransformList = []
    mmMeshAndParentList = []

    for mmMesh in mmMeshesInScene:
        mmMeshAndParent = []

        if ( mmMesh == "ATTOVERCOG" ):
            cmds.delete(mmMesh)
            cmds.delete(mmMesh + "_loc")
        else:
            mmLocTransformList.append(mmMesh + "_loc")

            mmMeshAndParent.append(mmMesh)

            if ( mmMesh != "root" ):
                
                mmLocParent = cmds.listRelatives(mmMesh + "_loc", p = 1)[0]

                #If there is a 'pad#', ignore it - just pretend its not there
                mmMeshParent = mmRecursivePadDiver( mmMesh, mmLocParent )

                mmMeshAndParent.append(mmMeshParent)

            mmMeshAndParentList.append(mmMeshAndParent)

    for mmMeshAndParent in mmMeshAndParentList:
        #Reparent all meshes based on loc structure - 'root' should also be grabbed
        if ( mmMeshAndParent[0] != "root" ):

            cmds.parent(mmMeshAndParent[0], mmMeshAndParent[1])
            
        else:
            cmds.parent(mmMeshAndParent[0], w = 1)

        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)


    #Then delete all the stuff we don't want - should be in folders.

    mmGroup_HiddenChecker = cmds.ls("_Group_Hidden")
    mmGroup_MainBonesChecker = cmds.ls("_Group_MainBones")
    mmGroup_ControlsChecker = cmds.ls("_Group_Controls")
    mmGroup_BuildLocatorChecker = cmds.ls("_Group_BuildLocators")
    mmGroup_GeoChecker = cmds.ls("_Group_Geometry")
    mmGroup_ExportLocatorChecker = cmds.ls("_Group_ExportLocators")
    mmGroup_ExtraObjectChecker = cmds.ls("_Group_ExtraObject")

    if ( mmGroup_HiddenChecker != [] ):
        cmds.delete("_Group_Hidden")

    if ( mmGroup_MainBonesChecker != [] ):
        cmds.delete("_Group_MainBones")

    if ( mmGroup_ControlsChecker != [] ):
        cmds.delete("_Group_Controls")

    if ( mmGroup_BuildLocatorChecker != [] ):
        cmds.delete("_Group_BuildLocators")

    if ( mmGroup_GeoChecker != [] ):
        cmds.delete("_Group_Geometry")

    if ( mmGroup_ExportLocatorChecker != [] ):
        cmds.delete("_Group_ExportLocators")

    if ( mmGroup_ExtraObjectChecker != [] ):
        cmds.delete("_Group_ExtraObject")

    #Toggle the geo to be selectable again
    mmToggleGeoManipulation()

    cmds.setAttr("root.visibility", 1)

    return None

'''
#This function will recursively check down a hierarchy until it finds a parent which is not a 'pad', then returns it.
'''
def mmRecursivePadDiver( mmMesh = None, mmLocParent = None, *args):

    mmNameChecker = mmLocParent.split("_")

    if ( mmNameChecker[len(mmNameChecker)-1][0:3] != "pad" or
    mmNameChecker[len(mmNameChecker)-1][0:3] != "Pad" or 
    mmNameChecker[len(mmNameChecker)-1][0:9] != "OffsetPad" ):
        mmMeshParent = mmNameChecker[0]
    else:
        mmLocPadParent = cmds.listRelatives(mmLocParent, p = 1)[0]
        mmMeshParent = mmRecursivePadDiver(mmMesh, mmLocPadParent)

    return mmMeshParent

'''
#Need to create a basic 'plop down' of all reverse foot controls needed, then have the user set them up.
'''
def mmCreateLimbPrimer( mmBoolCheckList = [], mmSelectedLimbPieceList = [], *args ):
    #Need to grab one set of limb's selections at a time, to do this:
    #   Only grab Left Limbs/Feet - Must count on user to do this
    #
    #   Trash Locator Button-
    #       Have a button which creates a trash locator (name would identify it as this type of locator), user then includes that in their selections
    #
    #   Toggle Buttons-
    #       Mirror Limb
    #           Default Yes - a "right" version of the "left" originally selected should be found and duplicated across.
    #           No - no other version is looked for - could simply name locators "left" or "center" for differentiation.
    #       Include Foot
    #           Default Yes - First selection is foot, then shin, then thigh, etc.
    #           No - First selection is "nub" (foot with no foot controls), then shin, then thigh, etc.  (mainly for a scorpion like tail when IK)
    #               For true "tail" with no "nub" - use a trash locator.  Control would still be made, but we can default to FK.
    #       Include Toe
    #           Default No - First selection is foot, then shin, then thigh, etc.
    #           Yes - First selection is toe, then foot, then shin, then thigh, etc.
    #   
    #   Limb Primer Button-
    #       User then selects all bones associated with that limb, starting from toe or foot, working way upwards to thigh
    #       1 - Current Simple Foot System
    #       2 - Is not possible - will either be 1 or 3+
    #       3+- Actual IK System
    #
    #   Then the primer script would create tags on all these meshes/controls (does it have to be meshes? don't think so)
    #       Think we need to get ahead of the loc/mesh/controller hookup - unsure what this means, research!
    #   Including feet primer nulls
    #       
    #       Add an "Include Toe" toggle button?  Then the first selection would be the toe instead?
    #           Need to update the foot scripts to allow for toes on general rigs, and might as well fix hearthlings as well.
    #       Also need "no foot" and "no mirror" toggle buttons - for tails eventually.
 

    #Grab all identifiers that the user has already made - need to ensure we are on a different set
    
    #Grab all tranforms in scene
    mmAllTransformsInScene = cmds.ls(type = "transform")

    mmCurrentHighestCount = -1

    #Find the "identifier" tags if they exist (they may not), and save out what set we are currently on - later allows us to create the 'next set'
    for mmTransform in mmAllTransformsInScene:
        mmSplitWordsFound = mmTransform.split("_")
        if (mmSplitWordsFound[0] == "identifier" and mmSplitWordsFound[1] == "limb" ):

            if ( int(mmSplitWordsFound[3]) > mmCurrentHighestCount ):
                mmCurrentHighestCount = int(mmSplitWordsFound[3])

    #Iterate for "next" set
    mmCurrentHighestCount += 1

    # print "mmCurrentHighestCount", mmCurrentHighestCount

    if ( mmBoolCheckList == [] ):
        if ( cmds.radioButtonGrp("mmLimb_MirrorCheckBox", q = 1, sl = 1) == 1 ):
            mmBool_MirrorCheck = True
        else:
            mmBool_MirrorCheck = False

        if ( cmds.radioButtonGrp("mmLimb_FootCheckBox", q = 1, sl = 1) == 1 ):
            mmBool_FootCheck = True
        else:
            mmBool_FootCheck = False

        if ( cmds.radioButtonGrp("mmLimb_ToeCheckBox", q = 1, sl = 1) == 1 ):
            mmBool_ToeCheck = True
        else:
            mmBool_ToeCheck = False

    else:
        mmBool_MirrorCheck = mmBoolCheckList[0]
        mmBool_FootCheck = mmBoolCheckList[1]
        mmBool_ToeCheck = mmBoolCheckList[2]

    if ( mmSelectedLimbPieceList == [] ):
        mmSelectedLimbPieceList = cmds.ls(sl = 1)

    #Check to see if any of our selected pieces have identifiers on them - if they do, stop this function and warn the user.
    for mmLimbPiece in mmSelectedLimbPieceList:
        mmChildrenToCheck = cmds.listRelatives( mmLimbPiece, c = 1 )
        for mmChild in mmChildrenToCheck:
            mmNameChecker = mmChild.split("_")
            if ( len(mmNameChecker) > 2 and mmNameChecker[0] == "identifier" and mmNameChecker[1] == "limb"):
                print "Some portion of your selection already has limb identifiers on it, please verify selection and remove any other limb identifiers."
                return None

    mmLimbObjectList = []
    mmFootObject = ""
    mmToeObject = ""
    mmIdentifierCurrentSide = ""
    mmIdentifierMirroredSide = ""
    mmSelectedLimbPieceListLen = len(mmSelectedLimbPieceList[0])
    
    #If user wants to mirror this limb
    if ( mmBool_MirrorCheck ):
        #Then look for either 'left' or 'righ'
        if ( mmSelectedLimbPieceList[0][0:4] == "left"
            or mmSelectedLimbPieceList[0][0:4] == "Left"
            or mmSelectedLimbPieceList[0][mmSelectedLimbPieceListLen-4:mmSelectedLimbPieceListLen] == "left"
            or mmSelectedLimbPieceList[0][mmSelectedLimbPieceListLen-4:mmSelectedLimbPieceListLen] == "Left" ):
            mmIdentifierCurrentSide = "left"
            mmIdentifierMirroredSide = "right"
        elif ( mmSelectedLimbPieceList[0][0:5] == "right"
            or mmSelectedLimbPieceList[0][0:5] == "Right"
            or mmSelectedLimbPieceList[0][mmSelectedLimbPieceListLen-5:mmSelectedLimbPieceListLen] == "right"
            or mmSelectedLimbPieceList[0][mmSelectedLimbPieceListLen-5:mmSelectedLimbPieceListLen] == "Right" ):
            mmIdentifierCurrentSide = "right"
            mmIdentifierMirroredSide = "left"

    else:
        #Then name the identifier "center"
        mmIdentifierCurrentSide = "center"

    # print "mmIdentifierCurrentSide", mmIdentifierCurrentSide

    #If the user wants to have foot controls
    if ( mmBool_FootCheck ):

        #If the user wants a toe
        if ( mmBool_ToeCheck ):

            #Then assign values to appropriate variables
            mmCounter = 0
            for mmLimbPiece in mmSelectedLimbPieceList:

                if ( mmCounter == 0 ):
                    mmToeObject = mmLimbPiece

                elif ( mmCounter == 1 ):
                    mmFootObject = mmLimbPiece

                else:
                    mmLimbObjectList.append(mmLimbPiece)

                mmCounter += 1

            ###################################################################################
            #Then call 'mmCreateRevFootRigPrimer' with a toe
            #?  This isn't possible atm - need to fix mmCreateRevFootRigPrimer to allow it.
            ###################################################################################

            cmds.select( cl = 1 )
            mmCreateRevFootRigPrimer( [mmFootObject, mmToeObject], mmCurrentHighestCount )

        #else they don't want a toe
        else:

            #Then assign values to appropriate variables
            mmCounter = 0
            for mmLimbPiece in mmSelectedLimbPieceList:

                if ( mmCounter == 0 ):
                    mmFootObject = mmLimbPiece

                else:
                    mmLimbObjectList.append(mmLimbPiece)

                mmCounter += 1

            #Then call 'mmCreateRevFootRigPrimer' without a toe
            cmds.select( cl = 1 )
            mmCreateRevFootRigPrimer( [mmFootObject], mmCurrentHighestCount )

    #Else, they dont want foot controls
    else:

        #Then assign values to appropriate variables
        for mmLimbPiece in mmSelectedLimbPieceList:

            mmLimbObjectList.append(mmLimbPiece)

        #Don't think anything else needs to happen here - possibly arrange the order of selections (or names to the selections)
        #   Must have a foot yes?  Yes - need something there to control the IK, but no, don't need foot controls - which is what this is asking
        #   For true "tail" with no "nub" - use a trash locator for the foot.  Control would still be made, but we can default to FK (somehow).

    #Take the various selections and remember them as what they should be, then create identifiers for each piece as appropriate on the provided selection
    
    #----------------------------------------------------
    mmNewTrashObjects = []

    mmCounter = 0
    #Need to identify any trash locators and deal with them - as other functions use names to name things.

    for mmLimbPiece in mmLimbObjectList:

        mmSplitWordsFound = mmLimbPiece.split("_")

        if ( mmSplitWordsFound[0] == "identifier" and mmSplitWordsFound[1] == "trash" ):

            mmLimbObjectList[mmCounter] = cmds.rename(mmLimbPiece, mmIdentifierCurrentSide + "_" + mmLimbPiece )
            mmLimbPiece = mmLimbObjectList[mmCounter]

            #If we are mirroring, need to duplicate any trash locators across the root.
            if ( mmBool_MirrorCheck ):

                if (mmIdentifierCurrentSide == "left"):
                    mmNewLocatorName = "right"
                elif (mmIdentifierCurrentSide == "right"):
                    mmNewLocatorName = "left"

                #Find the X value of the root which is passed in
                mmBaseRootTrans = cmds.getAttr ("root.worldPosition")[0]
                mmBaseRootX = mmBaseRootTrans[0]

                mmTempTransXHolderOrig = cmds.getAttr( mmLimbPiece + ".translateX")
                mmTempTransXHolderAbs = abs(mmBaseRootX) - abs(mmTempTransXHolderOrig)
                mmTempTransXHolder = mmBaseRootX - mmTempTransXHolderAbs

                if ( mmTempTransXHolder == mmTempTransXHolderOrig ):
                    mmTempTransXHolder = mmBaseRootX + mmTempTransXHolderAbs

                mmTempTransYHolder = cmds.getAttr( mmLimbPiece + ".translateY")
                mmTempTransZHolder = cmds.getAttr( mmLimbPiece + ".translateZ")

                mmNameSplitter = mmLimbPiece.split("_")

                mmCounterInner = 0
                for mmName in mmNameSplitter:
                    if ( mmCounterInner == 0 ):
                        mmNewLocatorName = mmNewLocatorName
                    elif ( mmCounterInner + 1 == len(mmNameSplitter) ):
                        mmNewLocatorName = mmNewLocatorName + "_" + str(int(mmName))
                    else:
                        mmNewLocatorName = mmNewLocatorName + "_" + mmName
                    mmCounterInner += 1

                cmds.spaceLocator(  )
                cmds.move( mmTempTransXHolder,mmTempTransYHolder,mmTempTransZHolder )
                mmRightLoc = cmds.rename(mmNewLocatorName)

        mmCounter += 1

    # for mmObject in mmNewTrashObjects:
    #     mmLimbObjectList.append(mmObject)


    #----------------------------------------------------


    #----------------------------------------------------

    if ( mmToeObject != "" ):
        #Then we should tag the toe appropriately
        
        mmCreateTagOnObject( mmToeObject, "identifier_limb_set_" + str(mmCurrentHighestCount) + "_" + mmIdentifierCurrentSide + "_toe_#" )
        if ( mmBool_MirrorCheck ):
            if (mmIdentifierCurrentSide == "left"):
                mmToeObject = "right" + mmToeObject[4:]
            elif (mmIdentifierCurrentSide == "right"):
                mmToeObject = "left" + mmToeObject[5:]

            mmCreateTagOnObject( mmToeObject, "identifier_limb_set_" + str(mmCurrentHighestCount+1) + "_" + mmIdentifierMirroredSide + "_toe_#" )

    if ( mmFootObject != "" ):
        #Then we should tag the foot appropriately

        mmCreateTagOnObject( mmFootObject, "identifier_limb_set_" + str(mmCurrentHighestCount) + "_" + mmIdentifierCurrentSide + "_foot_#" )
        if ( mmBool_MirrorCheck ):
            if (mmIdentifierCurrentSide == "left"):
                mmFootObject = "right" + mmFootObject[4:]
            elif (mmIdentifierCurrentSide == "right"):
                mmFootObject = "left" + mmFootObject[5:]

            mmCreateTagOnObject( mmFootObject, "identifier_limb_set_" + str(mmCurrentHighestCount+1) + "_" + mmIdentifierMirroredSide + "_foot_#" )

            mmDuplicateFootAndInvert( "root", mmCurrentHighestCount)
        else:
            #Else we do not want to duplicate or invert, just adjust the names as appropriate
            mmDuplicateFootAndInvert( "root", mmCurrentHighestCount, False)
    
    mmCounter = 0
    for mmLimbPiece in mmLimbObjectList:
        #Then each limb piece should be tagged appropriately

        mmCreateTagOnObject( mmLimbPiece, "identifier_limb_set_" + str(mmCurrentHighestCount) + "_" + mmIdentifierCurrentSide + "_limbPiece_#" )
        if ( mmBool_MirrorCheck ):
            if (mmIdentifierCurrentSide == "left"):
                mmLimbPiece = "right" + mmLimbPiece[4:]
            elif (mmIdentifierCurrentSide == "right"):
                mmLimbPiece = "left" + mmLimbPiece[5:]

            mmCreateTagOnObject( mmLimbPiece, "identifier_limb_set_" + str(mmCurrentHighestCount+1) + "_" + mmIdentifierMirroredSide + "_limbPiece_#" )

        mmCounter += 1

    return None

'''
#Need to create a basic 'plop down' of all reverse foot controls needed, then have the user set them up.
'''
def mmCreateTrashLimbLoc( *args ):
    cmds.spaceLocator( n = "identifier_trash_#" )

'''
#Need to create a more intelligent 'plop down' of all reverse foot controls needed, then have the user adjust them if needed.
'''
def mmCreateRevFootRigPrimer( mmSelectedFeetMeshList = [], mmPassedInLimbSet = "", *args ):
    #Create Locators for Reverse Foot Rig

    mmToeMesh = ""
    mmCurrentFoot = ""

    #If objects are not passed in, grab selection.
    if ( mmSelectedFeetMeshList == [] ):
        mmSelectedFeetMeshList = cmds.ls(sl = 1)

        #If no selection, error out, must have selection.
        if ( mmSelectedFeetMeshList == [] ):
            print "Invalid selection for mmC3MTMR.mmCreateRevFootRigPrimer"
            return None

    if ( mmPassedInLimbSet == "" ):
        print "Must provide the limb set # which this foot belongs to in mmC3MTMR.mmCreateRevFootRigPrimer"
        return None
    else:
        mmPassedInLimbSet = str(mmPassedInLimbSet)

    # print "mmPassedInLimbSet", mmPassedInLimbSet

    #Check if there is a second object in the list - if yes, this is our toe
    if ( len(mmSelectedFeetMeshList) > 1 ):

        mmToeMesh = mmSelectedFeetMeshList[1]

        mmToe_BoundingBoxList = mmRF.mmGrabBoundingBoxInfo( [mmToeMesh] )

    mmCurrentFoot = mmSelectedFeetMeshList[0]
    # print "mmCurrentFoot", mmCurrentFoot

    mmFoot_BoundingBoxList = mmRF.mmGrabBoundingBoxInfo( [mmCurrentFoot] )    

    #mmGrabBoundingBoxInfo returns mmDictOfBoundingBoxLists with this information:
    # [
    #     "min":       [X, Y, Z],
    #     "midPoint":  [X, Y, Z],
    #     "max":       [X, Y, Z],
    #     "total":     [X, Y, Z],
    #     "pivot":     [X, Y, Z]
    # ]

    #If we do want a toe
    if ( mmToeMesh != "" ):
        #Store the foot loc on the newly created heel locator
        mmEmptyGroup = cmds.group( em = 1, name = "ParentLocIs_" + mmCurrentFoot )
        #?  Change this to an identifier?

        #Start Creating locators based on where the root is
        #Heel Pivot
        mmLeftFootPivotRear = cmds.spaceLocator(  )
        mmLeftFootPivotRear = cmds.rename("Foot_Pivot_Rear_0_Locator_LimbSet_" + mmPassedInLimbSet )
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmFoot_BoundingBoxList["min"][1], mmFoot_BoundingBoxList["min"][2], r = 1 )

        #parent in the empty group node to store the data we need
        cmds.parent( mmEmptyGroup, mmLeftFootPivotRear )
        
        #Ball of Foot Pivot
        mmBallPivotZ = mmToe_BoundingBoxList["min"][2] + mmToe_BoundingBoxList["total"][2]/3
        mmLeftFootPivotBall = cmds.spaceLocator(  )
        mmLeftFootPivotBall = cmds.rename("Foot_Pivot_Ball_1_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmFoot_BoundingBoxList["min"][1], mmBallPivotZ, r = 1 )

        #Toe Tip Pivot
        mmLeftFootPivotFront = cmds.spaceLocator(  )
        mmLeftFootPivotFront = cmds.rename("Foot_Pivot_Front_2_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmFoot_BoundingBoxList["min"][1], mmToe_BoundingBoxList["max"][2], r = 1 )

        #Toe bend pivot
        mmLeftFootPivotToe = cmds.spaceLocator(  )
        mmLeftFootPivotToe = cmds.rename("Foot_Pivot_Toe_3_Locator_LimbSet_" + mmPassedInLimbSet)
        mmToePivotY = mmToe_BoundingBoxList["min"][1] + mmToe_BoundingBoxList["total"][1]/3
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmToePivotY, mmToe_BoundingBoxList["min"][2], r = 1 )

        #Offset pivot of mesh - specifically for human male
        #?  Is this bad to have in non-human rigs?  Its useless yes, but doesn't actually do anything.. right?
        #?  Could we remove this locator after creation (or not create it) and still build the foot?
        #?      Later numbers would be wrong..
        mmAnklePivotY = mmFoot_BoundingBoxList["min"][1] + mmFoot_BoundingBoxList["total"][1]*3.0/5
        mmAnklePivotZ = mmFoot_BoundingBoxList["min"][2] + mmFoot_BoundingBoxList["total"][2]*3.5/10
        mmLeftFootPivotAnkle = cmds.spaceLocator(  )
        mmLeftFootPivotAnkle = cmds.rename("Foot_Pivot_Ankle_4_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmAnklePivotY, mmAnklePivotZ, r = 1 )

        #Original pivot of mesh
        mmLeftFootPivotOriginal = cmds.spaceLocator(  )
        mmLeftFootPivotOriginal = cmds.rename("Foot_Pivot_Original_5_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["pivot"][0], mmFoot_BoundingBoxList["pivot"][1], mmFoot_BoundingBoxList["pivot"][2], r = 1  )

        #Inner Pivot
        mmLeftFootPivotInner = cmds.spaceLocator(  )
        mmLeftFootPivotInner = cmds.rename("Foot_Pivot_Inner_6_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["min"][0], mmFoot_BoundingBoxList["min"][1], mmFoot_BoundingBoxList["midPoint"][2], r = 1  )

        #Outer Pivot
        mmLeftFootPivotOuter = cmds.spaceLocator(  )
        mmLeftFootPivotOuter = cmds.rename("Foot_Pivot_Outer_7_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["max"][0], mmFoot_BoundingBoxList["min"][1], mmFoot_BoundingBoxList["midPoint"][2], r = 1  )

    else:
        #mmGrabBoundingBoxInfo returns mmDictOfBoundingBoxLists with this information:
        # [
        #     "min":       [X, Y, Z],
        #     "midPoint":  [X, Y, Z],
        #     "max":       [X, Y, Z],
        #     "total":     [X, Y, Z],
        #     "pivot":     [X, Y, Z]
        # ]

        #Store the foot loc on the newly created heel locator
        mmEmptyGroup = cmds.group( em = 1, name = "ParentLocIs_" + mmCurrentFoot )
        #?  Change this to an identifier?

        #Start Creating locators
        #Heel Pivot
        mmLeftFootPivotRear = cmds.spaceLocator(  )
        mmLeftFootPivotRear = cmds.rename("Foot_Pivot_Rear_0_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmFoot_BoundingBoxList["min"][1], mmFoot_BoundingBoxList["min"][2], r = 1 )

        #parent in the empty group node to store the data we need
        cmds.parent( mmEmptyGroup, mmLeftFootPivotRear )
        
        #Ball of Foot Pivot
        mmBallPivotZ = mmFoot_BoundingBoxList["min"][2] + mmFoot_BoundingBoxList["total"][2]*3.0/4

        mmLeftFootPivotBall = cmds.spaceLocator(  )
        mmLeftFootPivotBall = cmds.rename("Foot_Pivot_Ball_1_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmFoot_BoundingBoxList["min"][1], mmBallPivotZ, r = 1 )

        #Toe Tip Pivot
        mmLeftFootPivotFront = cmds.spaceLocator(  )
        mmLeftFootPivotFront = cmds.rename("Foot_Pivot_Front_2_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["midPoint"][0], mmFoot_BoundingBoxList["min"][1], mmFoot_BoundingBoxList["max"][2], r = 1 )

        #Original pivot of mesh
        mmLeftFootPivotOriginal = cmds.spaceLocator(  )
        mmLeftFootPivotOriginal = cmds.rename("Foot_Pivot_Original_3_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["pivot"][0], mmFoot_BoundingBoxList["pivot"][1], mmFoot_BoundingBoxList["pivot"][2], r = 1  )

        #Inner Pivot
        mmLeftFootPivotInner = cmds.spaceLocator(  )
        mmLeftFootPivotInner = cmds.rename("Foot_Pivot_Inner_4_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["min"][0], mmFoot_BoundingBoxList["min"][1], mmFoot_BoundingBoxList["midPoint"][2], r = 1  )

        #Outer Pivot
        mmLeftFootPivotOuter = cmds.spaceLocator(  )
        mmLeftFootPivotOuter = cmds.rename("Foot_Pivot_Outer_5_Locator_LimbSet_" + mmPassedInLimbSet)
        cmds.move( mmFoot_BoundingBoxList["max"][0], mmFoot_BoundingBoxList["min"][1], mmFoot_BoundingBoxList["midPoint"][2], r = 1  )

    """
    #?  This is trash now, there should always be a selection.
    #?      However.. Keeping around because I think the 6 loc creation bit might be important to hang onto for human rigs without toes.. maybe.. 
    #?          ..those shouldn't exist anymore.  Prolly delete this later.
    #If there is no selection
    else:

        #If there was no selection, then place locators based on world location - these are default values for the human male's feet.
        #Find the trans of the root which is passed in
        mmBaseRootTrans = cmds.getAttr (mmBaseRoot + ".worldPosition")[0]

        #Do we want to add a toe?
        if ( mmAddToe ):
            #Start Creating locators based on where the root is
            mmLeftFootPivotRear = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])

            cmds.move( 3.5,0,-3.5, r = 1  )

            mmLeftFootPivotRear = cmds.rename("Foot_Pivot_Rear_0_Locator_0")
            
            mmLeftFootPivotBall = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,0,4.5, r = 1  )

            mmLeftFootPivotBall = cmds.rename("Foot_Pivot_Ball_1_Locator_0")
            
            mmLeftFootPivotFront = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,0,6.5, r = 1  )

            mmLeftFootPivotFront = cmds.rename("Foot_Pivot_Front_2_Locator_0")

            mmLeftFootPivotToe = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,1,3.5, r = 1  )

            mmLeftFootPivotToe = cmds.rename("Foot_Pivot_Toe_3_Locator_0")
                
            mmLeftFootPivotAnkle = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,3,0, r = 1  )

            mmLeftFootPivotAnkle = cmds.rename("Foot_Pivot_Ankle_4_Locator_0")
            
            mmLeftFootPivotOriginal = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,5,1.5, r = 1  )

            mmLeftFootPivotOriginal = cmds.rename("Foot_Pivot_Original_5_Locator_0")

            mmLeftFootPivotInner = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 0.5,0,1.5, r = 1  )

            mmLeftFootPivotInner = cmds.rename("Foot_Pivot_Inner_6_Locator_0")

            mmLeftFootPivotOuter = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 6.5,0,1.5, r = 1  )

            mmLeftFootPivotOuter = cmds.rename("Foot_Pivot_Outer_7_Locator_0")

        else:

            #Start Creating locators based on where the root is
            mmLeftFootPivotRear = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])

            cmds.move( 3.5,0,-3.5, r = 1  )

            mmLeftFootPivotRear = cmds.rename("Foot_Pivot_Rear_0_Locator_0")
            
            mmLeftFootPivotBall = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,0,4.5, r = 1  )

            mmLeftFootPivotBall = cmds.rename("Foot_Pivot_Ball_1_Locator_0")
            
            mmLeftFootPivotFront = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,0,6.5, r = 1  )

            mmLeftFootPivotFront = cmds.rename("Foot_Pivot_Front_2_Locator_0")

            mmLeftFootPivotAnkle = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,3,0, r = 1  )

            mmLeftFootPivotAnkle = cmds.rename("Foot_Pivot_Ankle_3_Locator_0")
            
            mmLeftFootPivotOriginal = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 3.5,5,1.5, r = 1  )

            mmLeftFootPivotOriginal = cmds.rename("Foot_Pivot_Original_4_Locator_0")

            mmLeftFootPivotInner = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 0.5,0,1.5, r = 1  )

            mmLeftFootPivotInner = cmds.rename("Foot_Pivot_Inner_5_Locator_0")

            mmLeftFootPivotOuter = cmds.spaceLocator(  )
            cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
            
            cmds.move( 6.5,0,1.5, r = 1  )

            mmLeftFootPivotOuter = cmds.rename("Foot_Pivot_Outer_6_Locator_0")
    """

'''
This Function creates a locator for the Clavicle in the default positions of a Human Male Rig.
'''
def mmCreateClavicleRigPrimer( mmBaseRoot = "root" ):
    #Create Locators for Reverse Foot Rig
    
    #Find the trans of the root which is passed in
    mmBaseRootTrans = cmds.getAttr (mmBaseRoot + ".worldPosition")[0]

    mmClavicle = cmds.spaceLocator(  )
    cmds.move(mmBaseRootTrans[0], mmBaseRootTrans[1], mmBaseRootTrans[2])
    
    cmds.move( 1.5, 15.5, 0, r = 1 )
    cmds.scale( 1, 1, 6 )
    mmClavicle = cmds.rename("Clavicle_Locator")

'''
This Function creates a 10x10x10 cube and names it "carry", if one doesn't exist already.
'''
def mmCreateCarryGeo( mmRootControl ):

    #Check all mesh objects in scene to see if there is something with the name "carry"
    mmSelectedItems = mmSAP.main()

    for mmItem in mmSelectedItems:
        if ( mmItem == "carry" ):
            print "Found a Carry - new Carry Mesh not needed."

            cmds.select( cl = 1 )
            return None

    #if not, create a cube as 10x10x10
    mmNewCubeGeo = cmds.polyCube( w = 10, h = 10, d = 10, name = "carry" )[0]

    #Place its pivot at its base (or move its geometry up)
    cmds.select( mmNewCubeGeo + ".vtx[0:7]" )
    cmds.move( 0, 5, 0, r = 1, os = 1, wd = 1 )

    #Find location of Root so we can offset the carry we just made
    mmTempPC = cmds.pointConstraint( mmRootControl, mmNewCubeGeo )

    cmds.delete( mmTempPC )

    #Put the Carry into the appropriate hierarchy
    cmds.parent( mmNewCubeGeo, mmRootControl )

    cmds.select( mmNewCubeGeo, r = 1 )

    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    cmds.select( cl = 1 )

'''
This Function duplicates the locators of a foot rig set up across the YZ axis of the parent node which is passed in.
'''
def mmDuplicateFootAndInvert( mmBaseRoot = "root", mmPassedInLimbSet = "", mmShouldDuplicate = True, *args ):

    if ( mmPassedInLimbSet == "" ):
        print "Must provide the limb set # which this foot belongs to in mmC3MTMR.mmDuplicateFootAndInvert"
        return None

    mmParentLocName = "_Failed_Name_"

    #--------------------------------------------------------

    #Need to find out if there are multiple feet pairs
    #And store them into the appropriate ordered list location - can't sort by the number exactly because we don't know what order they are selected in.
    mmLocatorShapesInScene = cmds.ls( type = ("locator") )
    
    #Find the parent (which should always be the transforms)
    mmLocatorsInScene = cmds.listRelatives(mmLocatorShapesInScene, parent=True, fullPath=0)
    
    #--------------------------------------------------------

    #Create Locators for Reverse Foot Rig
    #First must select the proper locators
    cmds.select( clear=True )

    #Find the X value of the root which is passed in
    mmBaseRootTrans = cmds.getAttr (mmBaseRoot + ".worldPosition")[0]
    mmBaseRootX = mmBaseRootTrans[0]

    #Select all Locators
    mmLocatorShapesInScene = cmds.ls( type = ("locator") )

    #Find the parent (which should always be the transforms)
    mmLocatorsInScene = cmds.listRelatives(mmLocatorShapesInScene, parent=True, fullPath=0)
    
    mmDesiredLocatorsInScene = []
    
    for mmLocator in mmLocatorsInScene:
        mmListOfLocName = mmLocator.split("_")

        mmListOfLocNameLen = len(mmListOfLocName)

        if ( mmListOfLocNameLen > 6 and mmListOfLocName[0] == "Foot" and mmListOfLocName[mmListOfLocNameLen-3] == "Locator" and int(mmListOfLocName[mmListOfLocNameLen-1]) == int(mmPassedInLimbSet)):
            mmDesiredLocatorsInScene.append(mmLocator)            

    cmds.select(mmDesiredLocatorsInScene)

    mmLocToLookAt = ""

    #They are not ordered, so we must find the correct one
    # print("mmDesiredLocatorsInScene", mmDesiredLocatorsInScene)
    for mmLocator in mmDesiredLocatorsInScene:
        mmListOfLocName = mmLocator.split("_")

        mmListOfLocNameLen = len(mmListOfLocName)
        # print("mmListOfLocName", mmListOfLocName)

        if (mmListOfLocNameLen > 6):
            mmTempNumber = mmListOfLocName[ mmListOfLocNameLen-4 ]

            # print("mmListOfLocName[ mmListOfLocNameLen-4 ]", mmListOfLocName[ mmListOfLocNameLen-4 ])
            if ( int(mmListOfLocName[ mmListOfLocNameLen-4 ]) == 0 ):
                mmLocToLookAt = mmLocator

    mmChildList = cmds.listRelatives(mmLocToLookAt, c = 1)
    mmChildListLen = len(mmChildList)

    mmCounter = 0

    if ( mmShouldDuplicate ):
        if ( mmChildListLen > 0 ):

            for mmChild in mmChildList:

                if ( mmChild[0:12] == "ParentLocIs_" ):

                    mmParentLocName = mmChild[0:12] + "right" + mmChild[15:len(mmChild)]

        while (mmCounter < len(mmDesiredLocatorsInScene)):
            cmds.select(mmDesiredLocatorsInScene[mmCounter])

            mmTempTransXHolderOrig = cmds.getAttr( mmDesiredLocatorsInScene[mmCounter] + ".translateX")
            mmTempTransXHolderAbs = abs(mmBaseRootX) - abs(mmTempTransXHolderOrig)
            mmTempTransXHolder = mmBaseRootX - mmTempTransXHolderAbs

            if ( mmTempTransXHolder == mmTempTransXHolderOrig ):
                mmTempTransXHolder = mmBaseRootX + mmTempTransXHolderAbs

            mmTempTransYHolder = cmds.getAttr( mmDesiredLocatorsInScene[mmCounter] + ".translateY")
            mmTempTransZHolder = cmds.getAttr( mmDesiredLocatorsInScene[mmCounter] + ".translateZ")

            mmNameSplitter = mmDesiredLocatorsInScene[mmCounter].split("_")
            mmNewLocatorName = "right"

            mmCounterInner = 0
            for mmName in mmNameSplitter:
                if ( mmCounterInner + 1 == len(mmNameSplitter) ):
                    mmNewLocatorName = mmNewLocatorName + "_" + str(int(mmName)+1)
                else:
                    mmNewLocatorName = mmNewLocatorName + "_" + mmName
                mmCounterInner += 1
            
            cmds.spaceLocator(  )
            cmds.move( mmTempTransXHolder,mmTempTransYHolder,mmTempTransZHolder )
            mmRightLoc = cmds.rename(mmNewLocatorName)

            #Right here - store an empty group with the correct name under the locator which points to the parent
            #Only do it if this is locator 0 - the heel
            if ( mmCounter == 0 ):

                mmRightParentLoc = cmds.group( em = 1, name = mmParentLocName )

                cmds.parent( mmRightParentLoc, mmRightLoc )

            cmds.select(mmDesiredLocatorsInScene[mmCounter])
            mmleftLoc = cmds.rename("left_" + mmDesiredLocatorsInScene[mmCounter])

            mmCounter +=1
    else:
        #Else we do not want to duplicate or invert, just change the names accordingly
        if ( mmChildListLen > 0 ):

            for mmChild in mmChildList:

                if ( mmChild[0:12] == "ParentLocIs_" ):

                    mmNameSplitter = mmChild.split("_")

                    mmParentLocName = mmChild[0:12] + mmNameSplitter[1]
                    # print "mmChild", mmChild
                    # print "mmChild[0:12]", mmChild[0:12]
                    # print "mmParentLocName", mmParentLocName

        while (mmCounter < len(mmDesiredLocatorsInScene)):
            cmds.select(mmDesiredLocatorsInScene[mmCounter])

            mmNameSplitter = mmDesiredLocatorsInScene[mmCounter].split("_")
            mmNewLocatorName = "center"

            mmCounterInner = 0
            for mmName in mmNameSplitter:
                if ( mmCounterInner + 1 == len(mmNameSplitter) ):
                    mmNewLocatorName = mmNewLocatorName + "_" + str(int(mmName))
                else:
                    mmNewLocatorName = mmNewLocatorName + "_" + mmName
                mmCounterInner += 1
            
            cmds.select(mmDesiredLocatorsInScene[mmCounter])
            mmCenterLoc = cmds.rename(mmNewLocatorName)
         
            #Right here - store an empty group with the correct name under the locator which points to the parent
            #Be wary, this may break things later
            #Only do it if this is locator 0 - the heel
            if ( mmCounter == 0 ):

                mmCenterParentLoc = cmds.group( em = 1, name = mmParentLocName )

                cmds.parent( mmCenterParentLoc, mmNewLocatorName )

            mmCounter +=1


    cmds.select( cl = 1)

'''
This Function duplicates the locators of a clavical rig set up across the YZ axis.
'''
def mmDuplicateClavicleAndInvert( mmBaseRoot = "root" ):

    global mmGroup_BuildLocator
    mmGroup_BuildLocator = "_Group_BuildLocators"

    #Create Locators for right side clavicle
    #First must select the proper locators
    cmds.select( clear=True )

    #Find the X value of the root which is passed in
    mmBaseRoot = cmds.getAttr (mmBaseRoot + ".worldPosition")[0]
    mmBaseRootX = mmBaseRoot[0]


    #Separate out only Locators
    mmLocatorShapesInScene = cmds.ls( type = ("locator") )

    #print mmSelectedLocatorsInScene

    #Find the parent (which should always be the transforms)
    mmLocatorsInScene = cmds.listRelatives(mmLocatorShapesInScene, parent=True, fullPath=0)
    
    mmDesiredLocatorsInScene = []
    
    for mmLocator in mmLocatorsInScene:
        mmListOfLocName = mmLocator.split("_")
         
        if (mmListOfLocName[0] == "Clavicle" and mmListOfLocName[len(mmListOfLocName)-1] == "Locator"):
            mmDesiredLocatorsInScene.append(mmLocator)
        # print "mmLocator", mmLocator

    cmds.select(mmDesiredLocatorsInScene)

    mmSelected = cmds.ls( sl = 1)
    

    mmTempTransXHolderOrig = cmds.getAttr( mmSelected[0] + ".translateX")
    mmTempTransXHolderAbs = abs(mmBaseRootX) - abs(mmTempTransXHolderOrig)
    mmTempTransXHolder = mmBaseRootX - mmTempTransXHolderAbs
    if ( mmTempTransXHolder == mmTempTransXHolderOrig ):
        mmTempTransXHolder = mmBaseRootX + mmTempTransXHolderAbs

    mmTempTransYHolder = cmds.getAttr( mmSelected[0] + ".translateY")
    mmTempTransZHolder = cmds.getAttr( mmSelected[0] + ".translateZ")
    
    mmTempScaleXHolder = cmds.getAttr( mmSelected[0] + ".scaleX")
    mmTempScaleXHolder = mmTempScaleXHolder * -1
    mmTempScaleYHolder = cmds.getAttr( mmSelected[0] + ".scaleY")
    mmTempScaleZHolder = cmds.getAttr( mmSelected[0] + ".scaleZ")
 
    cmds.spaceLocator(  )
    cmds.move( mmTempTransXHolder,mmTempTransYHolder,mmTempTransZHolder )
    cmds.scale( mmTempScaleXHolder,mmTempScaleYHolder,mmTempScaleZHolder )
    mmRightClavicle = cmds.rename("right" + mmSelected[0])
     
    cmds.select(mmSelected[0])
    mmLeftClavicle = cmds.rename("left" + mmSelected[0])

    #cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
    
    #Organization!
    cmds.parent( mmLeftClavicle, mmGroup_BuildLocator )
    cmds.parent( mmRightClavicle, mmGroup_BuildLocator )

    cmds.select( cl = 1)

'''
This Function creates a basic set of controllers in the default positions of a Human Male Rig.
'''
def mmCreateBasicControllersHumanRig( *args ):

    mmCreatedControllerList = []
    mmTempCreatedController = ""

    #Grab all locators in the scene
    mmAllLocatorsInScene = mmSAP.main(["locator"])

    mmCounter = 0
    mmRunFingersScript = 1

    for mmLoc in mmAllLocatorsInScene:

        if ( mmLoc == "head_loc"):
            mmTempCreatedController = mmCreateController( "head_loc", "fitall" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmTempCreatedController = mmCreateController( "head_loc", "moveall" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "leftHand_loc"):
            mmTempCreatedController = mmCreateController( "leftHand_loc", "hand" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "rightHand_loc"):
            mmTempCreatedController = mmCreateController( "rightHand_loc", "hand" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "mainHand_loc"):
            mmTempCreatedController = mmCreateController( "mainHand_loc", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "offHand_loc"):
            mmTempCreatedController = mmCreateController( "offHand_loc", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "leftFoot_loc"):
            mmTempCreatedController = mmCreateController( "leftFoot_loc", "foot" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "rightFoot_loc"):
            mmTempCreatedController = mmCreateController( "rightFoot_loc", "foot" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "pelvis_loc"):
            mmTempCreatedController = mmCreateController( "pelvis_loc", "belt" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "bodyPosition_loc"):
            mmTempCreatedController = mmCreateController( "bodyPosition_loc", "cog" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""
            
        elif ( mmLoc == "torso_loc"):
            mmTempCreatedController = mmCreateController( "torso_loc", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "leftArm_loc"):
            mmTempCreatedController = mmCreateController( "leftArm_loc", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "rightArm_loc"):
            mmTempCreatedController = mmCreateController( "rightArm_loc", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "rightShoulder_loc"):
            mmTempCreatedController = mmCreateController( "rightShoulder_loc", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "leftShoulder_loc"):
            mmTempCreatedController = mmCreateController( "leftShoulder_loc", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "leftClavicle_Locator"):
            mmTempCreatedController = mmCreateController( "leftClavicle_Locator", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "rightClavicle_Locator" ):
            mmTempCreatedController = mmCreateController( "rightClavicle_Locator", "box" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc == "root_loc" ):
            mmTempCreatedController = mmCreateController( "root_loc", "moveall" )
            mmCreatedControllerList.append(mmTempCreatedController)
            
            mmAllLocatorsInScene[mmCounter] = ""

        elif ( mmLoc[4:9] == "Thumb" or mmLoc[5:10] == "Thumb" or  mmLoc[4:10] == "Finger" or mmLoc[5:11] == "Finger" ):
            if ( mmRunFingersScript ):
                mmCreateController( "fingers", "pin" )
            mmRunFingersScript = 0
            
            mmAllLocatorsInScene[mmCounter] = ""

        else:
            #This should catch everything which I am not accouting for manually.
            mmNameChecker = mmLoc.split("_")
            mmNameCheckerLen = len(mmNameChecker)
            if ( mmNameCheckerLen > 1 and mmNameChecker[1] == "loc" ):

                mmMesh = mmNameChecker[0]

                mmTempCreatedController = mmCreateController( mmMesh, "fitall" )
                mmCreatedControllerList.append(mmTempCreatedController)

                #print "ACTIVATED FITALL CREATION"

            mmAllLocatorsInScene[mmCounter] = ""

        mmCounter += 1

    #Now create an enum on each control so we can add fake things onto it later if we want.
    for mmControl in mmCreatedControllerList:

        cmds.select( mmControl )
        cmds.addAttr( longName="ExtraVis", attributeType='enum', en = "None:", dv=0, k = 1 )

    cmds.select( cl = 1)

'''
This Function creates a basic set of controllers around a generic Rig.
'''
def mmCreateBasicControllersGenericRig( *args ):

    #Grab all locators in the scene
    mmAllLocatorsInScene = mmSAP.main(["locator"])

    mmCounter = 0
    mmRunFingersScript = 1
    mmCreatedControllerList = []
    mmTempCreatedController = ""

    for mmLoc in mmAllLocatorsInScene:

        mmNameChecker = mmLoc.split("_")
        mmNameCheckerLen = len(mmNameChecker)

        if ( mmNameCheckerLen > 1 and mmNameChecker[1] == "loc" ):
            mmMesh = mmNameChecker[0]

            if ( mmLoc == "head_loc"):
                mmTempCreatedController = mmCreateController( mmMesh, "fitall" )
                mmCreatedControllerList.append(mmTempCreatedController)

                mmTempCreatedController = mmCreateController( "head_loc", "moveall" )
                mmCreatedControllerList.append(mmTempCreatedController)
                mmAllLocatorsInScene[mmCounter] = ""

            elif ( mmLoc == "root_loc"):
                mmTempCreatedController = mmCreateController( "root_loc", "moveall" )
                mmCreatedControllerList.append(mmTempCreatedController)
                mmAllLocatorsInScene[mmCounter] = ""

            else:
                #I am not accouting for anything manually, so everything should be automatically created.

                mmTempCreatedController = mmCreateController( mmMesh, "fitall" )
                mmCreatedControllerList.append(mmTempCreatedController)

                mmAllLocatorsInScene[mmCounter] = ""

        mmCounter += 1

    #Create a COG Icon in what we think is the right place - user can move if desired.
    mmTempCreatedController = mmOF.mmCreateDesiredNurbsIcon ( "cog" )

    #Find bounding box values of all meshes in the scene
    mmAllMeshesInScene = mmSAP.main(["mesh"])

    # print "mmAllMeshesInScene", mmAllMeshesInScene

    #Don't look at meshes that begin with "ATT"
    mmMeshesInSceneNotATT = []

    for mmChild in mmAllMeshesInScene:
        if ( not mmChild.startswith('ATT') ):
            mmMeshesInSceneNotATT.append(mmChild)

    # print "mmMeshesInSceneNotATT", mmMeshesInSceneNotATT

    mmBoundingBoxInfo = mmRF.mmGrabBoundingBoxInfo(mmMeshesInSceneNotATT)

    #Move COG into what we assume is the proper place
    cmds.select( mmTempCreatedController )
    cmds.move( mmBoundingBoxInfo["midPoint"][0], mmBoundingBoxInfo["midPoint"][1], mmBoundingBoxInfo["midPoint"][2], r = 1  )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    #Set color to green
    mmOF.changeColor( 14 )

    #Parent the COG under the root & rename it
    cmds.parent(mmTempCreatedController, "root_Control")
    mmTempCreatedController = cmds.rename(mmTempCreatedController, "cog_Control")
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
    mmCreatedControllerList.append(mmTempCreatedController)

    #Now create an enum on each control so we can add fake things onto it later if we want.
    for mmControl in mmCreatedControllerList:

        cmds.select( mmControl )
        cmds.addAttr( longName="ExtraVis", attributeType='enum', en = "None:", dv=0, k = 1 )

    cmds.select( cl = 1)

'''
#Need to create a basic 'plop down' of the quadruped spline locators needed, then have the user set them up.
#   Controls should be scaled larger than the model when finished, and then can be adjusted as desired.
'''
def mmCreateQuadrupedSpinePrimer( *args ):

    #Grab information from UI
    mmGroupValue = cmds.intField("mmCreateSpineGroupValue", q = 1, v = 1)

    #Place these controls approximately where they should be
    #Find bounding box values of all meshes in the scene
    mmAllMeshesInScene = mmSAP.main(["mesh"])

    mmBoundingBoxInfo = mmRF.mmGrabBoundingBoxInfo(mmAllMeshesInScene)
    #mmGrabBoundingBoxInfo returns mmDictOfBoundingBoxLists with this information:
    # [
    #     "min":       [X, Y, Z],
    #     "midPoint":  [X, Y, Z],
    #     "max":       [X, Y, Z],
    #     "total":     [X, Y, Z],
    #     "pivot":       [X, Y, Z]
    # ]

    cmds.select(cl = 1)

    '''
    #Demo for creation:
    #createTextBox( mmTextToAdd = "bob", mmObjectToScaleTo = None, mmRotationalOffset = [0,0,0], mmScaleValue = [1,1,1], mmTextScaleValue = [1,1,1], mmShapeName = "box" )
    #createTextBox( "bob", None, [0,0,0], [1,1,1], [1,1,1], "box" )
    # Possible Shapes:
        # box
        # belt
        # hand
        # foot
        # moveall
        # cog
        # left
        # right
        # pin
        # orb
        # fitall
    '''

    #Create a Chest and Pelvis Control, and color them green  
    mmChestIcon = mmOF.createTextBox("CHEST", None, [90,0,0], [20,20,5], [1,2,0.5], "box" )
    mmOF.changeColor( 14 )
    cmds.move( mmBoundingBoxInfo["midPoint"][0], mmBoundingBoxInfo["midPoint"][1], mmBoundingBoxInfo["midPoint"][2] + (mmBoundingBoxInfo["max"][2] - mmBoundingBoxInfo["midPoint"][2])/3 )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
    mmChestIcon = cmds.rename( mmChestIcon, "chest_Control")

    cmds.parent(mmChestIcon, "cog_Control")

    #Grab desired controller & apply tag
    #?  Leave this for the user to do later
    # mmCreateTagOnObject( mmChestIcon, "identifier_set_" + str(mmGroupValue) + "_startControl_#" )

    cmds.select(cl = 1)

    mmPelvisIcon = mmOF.createTextBox("PELVIS", None, [90,0,0], [20,20,5], [1,2,0.5], "box" )
    mmOF.changeColor( 14 )
    cmds.move( mmBoundingBoxInfo["midPoint"][0], mmBoundingBoxInfo["midPoint"][1], mmBoundingBoxInfo["midPoint"][2] - (mmBoundingBoxInfo["max"][2] - mmBoundingBoxInfo["midPoint"][2])/3 )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
    mmPelvisIcon = cmds.rename( mmPelvisIcon, "pelvis_Control")

    cmds.parent(mmPelvisIcon, "cog_Control")

    #Grab desired controller & apply tag
    #?  Leave this for the user to do later
    # mmCreateTagOnObject( mmPelvisIcon, "identifier_set_" + str(mmGroupValue) + "_endControl_#" )

    cmds.select(cl = 1)

'''
#Need to "tag" the start/mid/end (for both objects and controls) for later so we will know how to hook up things with the functionality we are creating in the spine creator.
'''
def mmTagStartObject( *args ):
    
    #Grab information from UI
    mmGroupValue = cmds.intField("mmCreateSpineGroupValue", q = 1, v = 1)

    #Grab desired controller
    mmControllerName = cmds.ls(sl = 1)[0]

    mmCreateTagOnObject( mmControllerName, "identifier_spine_set_" + str(mmGroupValue) + "_start_#" )

    return None

def mmTagMidObject( *args ):

    mmGroupValue = cmds.intField("mmCreateSpineGroupValue", q = 1, v = 1)

    #Grab desired controller
    mmControllerName = cmds.ls(sl = 1)[0]

    mmCreateTagOnObject( mmControllerName, "identifier_spine_set_" + str(mmGroupValue) + "_mid_#" )

    return None

def mmTagEndObject( *args ):

    mmGroupValue = cmds.intField("mmCreateSpineGroupValue", q = 1, v = 1)

    #Grab desired controller
    mmControllerName = cmds.ls(sl = 1)[0]

    mmCreateTagOnObject( mmControllerName, "identifier_spine_set_" + str(mmGroupValue) + "_end_#" )

    return None

def mmTagStartControl( *args ):
    
    #Grab information from UI
    mmGroupValue = cmds.intField("mmCreateSpineGroupValue", q = 1, v = 1)

    #Grab desired controller
    mmControllerName = cmds.ls(sl = 1)[0]

    mmCreateTagOnObject( mmControllerName, "identifier_spine_set_" + str(mmGroupValue) + "_startControl_#" )

    return None

def mmTagMidControl( *args ):

    mmGroupValue = cmds.intField("mmCreateSpineGroupValue", q = 1, v = 1)

    #Grab desired controller
    mmControllerName = cmds.ls(sl = 1)[0]

    mmCreateTagOnObject( mmControllerName, "identifier_spine_set_" + str(mmGroupValue) + "_midControl_#" )

    return None

def mmTagEndControl( *args ):

    mmGroupValue = cmds.intField("mmCreateSpineGroupValue", q = 1, v = 1)

    #Grab desired controller
    mmControllerName = cmds.ls(sl = 1)[0]

    mmCreateTagOnObject( mmControllerName, "identifier_spine_set_" + str(mmGroupValue) + "_endControl_#" )

    return None

def mmCreateTagOnObject( mmObjectToTag = None, mmStringToTag = "trash", *args ):

    if ( mmObjectToTag == None or mmStringToTag == "trash" ):
        print "mmCreateTagOnObject not provided with an object or string to tag."
        return None
    
    #Create an empty group with an identifier name
    mmGroupIdentifier = cmds.group(em = 1, n = mmStringToTag)

    cmds.parent( mmGroupIdentifier, mmObjectToTag )

    cmds.select( mmGroupIdentifier )

    return mmGroupIdentifier

'''
This Function takes two inputs (a name of an object in a scene, and a shape of Nurbs controller to create),
creates the Nurb controller, renames it to the name of the object (-"loc" +"control"), moves it to the same location
as the object, and returns the name of the object when finished.
'''
def mmCreateController( mmObjectName, mmShapeName ):

    #Grab the first four letters of the name for checking purposes
    mmTempSideChecker = mmObjectName[0:4]

    #Create proper name for controller
    mmWorkingName = mmObjectName.split("_")

    mmCurrentChildren = ""
    
    if ( mmObjectName == "fingers" ):
        mmCreatedController = mmCreateFingerControllers( mmShapeName )
        return mmCreatedController
        
    if ( mmShapeName == "fitall" and mmTempSideChecker != "head" ):

        mmCreatedController = mmOF.createFitAll(mmObjectName, 1.1)

        cmds.select( mmCreatedController )

        if ( mmTempSideChecker == "left" or mmTempSideChecker == "offH" ):
            mmOF.changeColor( 6 )    
        elif ( mmTempSideChecker == "righ" or mmTempSideChecker == "main"  ):
            mmOF.changeColor( 13 )
        else:
            mmOF.changeColor( 14 )
        
        #Rename controller
        mmCreatedController = cmds.rename( mmCreatedController, mmWorkingName[0] + "_Control" )

        cmds.select( cl = 1 )
               
        return mmCreatedController

    #Determine which shape the user wants and create that icon
    if ( mmObjectName != "leftClavicle_Locator" and mmObjectName != "rightClavicle_Locator" ):
    
        cmds.select(mmWorkingName[0])

    mmCreatedController = mmOF.mmCreateDesiredNurbsIcon ( mmShapeName )
    
    #select created controller
    cmds.select( mmCreatedController, r =1 )
    
    
    #Flip the Nurbs image if it is Left or Right sided

    if ( mmShapeName == "foot" ):
        mmTempRotateY = -25
        if ( mmTempSideChecker == "left" ):
            cmds.scale( -1,1,1 )
            
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
            mmTempRotateY = 25
        
        cmds.select( cl = 1 )
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        #print "mmCurrentChildren", mmCurrentChildren
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        cmds.scale( 1.5, 1.5, 1.5 )
        cmds.rotate ( 0, mmTempRotateY, 0 )
        cmds.move( 0, -3, 0, r = 1 )
          
    if ( mmShapeName == "hand" and mmTempSideChecker == "left" ):
        cmds.scale(-1,1,1)
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
        cmds.rotate(90,90,0)

        cmds.select( cl = 1 )
        
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )
        cmds.move( 4, -3, 1, r = 1 )
        
    elif ( mmShapeName == "hand" and mmTempSideChecker == "righ" ):
        cmds.rotate(90,-90,0)
        
        cmds.select( cl = 1 )
        
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )
        cmds.move( -4, -3, 1, r = 1 )
              
    if ( mmShapeName == "box" and mmTempSideChecker == "main" or mmTempSideChecker == "offH" ):
        
        cmds.select( cl = 1 )
        
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )
        cmds.scale( 3, 3, 10, r = 1 )
        
        
    if ( mmTempSideChecker == "head" and mmShapeName == "fitall" ):
        
        cmds.select( cl = 1 )
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        #mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        #cmds.scale( 20, 15, 15, r = 1 )
        #cmds.move( 0, 8, 0, r = 1 )

    if ( mmShapeName == "belt" ):
        
        cmds.select( cl = 1 )
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        cmds.move( 0, 0, -0.5, r = 1 )
        cmds.scale( 0.6465, 0.75, 0.75, r = 1 )
        
    if ( mmShapeName == "cog" ):
        
        cmds.select( cl = 1 )
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        #cmds.move( 0, 0, -0.5, r = 1 )
        cmds.scale( 0.25, 0.25, 0.25, r = 1 )
        
    if ( mmTempSideChecker == "tors"  ):
        
        cmds.select( cl = 1 )
                
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        cmds.scale( 8.75, 8.75, 8.75, r = 1 )
        cmds.move( 0, 4, 0, r = 1 )
        
    if ( mmObjectName == "leftArm_loc" or mmObjectName == "rightArm_loc" ):
        
        cmds.select( cl = 1 )
                
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        cmds.scale( 5, 5, 6, r = 1 )
        
    if ( mmObjectName == "leftShoulder_loc" or mmObjectName == "rightShoulder_loc" ):
        
        cmds.select( cl = 1 )
                
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        cmds.scale( 2.5, 3.3, 5.5, r = 1 )
        
    if ( mmObjectName == "leftClavicle_Locator" or mmObjectName == "rightClavicle_Locator" ):
        
        cmds.select( cl = 1 )
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        cmds.scale( 0.75, 0.75, 8, r = 1 )
        
        if ( mmTempSideChecker == "left" ):
            cmds.move( 2, 2, 0, r = 1 )
        else:
            cmds.move( -2, 2, 0, r = 1 )
                    
    if ( mmShapeName == "moveall" and mmObjectName == "root_loc" ):
        
        cmds.select( cl = 1 )
        
        #Grab desired icon's sub elements, convert to their .cvs and modify them
        #mmCurrentChildren = mmSelectCVChildren( mmCreatedController )

        #cmds.scale( 0.75, 0.75, 8, r = 1 )
    
    cmds.select( cl = 1 )
    
    cmds.select( mmCreatedController )
    
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
         
    #Move created controller to object
    mmTempParentConst = cmds.parentConstraint( mmObjectName, mmCreatedController, w=1.0, mo=0  )
    cmds.delete( mmTempParentConst )
    
    #Clear rotations - this is trash from 3dsmax
    cmds.rotate( 0,0,0 )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
    
    #Create proper name for controller
    mmWorkingName = mmObjectName.split("_")
    
    #Rename controller
    mmCreatedController = cmds.rename( mmCreatedController, mmWorkingName[0] + "_Control" )

    if ( mmTempSideChecker == "head" and mmShapeName == "moveall" ):

        #Create a 'lookAt' control

        #Automatic determination of trans and scale:
        cmds.select( mmCreatedController )

        # cmds.refresh()
        # time.sleep(1)

        #Find bounding box values
        mmBoundingBoxList = cmds.xform( q = 1, boundingBox = 1, ws = 1 )
     
        mmXMin = mmBoundingBoxList[0]
        mmYMin = mmBoundingBoxList[1]
        mmZMin = mmBoundingBoxList[2]
        mmXMax = mmBoundingBoxList[3]
        mmYMax = mmBoundingBoxList[4]
        mmZMax = mmBoundingBoxList[5]

        #Find size user wants
        #Find total size
        mmXTotal = abs(mmXMax - mmXMin)
        mmYTotal = abs(mmYMax - mmYMin)
        mmZTotal = abs(mmZMax - mmZMin)

        cmds.select( mmWorkingName[0] )

        #Find bounding box values
        mmBoundingBoxList = cmds.xform( q = 1, boundingBox = 1, ws = 1 )
     
        mmXMinMesh = mmBoundingBoxList[0]
        mmYMinMesh = mmBoundingBoxList[1]
        mmZMinMesh = mmBoundingBoxList[2]
        mmXMaxMesh = mmBoundingBoxList[3]
        mmYMaxMesh = mmBoundingBoxList[4]
        mmZMaxMesh = mmBoundingBoxList[5]

        #Find halfway point (i.e. center of object) and how far to move controller to be in the right place
        mmXTotalMesh = abs(mmXMaxMesh - mmXMinMesh)
        mmYTotalMesh = abs(mmYMaxMesh - mmYMinMesh)
        mmZTotalMesh = abs(mmZMaxMesh - mmZMinMesh)

        #Find pivot values
        mmPivotList = cmds.xform( q = 1, pivots = 1, ws = 1 )
     
        mmXPiv = mmPivotList[0]
        mmYPiv = mmPivotList[1]
        mmZPiv = mmPivotList[2]

        mmXMidPoint = mmXMaxMesh - mmXTotalMesh/2
        mmYMidPoint = mmYMaxMesh - mmYTotalMesh/2
        mmZMidPoint = mmZMaxMesh - mmZTotalMesh/2
        mmYToMove = mmYMidPoint - mmYPiv

        # print "mmZMinMesh", mmZMinMesh
        # print "mmZMaxMesh", mmZMaxMesh
        # print "mmZPiv", mmZPiv

        mmZtoMove = (mmZMaxMesh - mmZPiv)*1.1

        #Find size user wants
        #Find total size
        mmXTotalMesh = abs(mmXMaxMesh - mmXMinMesh)
        mmYTotalMesh = abs(mmYMaxMesh - mmYMinMesh)
        mmZTotalMesh = abs(mmZMaxMesh - mmZMinMesh)

        
        #Make sure we aren't going to be dividing by zero
        if ( mmXTotal < 0.00001 ):
            mmXTotalComparison = 1
        else:
            mmXTotalComparison = mmXTotalMesh / mmXTotal

        if ( mmYTotal < 0.00001 ):
            mmYTotalComparison = 1
        else:
            mmYTotalComparison = mmYTotalMesh / mmYTotal

        if ( mmZTotal < 0.00001 ):
            mmXTotalComparison = 1
        else:
            mmZTotalComparison = mmZTotalMesh / mmZTotal

        cmds.select( mmCreatedController )

        #This determines the look at trans and scale manually - can we do it automatically?
        cmds.xform( t = (0, 0, mmZtoMove), r = 1 )
        cmds.rotate( -90, 0, 0, r = 1 )
        cmds.scale( mmXTotalComparison, mmYTotalComparison, mmZTotalComparison, r = 1 )

        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

        mmCurrentChildren = mmSelectCVChildren( mmCreatedController )
        cmds.move( 0, mmYToMove, 0, r = 1 )

        cmds.select(cl = 1)

        #Rename controller
        mmCreatedController = cmds.rename( mmCreatedController, "lookAt" + "_Control" )

        ####################
        
        #Revmoving this controller and changing the way the head works
        #Also create a few box icons and merge them to create a separate rotator (to be under our aim node)
        mmBoxList = ['', '', '']
        mmBoxList[0] = cmds.duplicate("head_Control")
        mmBoxList[1] = cmds.duplicate("head_Control")
        mmBoxList[2] = cmds.duplicate("head_Control")

        i = 0
        for mmBox in mmBoxList:

            if (i == 0):

                mmCurrentChildren = mmSelectCVChildren( mmBoxList[i] )

                cmds.scale(1.1, 0.1, 0.1, r = 1, p = (mmXMidPoint, mmYMidPoint, mmZMidPoint) )

            elif (i == 1):

                mmCurrentChildren = mmSelectCVChildren( mmBoxList[i] )

                cmds.scale(0.1, 1.1, 0.1, r = 1, p = (mmXMidPoint, mmYMidPoint, mmZMidPoint) )

            elif (i == 2):

                mmCurrentChildren = mmSelectCVChildren( mmBoxList[i] )
                
                cmds.scale(0.1, 0.1, 1.1, r = 1, p = (mmXMidPoint, mmYMidPoint, mmZMidPoint) )

            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

            mmBoxList[i] = cmds.rename( mmBoxList[i], "box" )

            i += 1

        mmHeadExtraShapeGroup = cmds.group(em = 1)

        cmds.select("boxShape", r = True)
        cmds.select("box1Shape", add = True)
        cmds.select("box2Shape", add = True)
        cmds.select(mmHeadExtraShapeGroup, add = True)

        cmds.parent( r = 1, s = 1)

        # cmds.refresh()
        # time.sleep(.5)

        # #Move created controller to object
        # mmTempPointConst = cmds.pointConstraint( mmObjectName, mmHeadExtraShapeGroup, w=1.0, mo=0  )
        # cmds.delete( mmTempPointConst )

        #Need to move only the pivot
        cmds.move( mmXPiv, mmYPiv, mmZPiv, mmHeadExtraShapeGroup+".scalePivot", mmHeadExtraShapeGroup+".rotatePivot", absolute=True)
        
        # cmds.refresh()
        # time.sleep(1)

        #Clear rotations - this is trash from 3dsmax
        cmds.select(mmHeadExtraShapeGroup)
        cmds.rotate( 0,0,0 )
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

        # cmds.refresh()
        # time.sleep(1)

        #Grab Children and move Up
        mmCurrentChildren = mmSelectCVChildren( mmHeadExtraShapeGroup )
        #cmds.move( 0,mmYToMove,0, r = 1 )
        cmds.select(cl = 1)

        mmHeadExtraShapeGroup = cmds.rename( mmHeadExtraShapeGroup, mmWorkingName[0] + "Extra_Control" )

        cmds.select(mmHeadExtraShapeGroup)
        cmds.addAttr( longName="ExtraVis", attributeType='enum', en = "None:", dv=0, k = 1 )        
        cmds.select(cl = 1)

        cmds.select(mmBoxList[0], r = 1)
        cmds.select(mmBoxList[1], add = 1)
        cmds.select(mmBoxList[2], add = 1)
        cmds.delete()

        cmds.select( mmCreatedController, r = 1 )
        cmds.select( mmHeadExtraShapeGroup, add = 1 )


    '''
    mel.eval("curve -d 1 -p -0.413521 -0.0864794 0 -p -0.412917 0 0.0860787 -p -0.413517 0.0858017 -0.000579073 -p -0.413158 0 -0.0864794 -p -0.413521 -0.0864794 0 -k 0 -k 1 -k 2 -k 3 -k 4 ;")
    pinPiece3 = cmds.rename("pin_pieceC")
    pinGroup = cmds.group(em=1)
    cmds.select( (pinPiece1+"Shape"), r=True )
    cmds.select( (pinPiece2+"Shape"), add=True )
    cmds.select( (pinPiece3+"Shape"), add=True )
    cmds.select( pinGroup, add=True )
    cmds.parent( r = 1, s = 1)
    '''

    #Set root controller's values back to world trans
    if ( mmObjectName == "root_loc" ):
        cmds.select( mmCreatedController )
        mmGWT.main()

    
    #Not working, something else is causing there to be transation information
    if ( mmObjectName == "bodyPosition_loc" ):

        cmds.select( mmCreatedController )

        mmTrashTrans = cmds.getAttr( mmCreatedController + ".translate" )

        #print "mmTrashTrans before GWT", mmTrashTrans
        '''
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

        mmTrashTrans = cmds.getAttr( mmCreatedController + ".translate" )

        print "mmTrashTrans After GWT", mmTrashTrans
        '''
        
    
    if ( mmTempSideChecker == "left" or mmTempSideChecker == "offH" ):
        mmOF.changeColor( 6 )    
    elif ( mmTempSideChecker == "righ" or mmTempSideChecker == "main" ):
        mmOF.changeColor( 13 )
    else:
        mmOF.changeColor( 14 )
    
    
    return mmCreatedController

'''
This Function takes a passed object, selects its .cv components, and returns a list of those components.
#?  This should move to mmOF
'''
def mmSelectCVChildren( mmDesiredNurbsObject ):
    #Grab foot icon's sub elements and convert to their .cvs and modify them
    mmCurrentChildren = cmds.listRelatives( mmDesiredNurbsObject, s=True, c=True )
    cmds.select( cl = 1  )

    for mmShapeNode in mmCurrentChildren:
        
        mmTempListOfShapeNodes = cmds.select( mmShapeNode+'.cv[*]', add = 1 )

    return mmTempListOfShapeNodes

'''
This Function takes two inputs (a name of an object in a scene, and a shape of Nurbs controller to create),
creates the Nurb controller, renames it to the name of the object (-"loc" +"control"), moves it to the same location
as the object, and returns the name of the object when finished.
'''
def mmCreateFingerControllers( mmShapeName ):
    
    mmAllFingersInScene = []
    mmAllThumbsInScene = []
    
    
    #Identify how many fingers/thumbs there are - or should this be passed to the function?
    #Do it here for now
    #Search all meshes in the scene for "leftFinger" as the starting name, and "rightFinger" as the starting name.
    #Save those meshes out in a list of finger locators and a separate list for thumb locators
    mmAllLocatorsInScene = mmSAP.main(["locator"])
    
    for mmLocator in mmAllLocatorsInScene:
        if ( mmLocator[0:10] == "leftFinger" or mmLocator[0:11] == "rightFinger" ):
            mmAllFingersInScene.append(mmLocator)
        elif ( mmLocator[0:9] == "leftThumb" or mmLocator[0:10] == "rightThumb" ):
            mmAllThumbsInScene.append(mmLocator)
            
    #Combine two lists so we don't have to run through this twice
    mmAllDesired = list(mmAllFingersInScene)
    mmAllDesired = mmAllDesired + mmAllThumbsInScene
    
    
    mmNumOfFingers = len(mmAllFingersInScene)
    
    mmCounter = 0
    
    for mmLocator in mmAllDesired:
            
        #Determine which shape the user wants and create that icon
        mmCreatedController = mmOF.mmCreateDesiredNurbsIcon ( mmShapeName )
    
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
        
        #Move created controller to object
        mmTempParentConst = cmds.parentConstraint( mmLocator, mmCreatedController, w=1.0, mo=0  )
        cmds.delete( mmTempParentConst )
        
        #Clear rotations - this is trash from 3dsmax
        cmds.rotate( 0,0,0 )
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
        
        #Rotate pin for finger or thumb
        if ( mmCounter < mmNumOfFingers ):
            cmds.rotate( 0,0,90 )
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
            cmds.scale( 0.5,1,1 )
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
        else:
            cmds.rotate( 90,0,0 )
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
            cmds.scale( 1,1,0.5 )
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
        
        #Create proper name for controller
        mmWorkingName = mmLocator.split("_")
        
        #Rename controller
        mmCreatedController = cmds.rename( mmCreatedController, mmWorkingName[0] + "_Control" )
    
        
        #Grab the first four letters of the name for checking purposes
        mmTempSideChecker = mmLocator[0:4]
        
        #Set the color of the Nurbs Curve as desired
        if ( mmTempSideChecker == "left" or mmTempSideChecker == "offH" ):
            mmOF.changeColor( 6 )    
        elif ( mmTempSideChecker == "righ" or mmTempSideChecker == "main"  ):
            mmOF.changeColor( 13 )
        else:
            mmOF.changeColor( 14 )
        
        mmCounter += 1
    
    return mmCreatedController

'''
This Function grabs all controls which were made before (assumed to be there), parents them properly, and
    parentConstrains the "_loc"s to the proper places
'''
def mmConnectTheRigControlsUp( *args ):

    global mmGroup_Controls

    mmGroup_Controls = "_Group_Controls"

    #---------------------------------------------

    #Select all locators in the scene

    mmSelectionList = cmds.ls( type = "transform" )

    #---------------------------------------------
    
    #Find the parents of all the "_loc" locators and store them.
    
    #mmLocatorStoreArray will hold on to each newly created Locator Bone and its Parent bone to be (if it has one),
    #     replacing the suffix with _Control so we grab the controls
    mmControllerStoreArray = []
    mmLocatorStoreArray = []

    mmCounterA = 0
    mmClavicleBool = False
    mmLookAtName = None
    mmHeadExtraName = None

    for objectName in mmSelectionList:

        mmTempNameChecker = objectName.split("_")

        if( len( mmTempNameChecker ) > 1 and mmTempNameChecker[1] == "loc" ):

            #Each loc found is given an array to store its name and its parent
            # Also are saving a version of the loc object as _Control
            mmControlStoreArray = []
            mmOriginalLocStoreArray = []

            mmControllerName = mmTempNameChecker[0] + "_Control"

            #Store the name of the bone into the two arrays
            mmControlStoreArray.append( mmControllerName )
            mmOriginalLocStoreArray.append( objectName )
            
            objectParent = cmds.listRelatives( objectName, p = 1 )
            
            #If there is a parent of the current bone, store it here.
            if ( objectParent != None and objectParent[0] == "_Group_ExportLocators" ):
                mmParentName = "_Group_Controls"

            elif ( objectParent != None and objectParent[0] != "_Group_ExportLocators" ):

                mmParentName = objectParent[0].split("_")

                mmParentName = mmParentName[0] + "_Control"

            else:
                mmParentName = "None"
            
            mmControlStoreArray.append( mmParentName )
            mmOriginalLocStoreArray.append( mmParentName )

            mmControllerStoreArray.append( mmControlStoreArray )
            mmLocatorStoreArray.append( mmOriginalLocStoreArray )

        #Check for various names, and if found, do some action later
        if( len( mmTempNameChecker ) > 1 and mmTempNameChecker[0] == "leftClavicle" ):
            mmClavicleBool = True
        elif( len( mmTempNameChecker ) > 1 and mmTempNameChecker[0] == "lookAt" ):
            mmLookAtName = objectName
        elif( len( mmTempNameChecker ) > 1 and mmTempNameChecker[0] == "headExtra" ):
            mmHeadExtraName = objectName


        mmCounterA += 1
    
    #Grab each control and parent it to the proper parent
    # Must be a separate for loop because we are not sure when each bone is created.
    for mmControl in mmControllerStoreArray:
        if ( mmControl[1] != "None" and mmControl[1] != None ):

            #Run Parenting
            mmParent = cmds.listRelatives(mmControl[0], p = 1)

            if type(mmParent) == type([""]) :
                mmParent = mmParent[0]
            if mmParent != mmControl[1] :
                cmds.parent( mmControl[0], mmControl[1] )
            
            #If this is not the root, then I want the trans to be zeroed out, so just freeze trans
            if ( mmControl[0] != "root_Control" ):
                # print "mmControl[0]", mmControl[0]
                cmds.select(mmControl[0], r = 1)
                cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    #After all the iterations are done (and we know the parenting is complete), then check for clavicles again and parent in if its found.
    #     Assuming this is specifically a human rig because the clavicle is specifically designed for that.
    if ( mmClavicleBool ): 
        cmds.parent( "leftClavicle_Control", "torso_Control" )
        cmds.parent( "leftShoulder_Control", "leftClavicle_Control" )

        cmds.parent( "rightClavicle_Control", "torso_Control" )
        cmds.parent( "rightShoulder_Control", "rightClavicle_Control" )

        #Freeze Transforms after parenting
        cmds.select( "rightClavicle_Control", r = 1 )
        cmds.select( "leftClavicle_Control", add = 1 )
        cmds.select( "rightShoulder_Control", add = 1 )
        cmds.select( "leftShoulder_Control", add = 1 )
        
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    if ( mmLookAtName != None ):
        cmds.parent( mmLookAtName, "root_Control" )
        cmds.select( mmLookAtName, r = 1)
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    if ( mmHeadExtraName != None ):

        # bob = cmds.getAttr( "headExtra_Control.translate")
        # print "headExtra_Control.translate 2", bob

        cmds.parent( mmHeadExtraName, "head_Control" )

        cmds.select( mmHeadExtraName, r = 1)
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)


        # bob = cmds.getAttr( "headExtra_Control.translate")
        # print "headExtra_Control.translate 3", bob

        #Also need to check - any other children of "head_Control" (but not shape nodes) should instead be parented to mmHeadExtraName
        mmChildrenOfHeadControl = cmds.listRelatives("head_Control", c = 1)
        for mmChild in mmChildrenOfHeadControl:
            
            if (mmChild != "head_ControlShape" and mmChild != mmHeadExtraName ):
                cmds.parent( mmChild, mmHeadExtraName )

                cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    #Go through and parentconstrain all the locators to the controls
    #First sort the two lists so they are the same
    mmLocatorStoreArray.sort()
    mmControllerStoreArray.sort()

    # print "mmLocatorStoreArray", mmLocatorStoreArray
    # print "mmControllerStoreArray", mmControllerStoreArray

    mmMaxCounter = len( mmControllerStoreArray )

    mmCounter = 0
    while mmCounter < mmMaxCounter:
        cmds.parentConstraint( mmControllerStoreArray[mmCounter][0], mmLocatorStoreArray[mmCounter][0], mo = True )
        mmCounter += 1

    cmds.select(cl = 1)

    #cmds.parent( mmRootController, mmGroup_Controls )

'''
This Function takes one input of two points (and possibly more later), and then creates the required controls for a "stretchy spine".
    Really just two locators that point at each other atm.
'''
def mmCreateSpineRig( *args ):

    #Verify that groups are created
    mmCreateRigGroups()

    '''
    #Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''

    #Create a group to put all the spine objects into
    mmSpineGroup = cmds.group( em = True, n = "_Group_Spine" )

    #Put locators created under mmSpineGroup and put that under mmGroup_Hidden
    cmds.parent( mmSpineGroup, mmGroup_Hidden )

    mmIdentifierList = []

    mmPointActualControl = {}
    mmPointIdentifier = {}
    mmPointChildObject = {}
    mmPointControlIdentifier = {}
    #{ 0 : mmPointActualControl, 1 : mmPointIdentifier, 2: mmPointChildObject }

    mmOverallListOfCreatedLocators = []

    mmPointSet = { 0:{}, 1:{} }
    mmPointSetDict = {}
    #mmPointSetDict = collections.defaultdict(lambda: collections.defaultdict(lambda: {}))
    
    #Create a list of objects to be hidden later since they aren't needed
    mmObjectsToHideList = []

    mmMidPointDict = {}

    #Grab all tranforms in scene
    mmAllTransformsInScene = cmds.ls(type = "transform")

    #Grab all identifiers that the user wants
    
    #Find the "identifier" tags if they exist (may not)
    for mmTransform in mmAllTransformsInScene:
        mmSplitWordsFound = mmTransform.split("_")
        if (len(mmSplitWordsFound) > 1 and mmSplitWordsFound[0] == "identifier" and mmSplitWordsFound[1] == "spine"):

            mmIdentifierList.append(mmTransform)

    for mmTransform in mmIdentifierList:
        mmSplitWordsFound = mmTransform.split("_")
        
        #First verify that we are working with the right group.  Save out everything to this specific group's information.
        mmSetNumber = int(mmSplitWordsFound[3])

        if mmSetNumber in mmPointSetDict :
            mmPointSet = mmPointSetDict[mmSetNumber]
        else:
            mmPointSet = { 0:{}, 1:{} }

        #-------------------------------------------------------------------------------

        #Find the actual Point1 control (leave this open for mid-belly pieces)
        if ( mmSplitWordsFound[4] == "startControl" ):

            #Grab parent
            mmPointSet[0][0] = cmds.listRelatives(mmTransform, p = 1)[0]

            cmds.delete(mmTransform)

            cmds.select(mmPointSet[0][0])
            #Freeze Transforms - because the user most likely moved it
            cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

        if ( mmSplitWordsFound[4] == "endControl" ):

            #Grab parent
            mmPointSet[0][1] = cmds.listRelatives(mmTransform, p = 1)[0]

            cmds.delete(mmTransform)

            cmds.select(mmPointSet[0][1])
            #Freeze Transforms - because the user most likely moved it
            cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

        ############################################
        #Grabbing the mid point controls if they exist, but not doing anything with them currently
        #?   Not 100% sure that "1+mmSplitWordsFound[5]" is correct, check if we ever start to use this.
        ############################################
        if ( mmSplitWordsFound[4] == "midControl" ):

            #Grab parent
            mmPointSet[0][1+mmSplitWordsFound[5]] = cmds.listRelatives(mmTransform, p = 1)[0]

            cmds.delete(mmTransform)

            cmds.select(mmPointSet[0][1+mmSplitWordsFound[5]])
            #Freeze Transforms - because the user most likely moved it
            cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

        #-------------------------------------------------------------------------------

        #-------------------------------------------------------------------------------

        #Find the Point1 and Point2 child controls (leave this open for mid-belly pieces)
        if ( mmSplitWordsFound[4] == "start" ):
            #Grab parent
            mmPointSet[1][0] = cmds.listRelatives(mmTransform, p = 1)[0]

            cmds.delete(mmTransform)

        if ( mmSplitWordsFound[4] == "end" ):

            #Grab parent
            mmPointSet[1][1] = cmds.listRelatives(mmTransform, p = 1)[0]

            cmds.delete(mmTransform)

        ############################################
        #Grabbing the mid points if they exist, but not doing anything with them currently
        #?   Not 100% sure that "1+mmSplitWordsFound[5]" is correct, check if we ever start to use this.
        ############################################
        if ( mmSplitWordsFound[4] == "mid" ):
            #Grab parent
            mmPointSet[1][1+mmSplitWordsFound[5]] = cmds.listRelatives(mmTransform, p = 1)[0]

            cmds.delete(mmTransform)

        #-------------------------------------------------------------------------------

        mmPointSetDict[mmSetNumber] = mmPointSet

    #Adding a for loop for iterating this for each spine set which we are creating.
    for mmKey, mmPointSet in mmPointSetDict.items():

        mmPointActualControl = mmPointSet[0]
        mmPointChildObject = mmPointSet[1]

        #Need to find if our children are meshes.
        #   If they are, need to convert the mmPointActualControl into the mmPointChildObject, then duplicate the mmPointActualControl and make that the parent.
        for mmSubKey, mmChildObject in mmPointChildObject.items():
            # print "mmSubKey, mmChildObject:", mmSubKey, ",", mmChildObject

            #Check to see if our transform is a mesh, if it is, create a new control, inject it into the hierarchy above the mesh's control,
            #   and swap in the proper elements for child control and actual control.
            mmChildrenOfTransform = cmds.listRelatives( mmChildObject, c = 1 )
            # print "mmChildrenOfTransform", mmChildrenOfTransform

            for mmChildLarge in mmChildrenOfTransform:

                if ( cmds.objectType(mmChildLarge) == "mesh" ):

                    mmOriginalName = mmPointActualControl[mmSubKey]
                    #If the child of this object is a mesh shape, then we want to do this instead:
                    #need to convert the mmPointActualControl into the mmPointChildObject
                    mmPointChildObject[mmSubKey] = mmPointActualControl[mmSubKey]
                    #Duplicate the mmPointActualControl, scale up by 1.1, and make that the parent of the original
                    #mmPointActualControl[mmSubKey] = cmds.duplicate( mmPointActualControl[mmSubKey] )
                    mmPointActualControl[mmSubKey] = mmOF.createTextBox( mmChildObject, mmChildObject, [90,0,0], [1.2,1.2,0.5], [1,1,1], "box" )

                    '''
                    #Demo for creation:
                    #createTextBox( mmTextToAdd = "bob", mmObjectToScaleTo = None, mmRotationalOffset = [0,0,0], mmScaleValue = [1,1,1], mmTextScaleValue = [1,1,1], mmShapeName = "box" )
                    # Possible Shapes:
                        # box
                        # belt
                        # hand
                        # foot
                        # moveall
                        # cog
                        # left
                        # right
                        # pin
                        # orb
                        # circle
                        # fitall
                    '''

                    cmds.select(mmPointActualControl[mmSubKey])
                    cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

                    mmPointChildObject[mmSubKey] = cmds.rename( mmPointChildObject[mmSubKey], mmOriginalName + "_child" )
                    mmPointActualControl[mmSubKey] = cmds.rename( mmPointActualControl[mmSubKey], mmOriginalName )

                    #Need to grab the original's parent, then parent the original under the new under the original parent
                    mmOriginalParent = cmds.listRelatives( mmPointChildObject[mmSubKey], p = 1 )
                    cmds.parent( mmPointActualControl[mmSubKey], mmOriginalParent )
                    cmds.parent( mmPointChildObject[mmSubKey], mmPointActualControl[mmSubKey] )

                    #Also need to grab any children of the original and parent them under the new
                    mmOriginalChildren = cmds.listRelatives( mmPointChildObject[mmSubKey], c = 1 )
                    # print "mmOriginalChildren", mmOriginalChildren
                    enum = 0
                    for mmChild in mmOriginalChildren:
                        # print "mmChild & type:", mmChild, cmds.objectType(mmChild)

                        if ( cmds.objectType(mmChild) == "transform" ):
                            
                            cmds.parent( mmChild, mmPointActualControl[mmSubKey] )

                            #head control is getting strange offsets - fix here
                            #?  Also need to fix its children
                            # print "setting 0,0,0 for ", mmChild
                            cmds.select(mmChild)
                            cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

                            #Also need to grab any children of the child and ensure they are zero'd out
                            mmRF.mmRecursiveUnparentAndCleanChildrensTransRotScale(mmChild)

                            enum += 1
                        
        #Moving these above the section of code which connects everything because we need to freeze transforms and cannot when there are connections.
        #Need to rig all the current children of the actual object to point constrain at the location they are from their current parent
        mmListOfExceptions = []
        if 0 in mmPointChildObject:
            mmListOfExceptions.append(mmPointChildObject[0])
        if 1 in mmPointChildObject:
            mmListOfExceptions.append(mmPointChildObject[1])
        if 0 in mmPointActualControl:
            mmListOfExceptions.append(mmPointActualControl[0])
        if 1 in mmPointActualControl:
            mmListOfExceptions.append(mmPointActualControl[1])

        mmListOfCreatedLocators = mmRF.mmParentRemovalAndConstrain( mmPointActualControl[0], "root_Control", 3, mmListOfExceptions )

        for mmLocator in mmListOfCreatedLocators:
                mmOverallListOfCreatedLocators.append(mmLocator)

        mmListOfCreatedLocators = mmRF.mmParentRemovalAndConstrain( mmPointActualControl[1], "root_Control", 3, mmListOfExceptions )

        for mmLocator in mmListOfCreatedLocators:
                mmOverallListOfCreatedLocators.append(mmLocator)

        #This section creates the start and endpoints and runs regardless of whether or not we found 'child controllers'.
        if 0 in mmPointChildObject:
            mmStartPointAimer = cmds.spaceLocator( n = "start_aimer_#" )[0]
            mmStartPointFollower = cmds.spaceLocator( n = "start_follower_#" )[0]

            cmds.pointConstraint( mmPointActualControl[0], mmStartPointAimer, mo = 0 )
            cmds.parentConstraint( mmPointActualControl[0], mmStartPointFollower, mo = 0 )

            #Set Aimer for StartPoint to point at EndPoint
            mmStartPointAimConstraint = cmds.aimConstraint( mmPointActualControl[1], mmStartPointAimer, mo = 1, wuo = mmPointActualControl[0], aim = [0,0,-1] )

            #Set orientation of aim constraint to follow the head controller if it gets funky
            cmds.setAttr( mmStartPointAimConstraint[0] + ".worldUpType", 2 )

            #Create a space switcher for StartPoint between between Aimer and Control
            mmStartPointPad = mmOF.mmGroupInPlace( mmPointChildObject[0] )

            #Freeze Transforms - because we have moved it in hierarchy
            cmds.select(mmPointChildObject[0])
            cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

            mmStartPointControlAttr = mmRF.spaceSwitcherMulti( 3, mmPointChildObject[0], [mmStartPointPad], [ mmStartPointAimer, mmStartPointFollower ], True, "aim_to_follow" )

            cmds.parent( mmStartPointAimer, mmSpineGroup )
            cmds.parent( mmStartPointFollower, mmSpineGroup )

            #Need to rig all the current children of the child objects to parent constrain at the location they are from their current parent.
            mmListOfExceptions = []
            if 0 in mmPointChildObject:
                mmListOfExceptions.append(mmPointChildObject[0])
            if 1 in mmPointChildObject:
                mmListOfExceptions.append(mmPointChildObject[1])
            if 0 in mmPointActualControl:
                mmListOfExceptions.append(mmPointActualControl[0])
            if 1 in mmPointActualControl:
                mmListOfExceptions.append(mmPointActualControl[1])
            
            mmListOfCreatedLocators = mmRF.mmParentRemovalAndConstrain(mmPointChildObject[0], "root_Control", 3, mmListOfExceptions )
            for mmLocator in mmListOfCreatedLocators:
                mmOverallListOfCreatedLocators.append(mmLocator)

        if 1 in mmPointChildObject:
            #Set Aimer for EndPoint to point at StartPoint
            mmEndPointAimer = cmds.spaceLocator( n = "end_aimer_#" )[0]
            mmEndPointFollower = cmds.spaceLocator( n = "end_follower_#" )[0]

            cmds.pointConstraint( mmPointActualControl[1], mmEndPointAimer, mo = 0 )
            cmds.parentConstraint( mmPointActualControl[1], mmEndPointFollower, mo = 0 )

            mmEndPointAimConstraint = cmds.aimConstraint( mmPointActualControl[0], mmEndPointAimer, mo = 1, wuo = mmPointActualControl[1], aim = [0,0,1] )
            cmds.aimConstraint( mmPointActualControl[0], q = 1, offset = 1 )

            #Set orientation of aim constraint to follow the head controller if it gets funky
            cmds.setAttr( mmEndPointAimConstraint[0] + ".worldUpType", 2 )

            #Create a space switcher for EndPoint between between Aimer and Control
            mmEndPointPad = mmOF.mmGroupInPlace( mmPointChildObject[1] )

            #Freeze Transforms - because we have moved it in hierarchy
            cmds.select(mmPointChildObject[1])
            cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

            mmEndPointControlAttr = mmRF.spaceSwitcherMulti( 3, mmPointChildObject[1], [mmEndPointPad], [ mmEndPointAimer, mmEndPointFollower ], True, "aim_to_follow" )

            cmds.parent( mmEndPointAimer, mmSpineGroup )
            cmds.parent( mmEndPointFollower, mmSpineGroup )

            #Need to rig all the current children of the child objects to point constrain at the location they are from their current parent
            mmListOfExceptions = []
            if 0 in mmPointChildObject:
                mmListOfExceptions.append(mmPointChildObject[0])
            if 1 in mmPointChildObject:
                mmListOfExceptions.append(mmPointChildObject[1])
            if 0 in mmPointActualControl:
                mmListOfExceptions.append(mmPointActualControl[0])
            if 1 in mmPointActualControl:
                mmListOfExceptions.append(mmPointActualControl[1])
            
            mmListOfCreatedLocators = mmRF.mmParentRemovalAndConstrain(mmPointChildObject[1], "root_Control", 3, mmListOfExceptions )
            for mmLocator in mmListOfCreatedLocators:
                mmOverallListOfCreatedLocators.append(mmLocator)

    #Need to take all created locators, put them in the appropriate place, and hide them if necessary.
    for mmCreatedLocator in mmOverallListOfCreatedLocators:

        cmds.parent( mmCreatedLocator, mmSpineGroup )

    return None

'''
This Function takes one input of the head_loc, and then creates the required controls
#?  NOTE: This function fails if the 'head' is not a child to something before the root (like a torso),
#?      unsure why or how to make it known when this failure happens - but it will be looking for W0 intead of W1.
'''
def mmCreateHeadRig( mmHeadLoc = None ):

    #Verify that groups are created
    mmCreateRigGroups()

    '''
    #Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''

    if mmHeadLoc == None:
        print "mmC3MRTMR.mmCreateHeadRig was not provided the loc it needs."
        return None

    #Find Head Controls
    #   We assume these exist because the function was called
    mmHeadLocList = mmHeadLoc.split("_")

    mmHeadControl = mmHeadLocList[0] + "_Control"

    mmLookAtControl = "lookAt_Control"

    mmHeadExtraControl = "headExtra_Control"

    # Need a group which the head_loc is parented under
    mmHeadLocPad1 = mmOF.mmGroupInPlace( mmHeadLoc, "_pad#" )
    mmHeadLocPad2 = mmOF.mmGroupInPlace( mmHeadLocPad1, "_pad#" )
    
    #Removed the head extra control
    #Pad mmHeadExtraControl
    mmHeadExtraControlPad = mmOF.mmGroupInPlace(mmHeadExtraControl)

    #Constrain pad1 to head extra control
    cmds.parentConstraint( mmHeadExtraControl, mmHeadLocPad1, mo = 1 )

    #Create locator with point constraint putting it on the head, then an aim constraint pointing it at the LookAt
    mmAimerLoc = cmds.spaceLocator( name = mmHeadLoc + "_Aimer#" )[0]
    mmPointConstraint = cmds.pointConstraint( mmHeadControl, mmAimerLoc, mo = 0 )

    mmAimConstraint = cmds.aimConstraint( mmLookAtControl, mmAimerLoc, mo = 1, wuo = mmLookAtControl, aim = [0,0,1]  )
   
    #Set orientation of aim constraint to follow the head controller if it gets funky
    cmds.setAttr( mmAimConstraint[0] + ".worldUpType", 2 )

    #Group mmLookAtControl
    mmLookAtPad = mmOF.mmGroupInPlace( mmLookAtControl )

    #That group needs to space switch between the lookAt and regular rotation on the Head_Control with sdks
    #Select what is required to run the script
    cmds.select(cl = 1)

    #Need to parent in the head so it moves appropriately
    cmds.select( mmHeadLoc )
    mmRelativeList = cmds.listRelatives(  )

    #First find old parentconstraint and delete it
    for mmRelative in mmRelativeList:
        mmRelativeChecker = mmRelative.split("_")

        for mmRelativeName in mmRelativeChecker:
            
            if ( mmRelativeName[0:6] == "parent" ):
                cmds.select( mmRelative )
                cmds.delete()

    mmRF.spaceSwitcherMulti( 3, mmHeadExtraControl, [mmHeadExtraControlPad], [mmHeadControl, mmAimerLoc], True, "space_switch" )

    #Create a second space switcher for the head to orient according to its parent or world
    #   Must replace its current connection with a point constraint.

    mmHeadControlsParent = cmds.listRelatives(mmHeadControl, p = 1)[0]

    if (mmHeadControlsParent != "root_Control") :
 
        mmHeadControlPad = mmOF.mmGroupInPlace( mmHeadControl )

        mmRF.spaceSwitcherMulti( 2, mmHeadControl, [mmHeadControlPad], [mmHeadControlsParent, "root_Control"], True, "space_switch" )

        cmds.pointConstraint(mmHeadControlsParent, mmHeadControlPad, mo = 1)

    #Organization
    cmds.parent( mmAimerLoc, mmGroup_Hidden )

#####################################################################
"""
# '''
# This Function takes the input of two locators for a foot that already exists.
# After creating the forward and reverse foot systems, the bone which was created on top of the parent node is returned.
# This function was working, but wanted to have the revfoot rig work for general rigs (not just human), so made the next to scripts below this that separate the feet out.
# '''
def mmCreateRevFootRig( mmLeftFootLoc, mmRightFootLoc ):

    #Verify that groups are created
    mmCreateRigGroups()

    '''
    #Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''
    
    #Need to Organize!
    #Create groups to store stuff away
    mmGroup_Foot_Hidden = cmds.group( em = True, n = "_Group_Foot_Hidden" )
    mmGroup_Foot_MainBone = cmds.group( em = True, n = "_Group_Foot_MainBones" )
    mmGroup_Foot_BuildLocator = cmds.group( em = True, n = "_Group_Foot_BuildLocators" )

    cmds.select(cl= 1)
    
    cmds.parent( mmGroup_Foot_Hidden, mmGroup_Hidden )
    cmds.parent( mmGroup_Foot_MainBone, mmGroup_MainBones )
    cmds.parent( mmGroup_Foot_BuildLocator, mmGroup_BuildLocator )

    mmBonesOnParent = []
    
    mmRightFoot_Control = mmRightFootLoc.split("_")[0] + "_Control"
    mmLeftFoot_Control = mmLeftFootLoc.split("_")[0] + "_Control"
    mmRightFootLoc = mmRightFootLoc
    mmLeftFootLoc = mmLeftFootLoc

    mmToeConfirmBool = False
    mmLeftToeLoc = ""
    mmRightToeLoc = ""
    

    ''' Assume left and right feet are ready for Reverse Foot Rig, create and connect '''
    
    #First select all rev foot locators (for both feet)
    #And store them into the appropriate ordered list location - can't sort by the number exactly because we don't know what order they are selected in.
    mmLeftFootLocators = ["","","","","","","",""]
    mmRightFootLocators = ["","","","","","","",""]
    mmLeftFootNamers = ["","","","","","","",""]
    mmRightFootNamers = ["","","","","","","",""]
    mmLocatorShapesInScene = cmds.ls( type = ("locator") )
    
    #Find the parent (which should always be the transforms)
    mmLocatorsInScene = cmds.listRelatives(mmLocatorShapesInScene, parent=True, fullPath=0)
    
    for mmLocator in mmLocatorsInScene:

        mmListOfLocName = mmLocator.split("_")
        mmListOfLocNameLen = len(mmListOfLocName)

        if (mmListOfLocNameLen > 4):
            mmTempNumber = mmListOfLocName[len(mmListOfLocName)-4]

            # print "mmListOfLocName", mmListOfLocName

            if (mmListOfLocName[0] == "left" and mmListOfLocName[1] == "Foot" and mmListOfLocName[len(mmListOfLocName)-3] == "Locator"):
                mmLeftFootLocators[int(mmTempNumber)] = mmLocator
                  
                #Store names to use later
                mmLeftFootNamers[int(mmTempNumber)] = mmListOfLocName[0] + "_" + mmListOfLocName[1] + "_" + mmListOfLocName[2] + "_" + mmListOfLocName[3] + "_Bone"

             
            elif (mmListOfLocName[0] == "right" and mmListOfLocName[1] == "Foot" and mmListOfLocName[len(mmListOfLocName)-3] == "Locator"):
                mmRightFootLocators[int(mmTempNumber)] = mmLocator
                  
                #Store names to use later
                mmRightFootNamers[int(mmTempNumber)] = mmListOfLocName[0] + "_" + mmListOfLocName[1] + "_" + mmListOfLocName[2] + "_" + mmListOfLocName[3] + "_Bone"


            if ( len(mmListOfLocName) >= 2 and mmListOfLocName[1] == "Foot" ):
                cmds.parent( mmLocator, mmGroup_Foot_BuildLocator )

        if ( mmListOfLocNameLen > 1 ):
            if ( mmListOfLocName[0] == "leftToe" ):
                mmLeftToeLoc = mmLocator
                mmToeConfirmBool = True

                print("found leftToe")

            if ( mmListOfLocName[0] == "rightToe" ):
                mmRightToeLoc = mmLocator
                mmToeConfirmBool = True

                print("found rightToe")

   
    #clear selection
    cmds.select( cl = 1)
        
    
    #Create a counter to go through both feet
    mmCounter = 0
    
    #Create a list to equate to the list of locators which was gathered above
    mmCurrentFootLocators = []
    mmCurrentFootBoneNamers = []
    
    mmFootName = "bob"
    mmCurrentController = None
    mmCurrentToeLoc = ""
    
    # print "mmLeftFootLocators", mmLeftFootLocators
    # print "mmRightFootLocators", mmRightFootLocators
          
    #Need to create the required attributes on both foot controls, as well as required bones and heirarchy
    while mmCounter < 2:
        
        #Select the proper foot control
        if (mmCounter == 0):
            #Select the left foot control
            #****Should this be able to figure out different names?****
            mmCurrentFoot_Control = mmLeftFoot_Control
            mmFootName = "left"
            mmCurrentFootLoc = mmLeftFootLoc
            mmCurrentToeLoc = mmLeftToeLoc
             
            #Assign list of desired foot locators to a general list
            mmCurrentFootLocators = list(mmLeftFootLocators)
            mmCurrentFootBoneNamers = list(mmLeftFootNamers)
            
            #Need an angle multiplier for when things should be reversed
            mmAngleFlipper = 1
             
        elif (mmCounter == 1):
            #then select the right foot control
            #****Should this be able to figure out different names?****
            mmCurrentFoot_Control = mmRightFoot_Control
            mmFootName = "right"
            mmCurrentFootLoc = mmRightFootLoc
            mmCurrentToeLoc = mmRightToeLoc
             
            #Assign list of desired foot locators to a general list
            mmCurrentFootLocators = list(mmRightFootLocators)
            mmCurrentFootBoneNamers = list(mmRightFootNamers)
        
            #Need an angle multiplier for when things should be reversed
            mmAngleFlipper = -1


        #Need to find the mmParentObject of the passed foot loc
        cmds.select( mmCurrentFootLoc )
        mmRelativeList = cmds.listRelatives( p = True )

        mmParentObject = mmRelativeList[0]


        ######################################
        #--Create bones on top of locators where they should be--
        #And place the Reverse Foot Rig Bones into their proper Heirarchy (at the same time)
        ######################################

        #Create a default value
        mmCounterInner = 0
        mmLastCreatedJoint = "bob"
        mmRevFTRigList = []
        

        # print "mmCurrentFootLocators", mmCurrentFootLocators
            
        for mmEachLocator in mmCurrentFootLocators:

            mmSearchingForTrans = cmds.getAttr(mmCurrentFootLocators[mmCounterInner]+".translate")
            
            #Don't want to have joints made with parents if they are certain joints
            if ( mmCounterInner == 0 ):
                #deselect previously selected - to make sure parent joint is not selected.
                cmds.select(cl = 1)
                mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
                #cmds.parent( mmNewlyCreatedJoint, mmCurrentFoot_Control, r = 0 )

                
            elif ( mmCounterInner == 6 ):
                #print "mmRevFTRigList", mmRevFTRigList
                # This works, but I think its putting the group in the wrong place, lets try a group in place instead.
                # mmHeelBoneGroup = cmds.group( mmRevFTRigList[0] )
                # mmHeelBoneGroup = cmds.rename( mmHeelBoneGroup, mmRevFTRigList[0] + "_Group" )

                mmHeelBoneGroup = mmOF.mmGroupInPlace( mmRevFTRigList[0] , "_Group" )

                cmds.parentConstraint( mmEachLocator, mmHeelBoneGroup, mo = 1 )

                #Organize
                cmds.parent( mmHeelBoneGroup, mmGroup_Foot_Hidden )

            elif ( mmCounterInner == 7 ):
                #print "mmCurrentFootLocators", mmCurrentFootLocators
                mmInnerLocGroup = cmds.group( mmCurrentFootLocators[6] )
                mmInnerLocGroup = cmds.rename( mmInnerLocGroup, mmCurrentFootLocators[6] + "_Group" )
                cmds.parentConstraint( mmEachLocator, mmInnerLocGroup, mo = 1 )

                mmOuterLocGroup = cmds.group( mmCurrentFootLocators[7] )
                mmOuterLocGroup = cmds.rename( mmOuterLocGroup, mmCurrentFootLocators[7] + "_Group" )
                cmds.parentConstraint( mmCurrentFoot_Control, mmOuterLocGroup, mo = 1 )



            else:
                mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
                cmds.joint( mmLastCreatedJoint, e = True, zso = True, oj = "yzx", sao = 'yup' )
            
            if ( mmCounterInner < 6 ):
                #Rename Joint, but don't run this on iterate 6 & 7, because there are no joints
                #print "mmCurrentFootBoneNamers", mmCurrentFootBoneNamers
                mmNewlyCreatedJoint = cmds.rename( mmNewlyCreatedJoint, mmCurrentFootBoneNamers[mmCounterInner] + "_RevFt" )
            
                #Store the joint in a list for use later
                mmRevFTRigList.append(mmNewlyCreatedJoint)
                
                mmLastCreatedJoint = mmNewlyCreatedJoint


            mmCounterInner += 1
        

        #deselect previously selected - to make sure parent joint is not selected.
        cmds.select(cl = 1)
        
        mmFWFTRigList = []
        
        ######################################
        #--Create the Forward Foot Rig Bones--
        ######################################

        mmCounterInner = 5
        
        
        for mmEachLocator in mmCurrentFootLocators:
            
            mmSearchingForTrans = cmds.getAttr(mmCurrentFootLocators[mmCounterInner]+".translate")
            
            if ( mmCounterInner > 1):
                
                if ( mmCounterInner == 5 ):
                    
                    #Need to create a bone at the parent bone now instead of later
                    #deselect previously selected - to make sure parent joint is not selected.
                    cmds.select(cl = 1)
                    mmSearchingForTrans2 = cmds.xform( mmParentObject, q = 1, t = 1, ws = 1 )
                    

                    mmNewlyCreatedParentJoint = cmds.joint( p = mmSearchingForTrans2 )
                        
                    mmNewlyCreatedParentJoint = cmds.rename( mmNewlyCreatedParentJoint, mmParentObject + "_FwFt_" + mmFootName + "_Bone" )
                
                    mmLastCreatedJoint = mmNewlyCreatedParentJoint
                    
                    cmds.parent( mmNewlyCreatedParentJoint, mmGroup_Foot_MainBone )

                    #Set up the newly created joints to follow the parent bone passed in
                    cmds.pointConstraint( mmParentObject, mmNewlyCreatedParentJoint )
                    #print "constraining mmNewlyCreatedParentJoint to mmParentObject"
                    
                #Don't want to have joints made with parents if they are certain joints
                if ( mmCounterInner > 1 ):
                    if ( mmCounterInner == 4 ):
                        cmds.select(cl = 1)

                        mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
                        cmds.parent( mmNewlyCreatedJoint, mmLastCreatedJoint )


                    else:

                        mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
                        cmds.joint( mmLastCreatedJoint, e = True, zso = True, oj = "yzx", sao = 'yup' )
                        
                    mmNewlyCreatedJoint = cmds.rename( mmNewlyCreatedJoint, mmCurrentFootBoneNamers[mmCounterInner] + "_FwFt" )

                
                #Store the joint in a list for use later
                mmFWFTRigList.append(mmNewlyCreatedJoint)
                
                mmLastCreatedJoint = mmNewlyCreatedJoint
    
                mmCounterInner -= 1
        
        ######################################
        #Create IK handles across various bones and connect them as appropriate
        ######################################

        #Creating IK handles on Forward Foot Rig
        mmOriginalIKHandleName = mmRF.mmCreateIKHandle( mmFWFTRigList[0], mmFWFTRigList[1], "sc" )
        mmAnkleIKHandleName = mmRF.mmCreateIKHandle( mmFWFTRigList[1], mmFWFTRigList[2], "sc" )
        mmToeIKHandleName = mmRF.mmCreateIKHandle( mmFWFTRigList[2], mmFWFTRigList[3], "sc" )
        
        #Parent IK handles into reverse foot rig
        #cmds.parentConstraint( Parent, Child )
        cmds.parent( mmOriginalIKHandleName, mmRevFTRigList[4] )
        cmds.parent( mmAnkleIKHandleName, mmRevFTRigList[3] )
        
        
        #except toe ik - needs to go under a special new locator
        mmTempTransX = cmds.getAttr( mmCurrentFootLocators[3] + ".translateX" )
        mmTempTransY = cmds.getAttr( mmCurrentFootLocators[3] + ".translateY" )
        mmTempTransZ = cmds.getAttr( mmCurrentFootLocators[3] + ".translateZ" )
        
        mmToeLoc = cmds.spaceLocator(  )
        mmToeLoc = cmds.rename( mmFootName + "ToeRotator_RevFt" )
        cmds.move( mmTempTransX, mmTempTransY, mmTempTransZ )
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
        
        #parent ToeIK to ToeLoc
        cmds.parent( mmToeIKHandleName, mmToeLoc )
        #And parent ToeLoc into RevFoot Hierarchy
        cmds.parent( mmToeLoc, mmRevFTRigList[2] )
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
        
        #Create measuring tool, dupe bone on top of mmBoneOnParent, then parent in locators, create IK and connect to measuring tool
        #create a distance node to find the space between upper joints
        mmStretch_distanceShapeNodeName = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmFWFTRigList[0]+"_distanceNode#")
        
        #create locators
        mmStretch_firstLocator = cmds.spaceLocator( p = [0,0,0], n = mmFWFTRigList[0]+"_parentLocator#")
        mmStretch_secondLocator = cmds.spaceLocator( p = [0,0,0], n = mmFWFTRigList[0]+"_childLocator#")
        
        cmds.parent( mmStretch_firstLocator, mmGroup_Foot_Hidden )
        cmds.parent( mmStretch_secondLocator, mmGroup_Foot_Hidden )
        
        #attach locators to distance node
        cmds.connectAttr( mmStretch_firstLocator[0]+".translate", mmStretch_distanceShapeNodeName+".point1")
        cmds.connectAttr( mmStretch_secondLocator[0]+".translate", mmStretch_distanceShapeNodeName+".point2")
        
        #move locators to selected joint and its first child
        cmds.pointConstraint( mmParentObject, mmStretch_firstLocator, mo = 0)
        
        #mmSearchingForTransParent = cmds.getAttr(mmParentObject + ".translate" )
        
        #store to return
        mmBonesOnParent.append(mmStretch_firstLocator)
        
        cmds.pointConstraint( mmRevFTRigList[5], mmStretch_secondLocator, mo = 0)
        
        #mmSearchingForTransChild = cmds.getAttr(mmFWFTRigList[0] + ".translate" )


        #mmNewlyCreatedChildJoint = cmds.joint( p = mmSearchingForTransChild[0] )
        #instead of creating a new joint, lets try using the base fw rig joint
        mmNewlyCreatedChildJoint =  mmFWFTRigList[0]
        
        mmDistanceIKHandleName = mmRF.mmCreateIKHandle( mmNewlyCreatedParentJoint, mmNewlyCreatedChildJoint, "sc" )
        
        #Need to connect the ChildBone's length to the distance of the measuring tool
        cmds.connectAttr( mmStretch_distanceShapeNodeName + ".distance", mmNewlyCreatedChildJoint + ".translateY" )
        
        #Need to parent constrain the IK handle to the Reverse Foot Rig so it moves around properly
        cmds.parentConstraint( mmRevFTRigList[5], mmDistanceIKHandleName )
        
        cmds.parent ( mmDistanceIKHandleName, mmGroup_Foot_Hidden )
        
        ######################################
        
        #Creating reverse foot attributes needed
        cmds.select( mmCurrentFoot_Control )
        cmds.addAttr( longName="FootRoll", attributeType='double', min = -20, max = 20, dv=0, k = 1 )
        mmFootRollAttr = mmCurrentFoot_Control + ".FootRoll"
        
        cmds.addAttr( longName="FootBank", attributeType='double', min = -10, max = 10, dv=0, k = 1 )
        mmFootBankAttr = mmCurrentFoot_Control + ".FootBank"
        
        cmds.addAttr( longName="ToeBend", attributeType='double', min = -10, max = 10, dv=0, k = 1 ) 
        mmToeBendAttr = mmCurrentFoot_Control + ".ToeBend"
        
        cmds.addAttr( longName="ToeSwivel", attributeType='double', min = -10, max = 10, dv=0, k = 1 )
        mmToeSwivelAttr = mmCurrentFoot_Control + ".ToeSwivel"
        
        cmds.select( cl = 1 )

        ######################################
        #Create Set Driven Keys for various values
        ######################################

        '''
        #Example SDK creation
        1- Identify what things you will be keying
                mmObjectController
                mmObjectSlave
        2- Ensure both controller and slave are set to the proper value - or assume they are correct values (dangerous)
                cmds.setAttr( mmObjectController, mmCurrentValue )
                cmds.setAttr( mmObjectSlave, mmCurrentValue )
        3- Create a key on the thing being driven and point that key to look at the controller
                cmds.setDrivenKeyframe( mmObjectSlave, currentDriver = mmObjectController)
        4- Iterate through the various min/max and set all the keys needed.
        
        #In Function Form: 
        mmRF.mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )

        '''
        
        '''Connect the Foot Roll to the Heel and Toe both rotating up to 90 degrees, also toe roll'''
        mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-20, -10, 10, 20], [180, 90, 0, 0], 1 )
        mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[2], ".rotateX",  [-20, -10, 5, 10, 20], [0, 0, 0, 90, 180], 1 )
        mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[3], ".rotateX",  [-20, -10, 5, 10, 20], [0, 0, 45, 0, 0], 1 )
        
        '''Connect the Foot Bank to the Inner and Outer Locators'''
        mmRF.mmCreateSDK( mmFootBankAttr, mmCurrentFootLocators[6], ".rotateZ", [-10, 10], [0, 90], mmAngleFlipper )
        mmRF.mmCreateSDK( mmFootBankAttr, mmCurrentFootLocators[7], ".rotateZ", [-10, 10], [-90, 0], mmAngleFlipper )
        
        '''Connect the Toe Bend to the Toe Bend Locator'''
        mmRF.mmCreateSDK( mmToeBendAttr, mmToeLoc, ".rotateX", [-10, 10], [-90, 90], 1 )
      
        '''Connect the Toe Swivel to the Toe Swivel Locator'''
        mmRF.mmCreateSDK( mmToeSwivelAttr, mmRevFTRigList[1], ".rotateZ", [-10, 10], [-90, 90], 1 )
         
        cmds.select( cl =1 )
        
        #Need to parent in the foot so it moves appropriately
        cmds.select( mmCurrentFootLoc )
        mmRelativeList = cmds.listRelatives(  )

        #First find old parentconstraint and delete it
        for mmRelative in mmRelativeList:
            mmRelativeChecker = mmRelative.split("_")

            for mmRelativeName in mmRelativeChecker:
                #print "mmRelative", mmRelative
                if ( mmRelativeName[0:6] == "parent" ):
                    cmds.select( mmRelative )
                    cmds.delete()

        #Then give it a new constraint
        cmds.parentConstraint( mmFWFTRigList[0], mmCurrentFootLoc, mo = 1)
        
        # print "mmToeConfirmBool", mmToeConfirmBool

        if ( mmToeConfirmBool ):
            #Need to find the toe, delete its loc's parentConstraint, then its control, and then parentConstraint its loc into the appropriate place.

            #First must find old parent const
            cmds.select( mmCurrentToeLoc )
            mmRelativeList = cmds.listRelatives(  )

            #First find old parentconstraint and delete it
            for mmRelative in mmRelativeList:
                mmRelativeChecker = mmRelative.split("_")

                for mmRelativeName in mmRelativeChecker:
                    #print "mmRelative", mmRelative
                    if ( mmRelativeName[0:6] == "parent" ):
                        cmds.select( mmRelative )
                        cmds.delete()

            #Delete the Toe Control
            mmToeControlName = mmCurrentToeLoc.split("_")[0] + "_Control"

            # print "mmToeControlName", mmToeControlName

            cmds.delete(mmToeControlName)

            cmds.parentConstraint( mmFWFTRigList[2], mmCurrentToeLoc, mo = 1)

            # print "mmFWFTRigList[2]", mmFWFTRigList[2]
            
        mmCounter += 1


    #This return does nothing.  Didn't really have a plan for it either, could just remove.
    return mmBonesOnParent
"""
#####################################################################

'''
This Function takes the input of two locators for a foot that already exists.
'''
def mmCreateRevFootRig( mmLeftFootLoc, mmRightFootLoc ):
    #clear selection
    cmds.select( cl = 1)
    
    #Create a counter to go through both feet
    mmCounter = 0
    mmCurrentFootSide = "bob"
    
    #Need to create the required attributes on both foot controls, as well as required bones and heirarchy
    while mmCounter < 2:
        
        #Select the proper foot control
        if (mmCounter == 0):
            #Select the left foot control
            mmCurrentFootLoc = mmLeftFootLoc
            mmCurrentFootSide = "left"
            
        elif (mmCounter == 1):
            #then select the right foot control
            mmCurrentFootLoc = mmRightFootLoc
            mmCurrentFootSide = "right"

        mmCreateIndividualRevFootRig( mmCurrentFootLoc, mmCurrentFootSide )
        mmCounter += 1

    #This return does nothing.  Didn't really have a plan for it either, could just remove.
    return

'''
This Function takes the input of two locators for a foot that already exists.
After creating the forward and reverse foot systems, the bone which was created on top of the parent node is returned.
'''
# mmFootName = "left" or "right"
def mmCreateIndividualRevFootRig( mmCurrentFootLoc, mmFootName ):
    if mmCurrentFootLoc == None or mmFootName == None:
        print "Invalid information passed to mmC3MRTMR.mmCreateIndividualRevFootRig, skipping."
        return

    print "running script mmCreateIndividualRevFootRig"

    #Verify that groups are created
    mmCreateRigGroups()

    '''
    #Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''
    
    mmDictOfRevFootLists = {}

    #mmCreateIndividualRevFootRig should return mmDictOfRevFootLists with information of:
    #   Plus toes somewhere
    #{
    #   "revFootList":      [ Reverse Foot Bone0, 1, 2, etc ],
    #   "forFootList":      [ Forward Foot Bone0, 1, 2, etc ],
    #   "distSystem":       [ mmStretch_distanceShapeNodeName, mmStretch_firstLocator, mmStretch_secondLocator, mmDistanceIKHandleName ],
    #   "ikHandle":         [ mmForwardFootIKHandleName ],
    #   "footParentLoc":    [ mmFootLoc ],
    #   "footMesh":         [ mmFootMesh ],
    #   "footControl":      [ mmCurrentFoot_Control ]
    #}

    #Need to Organize!
    #Create groups to store stuff away
    mmGroup_Foot_Hidden = mmEnsureGroupExists( "_Group_Foot_Hidden" )
    mmGroup_Foot_MainBone = mmEnsureGroupExists( "_Group_Foot_MainBones" )
    mmGroup_Foot_BuildLocator = mmEnsureGroupExists( "_Group_Foot_BuildLocators" )

    cmds.select(cl= 1)
    # print "mmGroup_Foot_Hidden", mmGroup_Foot_Hidden
    # print "cmds.listRelatives( mmGroup_Foot_Hidden, p = True )", cmds.listRelatives( mmGroup_Foot_Hidden, p = True )
    
    if cmds.listRelatives( mmGroup_Foot_Hidden, p = True ) == None or cmds.listRelatives( mmGroup_Foot_Hidden, p = True )[0] != mmGroup_Hidden :
        cmds.parent( mmGroup_Foot_Hidden, mmGroup_Hidden )
    if cmds.listRelatives( mmGroup_Foot_MainBone, p = True ) == None or cmds.listRelatives( mmGroup_Foot_MainBone, p = True )[0] != mmGroup_MainBones :
        cmds.parent( mmGroup_Foot_MainBone, mmGroup_MainBones )
    if cmds.listRelatives( mmGroup_Foot_BuildLocator, p = True ) == None or cmds.listRelatives( mmGroup_Foot_BuildLocator, p = True )[0] != mmGroup_BuildLocator :
        cmds.parent( mmGroup_Foot_BuildLocator, mmGroup_BuildLocator )

    mmBonesOnParent = []
    
    mmCurrentFoot_Control = mmCurrentFootLoc.split("_")[0] + "_Control"

    mmToeConfirmBool = False
    mmCurrentToeLoc = ""    

    ''' Assume left and right feet are ready for Reverse Foot Rig, create and connect '''
    
    #First select all rev foot locators (for both feet)
    #And store them into the appropriate ordered list location - can't sort by the number exactly because we don't know what order they are selected in.
    mmCurrentFootLocators = {}
    mmCurrentFootBoneNamers = {}
    mmLocatorShapesInScene = cmds.ls( type = ("locator") )
    
    #Find the parent (which should always be the transforms)
    mmLocatorsInScene = cmds.listRelatives(mmLocatorShapesInScene, parent=True, fullPath=0)
    
    for mmLocator in mmLocatorsInScene:

        mmListOfLocName = mmLocator.split("_")
        mmListOfLocNameLen = len(mmListOfLocName)

        if (mmListOfLocNameLen > 4):
            mmTempNumber = mmListOfLocName[len(mmListOfLocName)-4]

            # print "mmListOfLocName", mmListOfLocName

            if (mmListOfLocName[0] == mmFootName and mmListOfLocName[1] == "Foot" and mmListOfLocName[len(mmListOfLocName)-3] == "Locator"):
                mmCurrentFootLocators[int(mmTempNumber)] = mmLocator
                  
                #Store names to use later
                mmCurrentFootBoneNamers[int(mmTempNumber)] = mmListOfLocName[0] + "_" + mmListOfLocName[1] + "_" + mmListOfLocName[2] + "_" + mmListOfLocName[3] + "_Bone"

            if ( len(mmListOfLocName) >= 2 and mmListOfLocName[1] == "Foot" ):
                if cmds.listRelatives( mmLocator, p = True ) == None :
                    cmds.parent( mmLocator, mmGroup_Foot_BuildLocator )

        if ( mmListOfLocNameLen > 1 ):
            if ( mmListOfLocName[0] == mmFootName + "Toe" ):
                mmCurrentToeLoc = mmLocator
                mmToeConfirmBool = True
    
    #clear selection
    cmds.select( cl = 1)
    
    mmAngleFlipper = 1
    #Select the proper foot control
    if (mmFootName == "right"):
        #Need an angle multiplier for when things should be reversed
        mmAngleFlipper = -1

    #Need to find the mmParentObject of the passed foot loc
    cmds.select( mmCurrentFootLoc )
    mmRelativeList = cmds.listRelatives( p = True )

    mmParentObject = mmRelativeList[0]

    mmParentLocChecker = mmParentObject.split("_")
    mmParentLoc = mmParentLocChecker[0] 
    mmCurrentParentLoc = mmParentLoc + "_loc"

    print ""
    print "***************************"
    print "mmParentObject", mmParentObject


    print "creating reverse foot rig bones"
    
    ######################################
    #--Create bones on top of locators where they should be--
    #And place the Reverse Foot Rig Bones into their proper Heirarchy (at the same time)
    ######################################

    #Create a default value
    mmCounterInner = 0
    mmLastCreatedJoint = "bob"
    mmRevFTRigList = []
    

    # print "mmCurrentFootLocators", mmCurrentFootLocators
        
    for mmKey, mmEachLocator in mmCurrentFootLocators.items():

        mmSearchingForTrans = cmds.getAttr(mmCurrentFootLocators[mmCounterInner]+".translate")
        
        #Don't want to have joints made with parents if they are certain joints
        if ( mmCounterInner == 0 ):
            #deselect previously selected - to make sure parent joint is not selected.
            cmds.select(cl = 1)
            mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
            #cmds.parent( mmNewlyCreatedJoint, mmCurrentFoot_Control, r = 0 )

            
        elif ( mmCounterInner == 6 ):
            mmHeelBoneGroup = mmOF.mmGroupInPlace( mmRevFTRigList[0] , "_Group" )
            # print "mmHeelBoneGroup", mmHeelBoneGroup
            # print "mmEachLocator", mmEachLocator

            cmds.parentConstraint( mmEachLocator, mmHeelBoneGroup, mo = 1 )

            #Organize
            cmds.parent( mmHeelBoneGroup, mmGroup_Foot_Hidden )

        elif ( mmCounterInner == 7 ):
            #print "mmCurrentFootLocators", mmCurrentFootLocators
            mmInnerLocGroup = cmds.group( mmCurrentFootLocators[6] )
            mmInnerLocGroup = cmds.rename( mmInnerLocGroup, mmCurrentFootLocators[6] + "_Group" )
            cmds.parentConstraint( mmEachLocator, mmInnerLocGroup, mo = 1 )

            mmOuterLocGroup = cmds.group( mmCurrentFootLocators[7] )
            mmOuterLocGroup = cmds.rename( mmOuterLocGroup, mmCurrentFootLocators[7] + "_Group" )
            cmds.parentConstraint( mmCurrentFoot_Control, mmOuterLocGroup, mo = 1 )

        else:
            mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
            cmds.joint( mmLastCreatedJoint, e = True, zso = True, oj = "yzx", sao = 'yup' )
        
        if ( mmCounterInner < 6 ):
            #Rename Joint, but don't run this on iterate 6 & 7, because there are no joints
            #print "mmCurrentFootBoneNamers", mmCurrentFootBoneNamers
            mmNewlyCreatedJoint = cmds.rename( mmNewlyCreatedJoint, mmCurrentFootBoneNamers[mmCounterInner] + "_RevFt" )
        
            #Store the joint in a list for use later
            mmRevFTRigList.append(mmNewlyCreatedJoint)
            
            mmLastCreatedJoint = mmNewlyCreatedJoint


        mmCounterInner += 1
    
    mmDictOfRevFootLists["revFootList"] = mmRevFTRigList

    #deselect previously selected - to make sure parent joint is not selected.
    cmds.select(cl = 1)
    
    mmFWFTRigList = []
    
    print "creating forward food rig bones"
    
    ######################################
    #--Create the Forward Foot Rig Bones--
    ######################################

    mmCounterInner = 5
    
    
    for mmEachLocator in mmCurrentFootLocators:
        
        mmSearchingForTrans = cmds.getAttr(mmCurrentFootLocators[mmCounterInner]+".translate")
        
        if ( mmCounterInner > 1):
            
            if ( mmCounterInner == 5 ):
                
                #Need to create a bone at the parent bone now instead of later
                #deselect previously selected - to make sure parent joint is not selected.
                cmds.select(cl = 1)
                mmSearchingForTrans2 = cmds.xform( mmParentObject, q = 1, t = 1, ws = 1 )
                mmNewlyCreatedParentJoint = cmds.joint( p = mmSearchingForTrans2 )
                mmNewlyCreatedParentJoint = cmds.rename( mmNewlyCreatedParentJoint, mmParentObject + "_FwFt_" + mmFootName + "_Bone" )
                mmLastCreatedJoint = mmNewlyCreatedParentJoint
                cmds.parent( mmNewlyCreatedParentJoint, mmGroup_Foot_MainBone )

                #Set up the newly created joints to follow the parent bone passed in
                cmds.pointConstraint( mmParentObject, mmNewlyCreatedParentJoint )
                
            #Don't want to have joints made with parents if they are certain joints
            if ( mmCounterInner > 1 ):
                if ( mmCounterInner == 4 ):
                    cmds.select(cl = 1)

                    mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
                    cmds.parent( mmNewlyCreatedJoint, mmLastCreatedJoint )
                else:
                    mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
                    cmds.joint( mmLastCreatedJoint, e = True, zso = True, oj = "yzx", sao = 'yup' )
                    
                mmNewlyCreatedJoint = cmds.rename( mmNewlyCreatedJoint, mmCurrentFootBoneNamers[mmCounterInner] + "_FwFt" )

            
            #Store the joint in a list for use later
            mmFWFTRigList.append(mmNewlyCreatedJoint)
            
            mmLastCreatedJoint = mmNewlyCreatedJoint

            mmCounterInner -= 1
    
    print "creating ik handles"

    ######################################
    #Create IK handles across various bones and connect them as appropriate
    ######################################

    #Creating IK handles on Forward Foot Rig
    # All "sc"'s were converted to "rp"'s because of some unexplicable issue with ogre feet.
    #   Switching them to RP even though they are only single joint chains somehow works.
    #   Leaving unless it breaks other stuff, then can switch back.
    mmOriginalIKHandleName = mmRF.mmCreateIKHandle( mmFWFTRigList[0], mmFWFTRigList[1], "rp" )
    mmAnkleIKHandleName = mmRF.mmCreateIKHandle( mmFWFTRigList[1], mmFWFTRigList[2], "rp" )
    mmToeIKHandleName = mmRF.mmCreateIKHandle( mmFWFTRigList[2], mmFWFTRigList[3], "rp" )
    
    #Parent IK handles into reverse foot rig
    #cmds.parentConstraint( Parent, Child )
    cmds.parent( mmOriginalIKHandleName, mmRevFTRigList[4] )
    cmds.parent( mmAnkleIKHandleName, mmRevFTRigList[3] )
    
    
    #except toe ik - needs to go under a special new locator
    mmTempTransX = cmds.getAttr( mmCurrentFootLocators[3] + ".translateX" )
    mmTempTransY = cmds.getAttr( mmCurrentFootLocators[3] + ".translateY" )
    mmTempTransZ = cmds.getAttr( mmCurrentFootLocators[3] + ".translateZ" )
    
    mmToeLoc = cmds.spaceLocator(  )
    mmToeLoc = cmds.rename( mmFootName + "ToeRotator_RevFt" )
    cmds.move( mmTempTransX, mmTempTransY, mmTempTransZ )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
    
    #parent ToeIK to ToeLoc
    cmds.parent( mmToeIKHandleName, mmToeLoc )
    #And parent ToeLoc into RevFoot Hierarchy
    cmds.parent( mmToeLoc, mmRevFTRigList[2] )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
    
    #Create measuring tool, dupe bone on top of mmBoneOnParent, then parent in locators, create IK and connect to measuring tool
    #create a distance node to find the space between upper joints
    mmStretch_distanceShapeNodeName = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmFWFTRigList[0]+"_distanceNode#")
    
    #create locators
    mmStretch_firstLocator = cmds.spaceLocator( p = [0,0,0], n = mmFWFTRigList[0]+"_parentLocator#")
    mmStretch_secondLocator = cmds.spaceLocator( p = [0,0,0], n = mmFWFTRigList[0]+"_childLocator#")
    
    cmds.parent( mmStretch_firstLocator, mmGroup_Foot_Hidden )
    cmds.parent( mmStretch_secondLocator, mmGroup_Foot_Hidden )
    
    #attach locators to distance node
    cmds.connectAttr( mmStretch_firstLocator[0]+".translate", mmStretch_distanceShapeNodeName+".point1")
    cmds.connectAttr( mmStretch_secondLocator[0]+".translate", mmStretch_distanceShapeNodeName+".point2")
    
    #move locators to selected joint and its first child
    cmds.pointConstraint( mmParentObject, mmStretch_firstLocator, mo = 0)
    
    #store to return
    mmBonesOnParent.append(mmStretch_firstLocator)
    
    cmds.pointConstraint( mmRevFTRigList[5], mmStretch_secondLocator, mo = 0)
    
    #instead of creating a new joint, lets try using the base fw rig joint
    mmNewlyCreatedChildJoint =  mmFWFTRigList[0]
    
    # All "sc"'s were converted to "rp"'s because of some unexplicable issue with ogre feet.
    #   Switching them to RP even though they are only single joint chains somehow works.
    #   Leaving unless it breaks other stuff, then can switch back.
    mmDistanceIKHandleName = mmRF.mmCreateIKHandle( mmNewlyCreatedParentJoint, mmNewlyCreatedChildJoint, "rp" )
    
    #Need to connect the ChildBone's length to the distance of the measuring tool
    cmds.connectAttr( mmStretch_distanceShapeNodeName + ".distance", mmNewlyCreatedChildJoint + ".translateY" )
    
    #Need to parent constrain the IK handle to the Reverse Foot Rig so it moves around properly
    cmds.parentConstraint( mmRevFTRigList[5], mmDistanceIKHandleName )
    
    cmds.parent ( mmDistanceIKHandleName, mmGroup_Foot_Hidden )
    
    mmDictOfRevFootLists["forFootList"] = mmFWFTRigList

    mmDictOfRevFootLists["distSystem"] = [ mmStretch_distanceShapeNodeName, mmStretch_firstLocator, mmStretch_secondLocator, mmDistanceIKHandleName ]
    mmDictOfRevFootLists["ikHandle"] = [ mmOriginalIKHandleName, mmAnkleIKHandleName, mmToeIKHandleName ]
    
    ######################################
    
    #Creating reverse foot attributes needed
    cmds.select( mmCurrentFoot_Control )
    cmds.addAttr( longName="FootRoll", attributeType='double', min = -20, max = 20, dv=0, k = 1 )
    mmFootRollAttr = mmCurrentFoot_Control + ".FootRoll"
    
    cmds.addAttr( longName="FootBank", attributeType='double', min = -10, max = 10, dv=0, k = 1 )
    mmFootBankAttr = mmCurrentFoot_Control + ".FootBank"
    
    cmds.addAttr( longName="ToeBend", attributeType='double', min = -10, max = 10, dv=0, k = 1 ) 
    mmToeBendAttr = mmCurrentFoot_Control + ".ToeBend"
    
    cmds.addAttr( longName="ToeSwivel", attributeType='double', min = -10, max = 10, dv=0, k = 1 )
    mmToeSwivelAttr = mmCurrentFoot_Control + ".ToeSwivel"
    
    cmds.select( cl = 1 )

    print "creating set driven keys"
    
    ######################################
    #Create Set Driven Keys for various values
    ######################################

    '''
    #Example SDK creation
    1- Identify what things you will be keying
            mmObjectController
            mmObjectSlave
    2- Ensure both controller and slave are set to the proper value - or assume they are correct values (dangerous)
            cmds.setAttr( mmObjectController, mmCurrentValue )
            cmds.setAttr( mmObjectSlave, mmCurrentValue )
    3- Create a key on the thing being driven and point that key to look at the controller
            cmds.setDrivenKeyframe( mmObjectSlave, currentDriver = mmObjectController)
    4- Iterate through the various min/max and set all the keys needed.
    
    #In Function Form: 
    mmRF.mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )

    '''
    
    '''Connect the Foot Roll to the Heel and Toe both rotating up to 90 degrees, also toe roll'''
    mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-20, -10, 10, 20], [180, 90, 0, 0], 1 )
    mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[2], ".rotateX",  [-20, -10, 5, 10, 20], [0, 0, 0, 90, 180], 1 )
    mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[3], ".rotateX",  [-20, -10, 5, 10, 20], [0, 0, 45, 0, 0], 1 )
    
    '''Connect the Foot Bank to the Inner and Outer Locators'''
    mmRF.mmCreateSDK( mmFootBankAttr, mmCurrentFootLocators[6], ".rotateZ", [-10, 10], [0, 90], mmAngleFlipper )
    mmRF.mmCreateSDK( mmFootBankAttr, mmCurrentFootLocators[7], ".rotateZ", [-10, 10], [-90, 0], mmAngleFlipper )
    
    '''Connect the Toe Bend to the Toe Bend Locator'''
    mmRF.mmCreateSDK( mmToeBendAttr, mmToeLoc, ".rotateX", [-10, 10], [-90, 90], 1 )
  
    '''Connect the Toe Swivel to the Toe Swivel Locator'''
    mmRF.mmCreateSDK( mmToeSwivelAttr, mmRevFTRigList[1], ".rotateZ", [-10, 10], [-90, 90], 1 )
     
    cmds.select( cl =1 )
    
    print "parenting things together"
    
    #Need to parent in the foot so it moves appropriately
    cmds.select( mmCurrentFootLoc )
    mmRelativeList = cmds.listRelatives(  )

    print "mmRelativeList", mmRelativeList

    #First find old parentconstraint and delete it
    #   What if there isn't one?
    for mmRelative in mmRelativeList:
        mmRelativeChecker = mmRelative.split("_")

        for mmRelativeName in mmRelativeChecker:
            if ( mmRelativeName[0:6] == "parent" ):
                cmds.select( mmRelative )
                cmds.delete()

    #Then give it a new constraint
    print "mmFWFTRigList[0]", mmFWFTRigList[0]

    print "mmCurrentFootLoc", mmCurrentFootLoc

    # This is the problem, what is happening and why?
    cmds.parentConstraint( mmFWFTRigList[0], mmCurrentFootLoc, mo = 1)
    
    if ( mmToeConfirmBool ):
        #Need to find the toe, delete its loc's parentConstraint, then its control, and then parentConstraint its loc into the appropriate place.

        #First must find old parent const
        cmds.select( mmCurrentToeLoc )
        mmRelativeList = cmds.listRelatives(  )
        
        print "toe mmRelativeList", mmRelativeList

        #First find old parentconstraint and delete it
        for mmRelative in mmRelativeList:
            mmRelativeChecker = mmRelative.split("_")

            for mmRelativeName in mmRelativeChecker:
                #print "mmRelative", mmRelative
                if ( mmRelativeName[0:6] == "parent" ):
                    cmds.select( mmRelative )
                    cmds.delete()

        #Delete the Toe Control
        mmToeControlName = mmCurrentToeLoc.split("_")[0] + "_Control"
        cmds.delete(mmToeControlName)
        cmds.parentConstraint( mmFWFTRigList[2], mmCurrentToeLoc, mo = 1) 
    
    mmDictOfRevFootLists["footParentLoc"] = [mmCurrentParentLoc]

    if ( mmFootName != "center" and mmFootName != "Center" ):
        mmDictOfRevFootLists["footMesh"] = [mmFootName + mmParentLoc]
    else:
        mmDictOfRevFootLists["footMesh"] = [mmParentLoc]

    mmDictOfRevFootLists["footControl"] = [mmCurrentFoot_Control]


    #This return now passes pertinent information back to mmCreateLimbActual.
    return mmDictOfRevFootLists

'''
This Function should take in some sort of passed in arguement, create a specific rev foot rig for that set, and returns various information.
After creating the forward and reverse foot systems, the bone which was created on top of the parent node is returned.
'''
def mmCreateRevFootRigNoToe( mmPassedInLimbSet = "", *args ):

    #This is how the script knows which foot to work on.
    if ( mmPassedInLimbSet == "" ):
        print "Must provide the limb set # which this foot belongs to in mmC3MTMR.mmCreateRevFootRigPrimer"
        return None
    else:
        mmPassedInLimbSet = str(mmPassedInLimbSet)

    #Verify that groups are created
    mmCreateRigGroups()

    '''
    # Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''
    
    mmDictOfRevFootLists = {}

    #mmCreateRevFootRigNoToe should return mmDictOfRevFootLists with information of:
    #{
    #   "revFootList":      [ Reverse Foot Bone0, 1, 2, etc ],
    #   "forFootList":      [ Forward Foot Bone0, 1, 2, etc ],
    #   "distSystem":       [ mmStretch_distanceShapeNodeName, mmStretch_firstLocator, mmStretch_secondLocator, mmDistanceIKHandleName ],
    #   "ikHandle":         [ mmForwardFootIKHandleName ],
    #   "footParentLoc":    [ mmFootLoc ],
    #   "footMesh":         [ mmFootMesh ],
    #   "footControl":      [ mmCurrentFoot_Control ]
    #}

    #Need to Organize!
    #Create groups to store stuff away
    mmGroup_Foot_Hidden = cmds.group( em = True, n = "_Group_Foot_Hidden_" + str(mmPassedInLimbSet) )
    mmGroup_Foot_MainBone = cmds.group( em = True, n = "_Group_Foot_MainBones_" + str(mmPassedInLimbSet) )
    mmGroup_Foot_BuildLocator = cmds.group( em = True, n = "_Group_Foot_BuildLocators_" + str(mmPassedInLimbSet) )

    cmds.select(cl= 1)
    
    cmds.parent( mmGroup_Foot_Hidden, mmGroup_Hidden )
    cmds.parent( mmGroup_Foot_MainBone, mmGroup_MainBones )
    cmds.parent( mmGroup_Foot_BuildLocator, mmGroup_BuildLocator )

    
    ''' Should not assume left and right feet are ready for Reverse Foot Rig, only work on the one foot we want. '''
    
    #--------------------------------------------------------

    #First select all rev foot locators for the specific limb set we are working on
    #And store them into the appropriate ordered list location - can't sort by the number exactly because we don't know what order they are selected in.
    mmLocatorShapesInScene = cmds.ls( type = ("locator") )

    mmCurrentFootLocators = {}
    mmCurrentFootBoneNamers = {}

    #Find the parent (which should always be the transforms)
    mmLocatorsInScene = cmds.listRelatives(mmLocatorShapesInScene, parent=True, fullPath=0)

    #Need to remove duplicates and sort
    mmLocatorsInScene = list(set(mmLocatorsInScene))
    mmLocatorsInScene.sort()

    mmFootName = "_unfed_name_"

    for mmLocator in mmLocatorsInScene:
        mmListOfLocName = mmLocator.split("_")
        mmListOfLocNameLen = len(mmListOfLocName)

        if ( mmListOfLocNameLen > 6 ):
            mmTempNumber = mmListOfLocName[mmListOfLocNameLen-4]

            # print "mmLocator", mmLocator
            # print "mmListOfLocName[0]", mmListOfLocName[0]
            # print "mmListOfLocName[1]", mmListOfLocName[1]
            # print "mmListOfLocName", mmListOfLocName
            # print "mmListOfLocName[mmListOfLocNameLen-3]", mmListOfLocName[mmListOfLocNameLen-3]
            # print "mmPassedInLimbSet", mmPassedInLimbSet
            # print ""

            if ( mmListOfLocName[1] == "Foot" and mmListOfLocName[mmListOfLocNameLen-3] == "Locator" and mmListOfLocName[mmListOfLocNameLen-1] == mmPassedInLimbSet ):
                mmCurrentFootLocators[int(mmTempNumber)] = mmLocator

                mmFootName = mmListOfLocName[0]

                #Store names to use later
                mmCurrentFootBoneNamers[int(mmTempNumber)] = mmListOfLocName[0] + "_" + mmListOfLocName[1] + "_" + mmListOfLocName[2] + "_" + mmListOfLocName[3] + "_" + mmListOfLocName[5] + "_" + mmListOfLocName[6] + "_Bone"

            if ( len(mmListOfLocName) >= 4 and mmListOfLocName[1] == "Foot" and mmListOfLocName[mmListOfLocNameLen-1] == mmPassedInLimbSet ):
                #find current parent

                mmCurrentParent = cmds.listRelatives(mmLocator, p = 1)

                #? Doesn't matter if mmCurrentParent has a proper value? 
                if ( mmCurrentParent == None ):
                    cmds.parent( mmLocator, mmGroup_Foot_BuildLocator )

                elif ( mmCurrentParent != None and mmCurrentParent[0] != mmGroup_Foot_BuildLocator ):
                    cmds.parent( mmLocator, mmGroup_Foot_BuildLocator )

    #clear selection
    cmds.select( cl = 1)

    mmCurrentController = None
    
    #Select the proper foot control
    mmNameSplitter = mmCurrentFootBoneNamers[0].split("_")

    if (mmNameSplitter[0] == "left" or mmNameSplitter[0] == "Left" or mmNameSplitter[0] == "center" or mmNameSplitter[0] == "Center" ):

        #Need an angle multiplier for when things should be reversed
        mmAngleFlipper = 1
         
    elif ( mmNameSplitter[0] == "right" or mmNameSplitter[0] == "Right" ):
        
        #Need an angle multiplier for when things should be reversed
        mmAngleFlipper = -1

    #Need to find the locs and controls
    # print "mmCurrentFootLocators", mmCurrentFootLocators
    # mmCurrentFootLocators {0: u'left_Foot_Pivot_Rear_0_Locator_LimbSet_0', 1: u'left_Foot_Pivot_Ball_1_Locator_LimbSet_0', 2: u'left_Foot_Pivot_Front_2_Locator_LimbSet_0', 3: u'left_Foot_Pivot_Toe_3_Locator_LimbSet_0', 4: u'left_Foot_Pivot_Ankle_4_Locator_LimbSet_0', 5: u'left_Foot_Pivot_Original_5_Locator_LimbSet_0', 6: u'left_Foot_Pivot_Inner_6_Locator_LimbSet_0', 7: u'left_Foot_Pivot_Outer_7_Locator_LimbSet_0'}

    for mmKey, mmLocatorValue in mmCurrentFootLocators.items():

        cmds.select(cl = 1)

        mmChildList = cmds.listRelatives(mmLocatorValue, c = 1)
        mmChildListLen = len(mmChildList)

        if ( mmChildListLen > 0 ):

            for mmChild in mmChildList:

                mmChildLen = len(mmChild)
                if ( mmChild[0:12] == "ParentLocIs_" ):

                    #?  This seems wrong - they are 2 off from each other.. should be 1, right?
                    #?      Dunno.. seems to be working as is.
                    if ( mmFootName == "left" or mmFootName == "Left" ):
                        mmParentLoc = mmChild[16:mmChildLen]

                        mmCurrentParentLoc = "left" + mmParentLoc + "_loc"

                    if ( mmFootName == "right" or mmFootName == "Right"  ):
                        mmParentLoc = mmChild[18:mmChildLen]

                        mmCurrentParentLoc = "right" + mmParentLoc + "_loc"

                    if ( mmFootName == "center" or mmFootName == "Center"  ):
                        mmNameSplitter = mmChild.split("_")
                        mmParentLoc = mmNameSplitter[1]

                        mmCurrentParentLoc = mmParentLoc + "_loc"

                    mmCurrentFoot_Control = mmCurrentParentLoc.split("_")[0] + "_Control"
                    mmCurrentFootLoc = mmCurrentParentLoc

    cmds.select( mmCurrentFoot_Control )
    mmRelativeList = cmds.listRelatives( p = True )

    mmParentObject = mmRelativeList[0]


    ######################################
    #--Create bones on top of locators where they should be--
    #And place the Reverse Foot Rig Bones into their proper Heirarchy (at the same time)
    ######################################

    #Create a default value
    mmCounterInner = 0
    mmLastCreatedJoint = "bob"
    mmRevFTRigList = []

    for mmKey, mmEachLocator in mmCurrentFootLocators.items():

        mmNewJointName = ""
        
        mmSearchingForTrans = cmds.getAttr(mmCurrentFootLocators[mmCounterInner]+".translate")
        
        #Don't want to have joints made with parents if they are certain joints
        if ( mmCounterInner == 0 ):

            #deselect previously selected - to make sure another joint is not selected.
            cmds.select(cl = 1)
            mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
            
        elif ( mmCounterInner == 4 ):
            mmHeelBoneGroup = cmds.group( mmRevFTRigList[0] )

            mmHeelBoneGroup = cmds.rename( mmHeelBoneGroup, mmRevFTRigList[0] + "_Group_" + str(mmPassedInLimbSet) )
            cmds.parentConstraint( mmEachLocator, mmHeelBoneGroup, mo = 1 )

            #Store the object in a list for use later
            mmRevFTRigList.append(mmHeelBoneGroup)

            #Organize
            cmds.parent( mmHeelBoneGroup, mmGroup_Foot_Hidden )

        elif ( mmCounterInner == 5 ):
            mmInnerLocGroup = cmds.group( mmCurrentFootLocators[4] )
            mmInnerLocGroup = cmds.rename( mmInnerLocGroup, mmCurrentFootLocators[4] + "_Group_" + str(mmPassedInLimbSet) )
            cmds.parentConstraint( mmEachLocator, mmInnerLocGroup, mo = 1 )

            mmOuterLocGroup = cmds.group( mmCurrentFootLocators[5] )
            mmOuterLocGroup = cmds.rename( mmOuterLocGroup, mmCurrentFootLocators[5] + "_Group_" + str(mmPassedInLimbSet) )
            cmds.parentConstraint( mmCurrentFoot_Control, mmOuterLocGroup, mo = 1 )

            #Store the objects in a list for use later
            mmRevFTRigList.append(mmInnerLocGroup)
            mmRevFTRigList.append(mmOuterLocGroup)

            #Organize
            cmds.parent( mmInnerLocGroup, mmGroup_Foot_Hidden )
            cmds.parent( mmOuterLocGroup, mmGroup_Foot_Hidden )

        elif( mmCounterInner < 4 ):
            mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
            cmds.joint( mmLastCreatedJoint, e = True, zso = True, oj = "yzx", sao = 'yup' )
        
        if ( mmCounterInner < 4 ):
            #Rename Joint, but don't run this on iterate 4 & 5, because there are no joints

            mmNewJointName = mmCurrentFootBoneNamers[mmCounterInner] + "_RevFt_" + str(mmPassedInLimbSet)

            mmNewlyCreatedJoint = cmds.rename( mmNewlyCreatedJoint, mmNewJointName )
        
            mmLastCreatedJoint = mmNewlyCreatedJoint

            #Store the object in a list for use later
            mmRevFTRigList.append(mmNewlyCreatedJoint)


        mmCounterInner += 1

    mmDictOfRevFootLists["revFootList"] = mmRevFTRigList

    #deselect previously selected - to make sure parent joint is not selected.
    cmds.select(cl = 1)
    
    ######################################
    #--Create the Forward Foot Rig Bones--
    ######################################
    
    mmFWFTRigList = []
    
    mmBaseJoint = ""

    cmds.select(cl = 1)

    #Need to create a bone at the parent bone first instead of later.
    #deselect previously selected.
    mmSearchingForTrans2 = cmds.xform( mmParentObject, q = 1, t = 1, ws = 1 )

    mmNewlyCreatedParentJoint = cmds.joint( p = mmSearchingForTrans2 )
        
    mmNewlyCreatedParentJoint = cmds.rename( mmNewlyCreatedParentJoint, mmParentObject + "_FwFt_" + mmFootName + "_Bone_" + str(mmPassedInLimbSet) )
    
    mmTempParentConst = cmds.parentConstraint( mmParentObject, mmNewlyCreatedParentJoint, w=1.0, mo=0  )
    cmds.delete( mmTempParentConst )

    mmLastCreatedJoint = mmNewlyCreatedParentJoint

    mmBaseJoint = mmNewlyCreatedParentJoint

    #Set up the newly created joints to follow the parent bone passed in
    cmds.pointConstraint( mmParentObject, mmBaseJoint, mo = 0 )
    
    cmds.parent( mmBaseJoint, mmGroup_Foot_MainBone )


    #------------------------------------

    for mmCounterInner in (3, 2):
        mmSearchingForTrans = cmds.getAttr(mmCurrentFootLocators[mmCounterInner]+".translate")

        #Don't want to have joints made with parents if they are certain joints

        mmNewlyCreatedJoint = cmds.joint( p = mmSearchingForTrans[0] )
        cmds.joint( mmLastCreatedJoint, e = True, zso = True, oj = "yzx", sao = 'zup' )
        
        mmNewlyCreatedJoint = cmds.rename( mmNewlyCreatedJoint, mmCurrentFootBoneNamers[mmCounterInner] + "_FwFt_" + str(mmPassedInLimbSet) )

        #Store the joint in a list for use later
        mmFWFTRigList.append(mmNewlyCreatedJoint)
        
        mmLastCreatedJoint = mmNewlyCreatedJoint
    
    ######################################
    #Create IK handles across various bones and connect them as appropriate
    ######################################

    #Create measuring tool, dupe bone on top of mmBoneOnParent, then parent in locators, create IK and connect to measuring tool
    #create a distance node to find the space between upper joints
    mmStretch_distanceShapeNodeName = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmFWFTRigList[0]+"_distanceNode#")
    
    #create locators
    mmStretch_firstLocator = cmds.spaceLocator( p = [0,0,0], n = mmFWFTRigList[0]+"_parentLocator#")
    mmStretch_secondLocator = cmds.spaceLocator( p = [0,0,0], n = mmFWFTRigList[0]+"_childLocator#")
    
    cmds.parent( mmStretch_firstLocator, mmGroup_Foot_Hidden )
    cmds.parent( mmStretch_secondLocator, mmGroup_Foot_Hidden )
    
    #attach locators to distance node
    cmds.connectAttr( mmStretch_firstLocator[0]+".translate", mmStretch_distanceShapeNodeName+".point1")
    cmds.connectAttr( mmStretch_secondLocator[0]+".translate", mmStretch_distanceShapeNodeName+".point2")
    
    #move locators to selected joint and its first child
    cmds.pointConstraint( mmParentObject, mmStretch_firstLocator, mo = 0)
    
    cmds.pointConstraint( mmRevFTRigList[3], mmStretch_secondLocator, mo = 0)
    
    #mmNewlyCreatedChildJoint = cmds.joint( p = mmSearchingForTransChild[0] )
    #instead of creating a new joint, lets try using the base fw rig joint
    mmNewlyCreatedChildJoint =  mmFWFTRigList[0]
    
    # All "sc"'s were converted to "rp"'s because of some unexplicable issue with ogre feet.
    #   Switching them to RP even though they are only single joint chains somehow works.
    #   Leaving unless it breaks other stuff, then can switch back.
    mmDistanceIKHandleName = mmRF.mmCreateIKHandle( mmNewlyCreatedParentJoint, mmNewlyCreatedChildJoint, "rp" )
    
    #Need to connect the ChildBone's length to the distance of the measuring tool
    cmds.connectAttr( mmStretch_distanceShapeNodeName + ".distance", mmNewlyCreatedChildJoint + ".translateY" )

    #Need to parent constrain the IK handle to the Reverse Foot Rig so it moves around properly
    cmds.parentConstraint( mmRevFTRigList[3], mmDistanceIKHandleName, mo = 1 )
    
    cmds.parent ( mmDistanceIKHandleName, mmGroup_Foot_Hidden )
    
    #Creating IK handles on Forward Foot Rig
    # All "sc"'s were converted to "rp"'s because of some unexplicable issue with ogre feet.
    #   Switching them to RP even though they are only single joint chains somehow works.
    #   Leaving unless it breaks other stuff, then can switch back.
    mmForwardFootIKHandleName = mmRF.mmCreateIKHandle( mmFWFTRigList[0], mmFWFTRigList[1], "rp" )

    #Parent IK handles into reverse foot rig
    cmds.parent( mmForwardFootIKHandleName, mmRevFTRigList[2] )

    mmDictOfRevFootLists["forFootList"] = mmFWFTRigList

    mmDictOfRevFootLists["distSystem"] = [ mmStretch_distanceShapeNodeName, mmStretch_firstLocator, mmStretch_secondLocator, mmDistanceIKHandleName ]
    mmDictOfRevFootLists["ikHandle"] = [ mmForwardFootIKHandleName ]
    

    ######################################
    
    #Creating reverse foot attributes needed
    cmds.select( mmCurrentFoot_Control )

    #Add false attribute to separate from other things
    cmds.addAttr( longName = "Foot_Controls", attributeType = "enum", en = "---------------:", k = 1)
    cmds.setAttr( mmCurrentFoot_Control + ".Foot_Controls", e = 1, l = 1)

    cmds.addAttr( longName="FootRoll", attributeType='double', min = -20, max = 20, dv=0, k = 1 )
    mmFootRollAttr = mmCurrentFoot_Control + ".FootRoll"
    
    cmds.addAttr( longName="FootBank", attributeType='double', min = -20, max = 20, dv=0, k = 1 )
    mmFootBankAttr = mmCurrentFoot_Control + ".FootBank"
    
    cmds.addAttr( longName="ToeSwivel", attributeType='double', min = -20, max = 20, dv=0, k = 1 )
    mmToeSwivelAttr = mmCurrentFoot_Control + ".ToeSwivel"
    
    cmds.select( cl = 1 )

    ######################################
    #Create Set Driven Keys for various values
    ######################################
    
    '''
    Foot_Pivot_Rear_0_Locator_0
    Foot_Pivot_Ball_1_Locator_0
    Foot_Pivot_Front_2_Locator_0
    Foot_Pivot_Original_3_Locator_0
    Foot_Pivot_Inner_4_Locator_0
    Foot_Pivot_Outer_5_Locator_0
    '''

    '''Connect the Foot Roll to the Heel and Toe both rotating up to 180 degrees, also toe roll'''
    mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-20, -10, 10, 20], [180, 90, 0, 0], 1 )
    mmRF.mmCreateSDK( mmFootRollAttr, mmRevFTRigList[2], ".rotateX",  [-20, -10, 10, 20], [0, 0, 90, 180], 1 )

    '''Connect the Foot Bank to the Inner and Outer Locators'''
    mmRF.mmCreateSDK( mmFootBankAttr, mmCurrentFootLocators[4], ".rotateZ", [0, 10, 20], [0, 90, 180], mmAngleFlipper )
    mmRF.mmCreateSDK( mmFootBankAttr, mmCurrentFootLocators[5], ".rotateZ", [-20, -10, 0], [-180, -90, 0], mmAngleFlipper )

    '''Connect the Toe Swivel to the Toe Swivel Locator'''
    mmRF.mmCreateSDK( mmToeSwivelAttr, mmRevFTRigList[1], ".rotateZ", [-20, -10, 10, 20], [-180, -90, 90, 180], 1 )
    
    cmds.select( cl =1 )
    
    #Need to parent in the foot so it moves appropriately
    cmds.select( mmCurrentFootLoc )
    mmRelativeList = cmds.listRelatives(  )

    #First find old parentconstraint and delete it
    for mmRelative in mmRelativeList:
        mmRelativeChecker = mmRelative.split("_")

        for mmRelativeName in mmRelativeChecker:

            if ( mmRelativeName[0:6] == "parent" ):
                cmds.select( mmRelative )
                cmds.delete()

    #Then give it a new constraint
    print "mmFWFTRigList[0]", mmFWFTRigList[0]

    print "mmCurrentFootLoc", mmCurrentFootLoc

    cmds.parentConstraint( mmFWFTRigList[0], mmCurrentFootLoc, mo = 1)
    
    mmDictOfRevFootLists["footParentLoc"] = [mmCurrentParentLoc]

    if ( mmFootName != "center" and mmFootName != "Center" ):
        mmDictOfRevFootLists["footMesh"] = [mmFootName + mmParentLoc]
    else:
        mmDictOfRevFootLists["footMesh"] = [mmParentLoc]

    mmDictOfRevFootLists["footControl"] = [mmCurrentFoot_Control]


    #This return now passes pertinent information back to mmCreateLimbActual.
    return mmDictOfRevFootLists

'''
This Function searches for identifiers named 'limb' and creates whatever limb system was specified before in the primer script.
'''
def mmCreateLimbActual( *args ):
    
    #Verify that groups are created
    mmCreateRigGroups()

    '''
    #Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''

    '''
    Actual Limb Creation:

    Gathers all identifier tags in the scene
    Find out how many limbs there are
        Store instead the objects they are on, then delete the tags.
    Gather all locators of the 'trash' name as a location to create bones or controls
    '''

    #Grab all tranforms in scene
    mmAllTransformsInScene = cmds.ls(type = "transform")
    mmAllLimbSetsInSceneDict = {}
    mmCurrentLimbSetDict = {}
    mmTrashNameList = []
    # mmFootBool = False

    mmCurrentHighestCount = -1

    #Find the "identifier" tags if they exist (they may not), and save out how many sets we have
    for mmTransform in mmAllTransformsInScene:

        mmSplitWordsFound = mmTransform.split("_")
        if ( mmSplitWordsFound[0] == "identifier" and mmSplitWordsFound[1] == "limb" ):

            if ( int(mmSplitWordsFound[3]) > mmCurrentHighestCount ):
                mmCurrentHighestCount = int(mmSplitWordsFound[3])

            #Need to use any existing data if there is any.
            mmSetNumber = int(mmSplitWordsFound[3])

            if mmSetNumber in mmAllLimbSetsInSceneDict:
                mmCurrentLimbSetDict = mmAllLimbSetsInSceneDict[int(mmSplitWordsFound[3])]
            else:
                mmCurrentLimbSetDict = {}

                #Trying to save a unique footBool per set
                mmCurrentLimbSetDict["footBool"] = False

            #Find the parent of the identifier
            mmIdentifierObject = cmds.listRelatives( mmTransform, p = 1 )[0]

            #Convert selection from the mesh or locator to its coresponding control - or if its a trash locator, keep it.
            #Grab "trash" name locators to remember to remove them in a bit

            #Find the other child - trying to find out if this was a mesh or not.
            mmIdentifierObjectsChildren = cmds.listRelatives( mmIdentifierObject, c = 1 )

            for mmChild in mmIdentifierObjectsChildren:
                #If the child is not identifier transform and is of type "mesh", then we want the control
                if ( mmChild != mmTransform and cmds.objectType(mmChild) == "mesh" ):
                    mmIdentifierObject = mmIdentifierObject + "_Control"
                #Else it is a trash locator.. and then what do we want?  Just itself?
                else:
                    mmIdentifierObject = mmIdentifierObject

            #Grab trash locators if they are being used
            mmNameChecker = mmIdentifierObject.split("_")
            if ( len(mmNameChecker) > 2 and mmNameChecker[2] == "trash" ):
                mmTrashNameList.append(mmIdentifierObject)

            #If its a toe, foot, or limb piece, then save it out in the proper container
            if ( len(mmSplitWordsFound) > 5 and mmSplitWordsFound[5] == "toe" ):
                mmCurrentLimbSetDict["toe"] = mmIdentifierObject

            elif ( len(mmSplitWordsFound) > 5 and mmSplitWordsFound[5] == "foot" ):
                mmCurrentLimbSetDict["foot"] = mmIdentifierObject
                mmCurrentLimbSetDict["footBool"] = True

            elif ( len(mmSplitWordsFound) > 5 and mmSplitWordsFound[5] == "limbPiece" ):
                mmCurrentLimbSetDict[int(mmSplitWordsFound[6])] = mmIdentifierObject

            mmAllLimbSetsInSceneDict[int(mmSplitWordsFound[3])] = mmCurrentLimbSetDict

            #Then delete the identifier because we have all the information we need.
            cmds.delete(mmTransform)

    #Need to Organize!
    #Create groups to store stuff away
    mmGroup_Limb_Hidden = cmds.group( em = True, n = "_Group_Limb_Hidden" )    
    cmds.parent(mmGroup_Limb_Hidden, mmGroup_Hidden)

    # print "mmAllLimbSetsInSceneDict", mmAllLimbSetsInSceneDict

    #This for loop goes through each limb set
    for mmSetKey, mmLimbSetDictValue in mmAllLimbSetsInSceneDict.items():
        #mmSetKey should be an int of set created, starting with 0? (we think so.)

        mmFootBool = mmLimbSetDictValue["footBool"]
        mmToePiece = None

        mmCounterMax = 0

        #This for loop goes through a limb and pulls out the different pieces it is made up of.
        for mmLimbPieceKey, mmLimbPieceValue in mmLimbSetDictValue.items():

            if (mmLimbPieceKey == "toe"):
                # print "mmC3MRTMR.mmCreateLimbActual found a toe, but toes are not currently supported."
                #?  We do not currently support generic rigs with toes - something we need to do.. eventually.
                # print "mmC3MRTMR.mmCreateLimbActual found a toe, attempting to implement"

                mmToePiece = mmLimbPieceValue

            # elif (mmLimbPieceKey == "foot"):
            #     # No reason to look for this atm, this for loop is only counting how many limb pieces there are - whether or not there is a foot doesn't matter.
            #     print "we found a foot"

            elif (type(mmLimbPieceKey) == type(int(10))):
                #print "we found a regular limb piece"
                if ( mmLimbPieceKey > mmCounterMax ):
                    #This is the max number of limb pieces
                    mmCounterMax = mmLimbPieceKey

        cmds.select(cl = 1)


        if (mmFootBool):
            #Need to space switch the feet between the root and their current parent - current parent control.
            #Find the foot control's parent
            mmFootControlParent = cmds.listRelatives(mmLimbSetDictValue["foot"], p = 1)[0]

            #Verify that the foot control's parent is not a pad
            mmIsFootChildOfLeg = False

            mmNameSplitter = mmFootControlParent.split("_")

            #Split the name apart and if 'pad' is one of the words, then find the next parent and do this over again.
            for mmName in mmNameSplitter:
                if ( mmName[0:3] == "pad" ):

                    #If this is a pad, find out if there is a constraint of some sort, if yes, find out what that constraint is to, and use that
                    mmTargetList = None
                    mmConstraintType = None
                    mmConstraintType2 = None

                    mmTargetList, mmConstraintType = mmFindConstraint(mmFootControlParent)

                    if ( mmTargetList != None and len(mmTargetList) > 0 ):
                        mmFootControlParent = mmTargetList[0]

                        mmExtraNameChecker = mmFootControlParent.split("_")

                        for mmExtraName in mmExtraNameChecker:
                            if(  mmExtraName == "PlaceHolder" ):

                                mmNameFinder, mmConstraintType2 = mmFindConstraint(mmFootControlParent)
                                mmNameSplitter = mmNameFinder[0].split("_")

            if ( mmFootControlParent != "root_Control" ):

                for mmLimbPieceKey, mmLimbPieceValue in mmLimbSetDictValue.items():

                    if (mmLimbPieceValue == mmFootControlParent):
                        mmIsFootChildOfLeg = True

                if (not mmIsFootChildOfLeg or mmCounterMax == 1):
                    mmFootControlPad = mmOF.mmGroupInPlace(mmLimbSetDictValue["foot"])

                    mmRF.spaceSwitcherMulti( 3, mmLimbSetDictValue["foot"], [mmFootControlPad], [mmFootControlParent, "root_Control"], True, mmNameSplitter[0] + "to_root")
                else:
                    cmds.parent( mmLimbSetDictValue["foot"],"root_Control" )

                cmds.select(mmLimbSetDictValue["foot"])
                cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

        #If there are more bones than just the foot selected.
        #   TODO: Think there are major issues if counter max > 3(?)
        if (mmCounterMax > 1):
            # print "working on limb"

            mmLastBone = ""
            mmCounter = mmCounterMax
            mmBoneCollector = []

            #For every mmCounter, we have the selection of our bones in reverse order
            #Create a reverse for loop that counts down through the mmLimbSetDictValue and creates a new bone at each location
            while ( mmCounter >= 0 ):

                #Find the xform of the object we have
                if ( mmCounter == 0):
                    if ( mmFootBool):
                        mmBoneValue = "foot"
                    else:
                        mmBoneValue = mmCounter + 1
                        print "mmC3MRTMR.mmCreateLimbActual may have been given unsupported information."
                        print "User is trying to create a limb without a foot."

                else:
                    mmBoneValue = mmCounter

                cmds.select(mmLimbSetDictValue[mmBoneValue])

                mmTransformWeWant = cmds.xform( q = 1, pivots = 1, ws = 1)

                #If there was a bone previously made, select it so we make a child
                if ( mmLastBone != "" ):
                    cmds.select(mmLastBone)
                else:
                    cmds.select(cl = 1)

                #Create a bone at the point we want
                mmLastBone = cmds.joint( p = (mmTransformWeWant[0],mmTransformWeWant[1],mmTransformWeWant[2]), n = mmLimbSetDictValue[mmBoneValue] + "_bone#" )
                mmBoneCollector.append(mmLastBone)

                mmCounter -= 1

            #Need to color the new controllers to match the original controller color
            if mmFootBool:
                mmDesiredColor = mmOF.mmGetColor(mmLimbSetDictValue["foot"])
            else:
                mmDesiredColor = mmOF.mmGetColor(mmLimbSetDictValue[1])

            #Creating a text label
            mmIKFKSwitchControl = mmOF.createTextBox( "IK/FK", None, [0,0,0], [1,1,1], [1,1,1], "box" )

            mmTrashPC = cmds.pointConstraint(mmLimbSetDictValue[mmCounterMax], mmIKFKSwitchControl, mo = 0)
            cmds.delete(mmTrashPC)
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
            mmOF.changeColor(mmDesiredColor)
            mmNameSplitter = mmLimbSetDictValue[mmCounterMax].split("_")
            mmIKFKSwitchControl = cmds.rename( mmIKFKSwitchControl, mmNameSplitter[0] + "_ikfkSwitch_Control" )

            #Add visibility swap of original controls to the ik/fk switch control - that way we don't have extra stuff in the way if we don't want it.
            cmds.addAttr(mmIKFKSwitchControl, ln = "Rig_Attributes", at ="enum", en = "------:", dv=0, k=1)
            cmds.setAttr((mmIKFKSwitchControl + ".Rig_Attributes"), l=1)
            
            cmds.addAttr(mmIKFKSwitchControl, ln = "Manual_Control_Vis", at ="enum", en = "off:on:", dv=0, k=1)

            #Create an SDK that controls the vis swap
            mmRF.mmCreateSDK( mmIKFKSwitchControl + ".Manual_Control_Vis", mmLimbSetDictValue[mmCounterMax], ".visibility",  [0, 1], [0, 1], 1 )
            cmds.setAttr((mmLimbSetDictValue[mmCounterMax] + ".visibility"), k=0)

            #?  Should we lock this control's info at some point?  Because the user shouldn't move it - but not now because the rig builder might want to move it.
            #?      Why not lock it now?  The user can always manipulate the CV curve.. that's what you would want to do anyway.

            #Need to call IK/FK Switch script with proper selection
            #Call it on mmIKFKSwitchControl and mmBoneCollector[0]
            cmds.select(cl = 1)
            if (mmFootBool):
                #Add 1 for counting the foot bone
                mmDictOfIKFKSwitchLists = mmRF.autoIKFK(mmCounterMax + 1, [mmIKFKSwitchControl, mmBoneCollector[0]], mmLimbSetDictValue["foot"])
            else:
                #Else there is no foot icon premade, and just make one from scratch
                mmDictOfIKFKSwitchLists = mmRF.autoIKFK(mmCounterMax, [mmIKFKSwitchControl, mmBoneCollector[0]], None)

                #?  We need to set the IKFKSwitch to FK by default - because this is a tail.

            #autoIKFK returns mmDictOfIKFKSwitchLists with information of:
            #{
            #   "bindBone":         [ BindBone0, 1, 2, etc. ],
            #   "ikBone":           [ IKBone0, 1, 2, etc. ],
            #   "fkBone":           [ FKBone0, 1, 2, etc. ],
            #   "ikIcon":           [ IKIcon, IKHandle, IKHandleConstraint ],
            #   "fkIcon":           [
            #                           [ FKIcon, FKIconPad1, FKIconPad2 ],
            #                           [ FKIcon2, FKIcon2Pad1, FKIcon2Pad2 ],
            #                           [... for however many FKIcons there are]
            #                       ],
            #   "poleVector":       [mmPoleVector]
            #   "baseIcon":         [mmLimbBaseControl]
            #   "distanceSystem":   [mmStretchLocator, mmStretchLocatorPointConstraint]
            #   "fkikSwitch":       [ IKFKSwitchControl ],
            #   "orgFolder":        [ Organization Folder ]
            #}

            #Need to move all the FK icons into the control group so they aren't hidden with the rest of the information.
            mmFKControlGroup = cmds.group(em = 1, n = "fkControl_Group_#")
            for mmFKIconList in mmDictOfIKFKSwitchLists["fkIcon"]:
                cmds.parent( mmFKIconList[2], mmFKControlGroup )
            cmds.parent(mmFKControlGroup, mmGroup_ExtraControls)

            #Need to make the newly created controllers large enough to be seen outside whatever meshes they were created for.
            mmCounterInner = 0

            #Our FK Controls are coming in in the wrong order - must reverse before processing.
            mmWorkingListOfFKControls = []
            mmFinalDictOfFKControls = {}

            for v in mmDictOfIKFKSwitchLists["fkIcon"]:
                mmWorkingListOfFKControls.append(v)

            mmWorkingListOfFKControls = list(reversed(mmWorkingListOfFKControls))

            mmCounterExtra = 1
            for v in mmWorkingListOfFKControls:
                mmFinalDictOfFKControls[mmCounterExtra] = v
                mmCounterExtra += 1

            #IK doesn't need it, so jump to FK Controls:
            for mmLimbPieceKey, mmLimbPieceValue in mmLimbSetDictValue.items():

                if (type(mmLimbPieceKey) == type(int(10))):

                    mmNameChecker = mmLimbPieceValue.split("_")

                    if ( len(mmNameChecker) > 0 and mmNameChecker[1] == "identifier" ):
                        #Create a cube to get a standard value of ones, then delete it
                        mmTrashCube = mmOF.createCube()
                        mmCurrentBB = mmRF.mmGrabBoundingBoxInfo([mmTrashCube])
                        cmds.delete(mmTrashCube)

                    else:
                        mmMeshToCheck = mmNameChecker[0]
                        mmCurrentBB = mmRF.mmGrabBoundingBoxInfo([mmMeshToCheck])

                    #? Issue when we don't want to create a foot, there aren't enough FX icons to match up, we need to account for this.
                    for mmFKControlKey, mmFKControlKeyValue in mmFinalDictOfFKControls.items():
                        mmNameChecker = mmFKControlKeyValue[0].split("_")
                        mmNameToCheck = mmNameChecker[1] + "_" + mmNameChecker[2]
                        if ( mmNameToCheck == mmLimbPieceKey ):

                            cmds.select(mmFinalDictOfFKControls[mmLimbPieceKey][0])
                            cmds.scale(mmCurrentBB["total"][0]*1.25, mmCurrentBB["total"][0]*1.25, mmCurrentBB["total"][0]*1.25)
                            mmOF.changeColor(mmDesiredColor)

                            #Freeze Scale Values
                            cmds.makeIdentity( apply = True, t = 0 , r = 0 , s = 1 , n = 0, pn = 1)

                    mmCounterInner += 1

                    #if this is the last pass, adjust the 'ikfk switch control' scale to match the smallest value of the limb start
                    #   This is the base control for the limb
                    if (mmLimbPieceKey == mmCounterMax):

                        cmds.select(mmIKFKSwitchControl)

                        cmds.scale(mmCurrentBB["total"][0]*1.25, mmCurrentBB["total"][0]*1.25, mmCurrentBB["total"][2]*1.25)
                        mmOF.changeColor(mmDesiredColor)

                        #Freeze Scale Values
                        cmds.makeIdentity( apply = True, t = 0 , r = 0 , s = 1 , n = 0, pn = 1)

            #Adjust Pole Vector as well
            if (mmDictOfIKFKSwitchLists["poleVector"] != []):
                cmds.select(mmDictOfIKFKSwitchLists["poleVector"][0])
                mmOF.changeColor(mmDesiredColor)

                #Freeze Trans/Rot/Scale Values
                cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)


            #Parent the bones to the ik/fk switch
            cmds.pointConstraint( mmIKFKSwitchControl, mmDictOfIKFKSwitchLists["bindBone"][0] )

            #For each limb bone
            #Grab the control, group in place, then constrain the group to the bone
            mmCounter = mmCounterMax
            mmParentToStore = ""

            #This constrains each mmLimbPiecePad to the bind bone
            for mmLimbPieceKey, mmLimbPieceValue in mmLimbSetDictValue.items():
                if ( mmLimbPieceKey != "foot" and mmLimbPieceKey != "toe" and mmLimbPieceKey != "footBool" ):
                    if ( mmLimbPieceKey == mmCounterMax ):
                        mmParentToStore = cmds.listRelatives(mmLimbPieceValue, p = 1)

                    mmLimbPiecePad = mmOF.mmGroupInPlace(mmLimbPieceValue)

                    cmds.parentConstraint( "bind_" + mmBoneCollector[mmCounter], mmLimbPiecePad, mo = 1)
                    # raise RuntimeError('# Problem is here #')

                mmCounter -= 1

            # raise RuntimeError('# just before point constraint #')

            #Need to constrain the ik fk switch box to whatever the original parent of the first mmLimbPiecePad was.

            mmBoneCollectorPad = mmOF.mmGroupInPlace(mmIKFKSwitchControl)

            cmds.parentConstraint( mmParentToStore, mmBoneCollectorPad, mo = 1 )

            cmds.parent(mmBoneCollectorPad, "root_Control")

            #Put IKFKSwitch stuff into the proper folder structures
            cmds.parent(mmDictOfIKFKSwitchLists["orgFolder"], mmGroup_Limb_Hidden)

            #Make it so the mmIKFKSwitchControl can space switch between its parent and world
            mmIKFKSwitchControlPad = mmOF.mmGroupInPlace(mmIKFKSwitchControl)

            mmIKFKSwitchControlAttr = mmRF.spaceSwitcherMulti( 3, mmIKFKSwitchControl, [mmIKFKSwitchControlPad], [ mmBoneCollectorPad, "root_Control" ], True, "ParentToWorld" )

        #If there is only one other limb piece besides the foot.
        #   Generally we don't want this situation, but we should address it somehow.
        elif (mmCounterMax == 1):
            print "WIP - you have found unfinished code in mmConvert3DSMaxRigToMayaRig, and now likely everything is broken... Sorry."
            print "You should probably be using a trash limb locator as a 'knee' or you are trying to add a toe and something is breaking."

        #Run revfootrig function
        if (mmFootBool):
            
            if mmToePiece != None:
                # THIS IS BAD - the feet of a generic rig MUST gain the mmDictOfRevFootLists of the mmCreateRevFootRigNoToe, or else everything breaks.
                if mmLimbPieceValue[0:4] == "left":
                    mmCurrentFootSide = "left"
                elif mmLimbPieceValue[0:4] == "righ":
                    mmCurrentFootSide = "right"
                elif mmLimbPieceValue[0:4] == "cent":
                    mmCurrentFootSide = "center"
                else :
                    mmCurrentFootSide = None

                mmCurrentFootLoc = mmLimbSetDictValue["foot"].split("_")[0] + "_loc"

                mmDictOfRevFootLists = mmCreateIndividualRevFootRig( mmCurrentFootLoc, mmCurrentFootSide )

            else:
                #Pass in the Set number which we are currently working on.
                #   This Set number _should_ always be correct.
                mmDictOfRevFootLists = mmCreateRevFootRigNoToe(mmSetKey)

            #mmCreateRevFootRigNoToe returns mmDictOfRevFootLists with information of:
            #{
            #   "revFootList":      [ Reverse Foot Bone0, 1, 2, etc ],
            #   "forFootList":      [ Forward Foot Bone0, 1, 2, etc ],
            #   "distSystem":       [ mmStretch_distanceShapeNodeName, mmStretch_firstLocator, mmStretch_secondLocator, mmDistanceIKHandleName ],
            #   "ikHandle":         [ mmForwardFootIKHandleName ],
            #   "footParentLoc":    [ mmFootLoc ],
            #   "footMesh":         [ mmFootMesh ],
            #   "footControl":      [mmCurrentFoot_Control]
            #}

            #If there are limb pieces (mmCounterMax is tracking the number of limb pieces)
            if (mmCounterMax > 1):
                mmMergeLimbAndFootPieces(mmDictOfIKFKSwitchLists, mmDictOfRevFootLists, mmFKControlGroup)

            # #Need to move all the FK icons into the control group so they aren't hidden with the rest of the information.
            # for mmFKIconList in mmDictOfIKFKSwitchLists["fkIcon"]:
            #     cmds.parent( mmFKIconList[2], mmGroup_ExtraControls )

        #-----------------------------------------------------------------

        if (mmCounterMax > 1):
            #Need to create an autonomous pole vector system to help with animating the legs
            mmLocToCheck = ""

            if len( mmLimbSetDictValue ) > 1:
                mmNameChecker = mmLimbSetDictValue[len(mmLimbSetDictValue)-2].split("_")
                
                if ( len(mmNameChecker) > 0 and mmNameChecker[1] == "Control" ):
                    mmLocToCheck = mmNameChecker[0] + "_loc"

                if ( mmLocToCheck != "" ):
                    mmLegParent = cmds.listRelatives(mmLocToCheck, p = 1)[0]

                    mmNameChecker = mmLegParent.split("_")
                    if ( len(mmNameChecker) > 0 and mmNameChecker[1] == "loc" ):
                        mmLegParent = mmNameChecker[0] + "_Control"

                    # print "mmLegParent", mmLegParent
                    mmAutoPVSystemList = mmRF.mmAutonomousPoleVectorSystem( mmDictOfIKFKSwitchLists["ikBone"], mmDictOfIKFKSwitchLists["ikIcon"][1], mmDictOfIKFKSwitchLists["poleVector"][0], mmLegParent, mmDictOfIKFKSwitchLists["ikIcon"][0] )

                    cmds.parent(mmAutoPVSystemList[len(mmAutoPVSystemList)-2], mmGroup_ExtraControls)
                    cmds.parent(mmAutoPVSystemList[len(mmAutoPVSystemList)-1], mmGroup_Hidden)

        print "past 1 loop of mmC3MRTMR.mmCreateLimbActual"

    #-----------------------------------------------------------------

    for mmTrashObj in mmTrashNameList:
        mmTrashObjParent = cmds.listRelatives(mmTrashObj, p = 1)[0]
        if (mmTrashObjParent != []):
            cmds.delete(mmTrashObjParent)
        else:
            cmds.delete(mmTrashObj)

    return None

'''
This Function takes an input object, finds its children, then finds if one of those children is a constraint,
    and then returns the list of targets and a number for what type of constraint it is.
'''
def mmFindConstraint( mmInputObject = None, *args ):

    mmTargetList = ""
    mmConstraintType = None

    mmFootControlParentsChildren = cmds.listRelatives(mmInputObject, c = 1)
    if ( mmFootControlParentsChildren and len(mmFootControlParentsChildren) >= 1 ):
        for mmChild in mmFootControlParentsChildren:

            if ( mmChild == None ):
                print "mmC3MRTM.mmFindConstraint was given improper information to proceed."
                return None

            mmNameChecker = mmChild.split("_")
            
            for mmChildName in mmNameChecker:
                if ( mmChildName[0:15] == "pointConstraint" ):
                    mmTargetList = cmds.pointConstraint(mmChild, q = 1, tl = 1)
                    mmConstraintType = 0
                if ( mmChildName[0:16] == "orientConstraint" ):
                    mmTargetList = cmds.orientConstraint(mmChild, q = 1, tl = 1)
                    mmConstraintType = 1
                if ( mmChildName[0:16] == "parentConstraint" ):
                    mmTargetList = cmds.parentConstraint(mmChild, q = 1, tl = 1)
                    mmConstraintType = 2
                if ( mmChildName[0:15] == "scaleConstraint" ):
                    mmTargetList = cmds.pointConstraint(mmChild, q = 1, tl = 1)
                    mmConstraintType = 3
                if ( mmChildName[0:13] == "aimConstraint" ):
                    mmTargetList = cmds.pointConstraint(mmChild, q = 1, tl = 1)
                    mmConstraintType = 4

    return mmTargetList, mmConstraintType

'''
This Function takes all of the information from the scripts ikfkScript and the mmCreateRevFootRigNoToe and merges them so the foot now functions 
'''
def mmMergeLimbAndFootPieces( mmDictOfIKFKSwitchLists = {}, mmDictOfRevFootLists = [], mmFootControlGroup = None, *args ):

    #Verify that groups are created
    mmCreateRigGroups()

    '''
    #Available groups:
    mmGroup_Hidden
    mmGroup_MainBones
    mmGroup_Controls
    mmGroup_ExtraControls
    mmGroup_BuildLocator
    mmGroup_Geo
    mmGroup_ExportLocator
    mmGroup_ExtraObject

    '''

    #autoIKFK returns mmDictOfIKFKSwitchLists with information of:
    #{
    #   "bindBone":         [ BindBone0, 1, 2, etc. ],
    #   "ikBone":           [ IKBone0, 1, 2, etc. ],
    #   "fkBone":           [ FKBone0, 1, 2, etc. ],
    #   "ikIcon":           [ IKIcon, IKHandle, IKHandleConstraint ],
    #   "fkIcon":           [
    #                           [ FKIcon, FKIconPad1, FKIconPad2 ],
    #                           [ FKIcon2, FKIcon2Pad1, FKIcon2Pad2 ],
    #                           [... for however many FKIcons there are]
    #                       ],
    #   "distanceSystem":   [mmStretchLocator, mmStretchLocatorPointConstraint]
    #   "fkikSwitch":       [ IKFKSwitchControl ],
    #   "orgFolder":        [ Organization Folder ]
    #}

    #mmCreateRevFootRigNoToe returns mmDictOfRevFootLists with information of:
    #{
    #   "revFootList":  [ Reverse Foot Bone0, 1, 2, etc ],
    #   "forFootList":  [ Forward Foot Bone0, 1, 2, etc ],
    #   "distSystem":  [ mmStretch_distanceShapeNodeName, mmStretch_firstLocator, mmStretch_secondLocator, mmDistanceIKHandleName ],
    #   "ikHandle":  [ mmForwardFootIKHandleName ],
    #   "footParentLoc":  [ mmFootLoc ],
    #   "footMesh":  [ mmFootMesh ]
    #}

    #Find the ikfkSwitchController
    nurbsCurveAttr = mmDictOfIKFKSwitchLists["fkikSwitch"][0] + ".ik_fk_switch"

    #Remove old ikHandle constraint for the limb, and create a new one on the reverse foot
    cmds.delete(mmDictOfIKFKSwitchLists["ikIcon"][2])

    for mmObject in mmDictOfRevFootLists["revFootList"]:
        mmNameChecker = mmObject.split("_")
        for mmName in mmNameChecker:
            if ( mmName == "Original" ):
                mmRevFootOriginalJoint = mmObject
    cmds.pointConstraint( mmRevFootOriginalJoint, mmDictOfIKFKSwitchLists["ikIcon"][1], mo = 1)

    #The distance system needs to be deleted (determines how far away the foot is from the parent bone)
    for mmObject in mmDictOfRevFootLists["distSystem"]:
        cmds.delete(mmObject)

    #Reparent the first forward foot bone to its parent's parent, then delete the first parent bone
    mmForwardFootParent = cmds.listRelatives(mmDictOfRevFootLists["forFootList"][0], p = 1)[0]
    mmForwardFootParentsGroup = cmds.listRelatives(mmForwardFootParent, p = 1)
    cmds.parent( mmDictOfRevFootLists["forFootList"][0], mmForwardFootParentsGroup )
    cmds.delete(mmForwardFootParent)
    
    #Duplicate the forward foot bone twice and delete any "effector#"s that tagged along
    mmIKJointChain = mmDictOfRevFootLists["forFootList"]
    mmFKJointChain = cmds.duplicate(mmDictOfRevFootLists["forFootList"][0], n = "fk_" + mmDictOfRevFootLists["forFootList"][0], rc = 1 )

    for mmIterate, mmJoint in enumerate(mmFKJointChain):

        if (mmJoint[0:8] == "effector"):
            cmds.delete(mmJoint)
            mmFKJointChain.remove(mmJoint)
        else:
            mmNameChecker = mmJoint.split("_")
            if ( mmNameChecker[0] != "fk" ):
                mmFKJointChain[mmIterate] = cmds.rename(mmJoint, "fk_" + mmJoint)

    cmds.select(mmIKJointChain[0])
    mmBindJointChain = cmds.duplicate(mmDictOfRevFootLists["forFootList"][0], n = "bind_" + mmDictOfRevFootLists["forFootList"][0], rc = 1 )

    for mmIterate, mmJoint in enumerate(mmBindJointChain):

        if (mmJoint[0:8] == "effector"):
            cmds.delete(mmJoint)
            mmBindJointChain.remove(mmJoint)
        else:
            mmNameChecker = mmJoint.split("_")
            if ( mmNameChecker[0] != "bind" ):
                mmBindJointChain[mmIterate] = cmds.rename(mmJoint, "bind_" + mmJoint)

    for mmIterate, mmJoint in enumerate(mmIKJointChain):
        mmIKJointChain[mmIterate] = cmds.rename(mmJoint, "ik_" + mmJoint)

    #---------------------------------------------------------

    mmFKPad = mmOF.mmGroupInPlace( mmFKJointChain[0], "_pad#" )
    mmIKPad = mmOF.mmGroupInPlace( mmIKJointChain[0], "_pad#" )
    mmBindPad = mmOF.mmGroupInPlace( mmBindJointChain[0], "_pad#" )

    #Point constrain the first ik and fk bones to the first bind bone
    cmds.parentConstraint(mmDictOfIKFKSwitchLists["ikBone"][len(mmDictOfIKFKSwitchLists["ikBone"])-1], mmIKPad, mo = 1 )
    cmds.parentConstraint(mmDictOfIKFKSwitchLists["fkBone"][len(mmDictOfIKFKSwitchLists["fkBone"])-1], mmFKPad, mo = 1 )
    #Point constrain the first bind bone to the limb bind foot joint
    cmds.parentConstraint(mmDictOfIKFKSwitchLists["bindBone"][len(mmDictOfIKFKSwitchLists["bindBone"])-1], mmBindPad, mo = 1 )

    #Adjust the overall distance system from the leg to accomidate the reverse foot system
    cmds.delete(mmDictOfIKFKSwitchLists["distanceSystem"][1])
    cmds.pointConstraint( mmRevFootOriginalJoint, mmDictOfIKFKSwitchLists["distanceSystem"][0], mo = 1 )
 
    #To connect the new feet bones together:
    #Need to pass through all created items and grab various names to plug in to SDKs.
    mmIterate = 0
    ikfk_blendColor_Dict = {}
    mmNumberOfBonesInLegSystem = len(mmBindJointChain)

    while ( mmIterate < mmNumberOfBonesInLegSystem ):

        ikfk_blendColor_Dict[mmIterate] = mmRF.mmCreateBlendSystem( mmBindJointChain[mmIterate], mmIKJointChain[mmIterate], mmFKJointChain[mmIterate])

        mmIterate += 1

    #Do another pass for connecting all the various pieces together in SDKs
    mmIterate = 0

    while ( mmIterate < mmNumberOfBonesInLegSystem ):

        #mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
        #Example: mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-10, 10], [90, 0], 1 )
        mmRF.mmCreateSDK( nurbsCurveAttr, ikfk_blendColor_Dict[mmIterate], ".blender", [0, 10], [0, 1], 1 )

        mmIterate += 1

    #We need to move where the mesh is connected in this debaucle - which means we need to actually reconnect the loc of the mesh's name.
    #Find the foot loc we are looking for
    mmFootLoc = mmDictOfRevFootLists["footParentLoc"][0]
    #Find the constraint on it (should be parentC), and delete it
    mmChildrenOfFootLoc = cmds.listRelatives( mmFootLoc, c = 1 )
    for mmChild in mmChildrenOfFootLoc:
        mmNameChecker = mmChild.split("_")
        for mmName in mmNameChecker:
            if ( mmName[0:16] == "parentConstraint" ):
                cmds.delete(mmChild)

    #Make a new constraint between the bind forward foot bone and the loc.
    cmds.parentConstraint( mmBindJointChain[0], mmFootLoc, mo = 1 )

    #Need to create controls for the FK foot
    #Connect them to the fk bones
    if (mmFootControlGroup != None):
        mmParentGroup = mmFootControlGroup
    else:
        mmParentGroup = mmGroup_ExtraControls

    mmFKCreationList, fkIconNameList = mmRF.mmCreateFKControls( mmFKJointChain, len(mmFKJointChain), mmParentGroup, mmDictOfIKFKSwitchLists["fkBone"][len(mmDictOfIKFKSwitchLists["fkBone"])-1], "Foot" )
    
    #Need to set scale of control to match the object its controlling
    mmMeshToCheck = mmDictOfRevFootLists["footMesh"]

    mmCurrentBB = mmRF.mmGrabBoundingBoxInfo([mmMeshToCheck])

    mmDesiredColor = mmOF.mmGetColor(mmDictOfIKFKSwitchLists["fkIcon"][0][0])

    cmds.select(fkIconNameList[0])
    cmds.scale(mmCurrentBB["total"][0]*1.25, mmCurrentBB["total"][0]*1.25, mmCurrentBB["total"][0]*1.25)
    mmOF.changeColor(mmDesiredColor)

    #Freeze Scale Values
    cmds.makeIdentity( apply = True, t = 0 , r = 0 , s = 1 , n = 0, pn = 1)

    #Have them toggle visibility same as the leg
    i = 0
    while (i <= len(fkIconNameList)-1):
        mmRF.mmCreateSDK( nurbsCurveAttr, fkIconNameList[i], ".visibility", [0, 0.5, 9.5, 10], [0, 1, 1, 1], 1 )
        cmds.setAttr (fkIconNameList[i] + ".visibility", k = 0 )
        i += 1

    return None

'''
This Function creates a simple arm rig.
'''
def mmCreateArmRig( mmRootControl, mmLeftShoulderLoc, mmRightShoulderLoc ):
     
    #Grab Global Group Variables
    global mmGroup_Hidden
    global mmGroup_MainBones
    global mmGroup_Controls
    global mmGroup_BuildLocator

    mmGroup_Hidden = "_Group_Hidden"
    mmGroup_MainBones = "_Group_MainBones" 
    mmGroup_Controls = "_Group_Controls"
    mmGroup_BuildLocator = "_Group_BuildLocators"

    #Need to Organize!
    #Create groups to store stuff away
    mmGroup_Arm_Hidden = cmds.group( em = True, n = "_Group_Arm_Hidden" )
    mmGroup_Arm_MainBone = cmds.group( em = True, n = "_Group_Arm_MainBones" )
    mmGroup_Arm_BuildLocator = cmds.group( em = True, n = "_Group_Arm_BuildLocators" )

    cmds.select(cl= 1)
    
    cmds.parent( mmGroup_Arm_Hidden, mmGroup_Hidden )
    cmds.parent( mmGroup_Arm_MainBone, mmGroup_MainBones )
    cmds.parent( mmGroup_Arm_BuildLocator, mmGroup_BuildLocator )

    #clear selection
    cmds.select( cl = 1)
        
    #Create a counter to go through both arms
    mmCounter = 0
        
    mmArmName = "bob"
    mmCurrentController = None

    mmLastForearmController = ""

    mmNewControlsCreated = []

    #Create an extra arm controller for use of various ideas
    mmExtraArmControllerBase = mmOF.createCube()

    mmExtraArmControllerHand1 = mmOF.createHand()
    mmExtraArmControllerHand1 = cmds.rename( mmExtraArmControllerHand1, "hand_iconA" )

    cmds.scale( 0.25, 0.25, 0.25 )
    cmds.move( -2, 0, 0 )

    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    mmExtraArmControllerHand2 = mmOF.createHand()
    mmExtraArmControllerHand2 = cmds.rename( mmExtraArmControllerHand2, "hand_iconB" )

    cmds.scale( -0.25, 0.25, 0.25 )
    cmds.move( 2, 0, 0 )

    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    #Create an empty group and move shape nodes into it
    mmExtraArmController = cmds.group (em = 1)

    cmds.select( mmExtraArmControllerBase + "Shape", r = 1)
    cmds.select( mmExtraArmControllerHand1 + "Shape", add = 1 )
    cmds.select( mmExtraArmControllerHand2 + "Shape", add = 1 )
    cmds.select( mmExtraArmController, add = 1 )

    cmds.parent( r = 1, s = 1 )

    mmExtraArmController = cmds.rename( mmExtraArmController, "armExtra_Control" )

    cmds.delete( mmExtraArmControllerBase )
    cmds.delete( mmExtraArmControllerHand1 )
    cmds.delete( mmExtraArmControllerHand2 )

    #Find location of Root so we can offset the control just made
    mmTempPC = cmds.pointConstraint( mmRootControl, mmExtraArmController )

    cmds.delete( mmTempPC )

    cmds.parent( mmExtraArmController, mmRootControl )

    cmds.select( mmExtraArmController, r = 1 )

    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)


    #Need to create the required attributes on both arm controls, as well as required bones and heirarchy
    while mmCounter < 2:

        #Create or blank out a list
        mmCurrentArmControllers = [[""], [""]]

        #Select the proper Arm Info
        if (mmCounter == 0):

            #then select the right arm controls
            #****Should this be able to figure out different names?****
            mmArm_Shoulder_Loc = mmRightShoulderLoc
            mmArm_Shoulder_Control = mmRightShoulderLoc.split("_")[0] + "_Control"
            mmArmName = "right"
        
        elif (mmCounter == 1):

            #Select the left arm controls
            #****Should this be able to figure out different names?****
            mmArm_Shoulder_Loc = mmLeftShoulderLoc
            mmArm_Shoulder_Control = mmLeftShoulderLoc.split("_")[0] + "_Control"
            mmArmName = "left"


        #New - Grab stuff and store it as you do

        cmds.select( mmArm_Shoulder_Control )

        mmCurrentArmControllers[1][0] = cmds.listRelatives( p = 1 )[0]
        mmCurrentArmControllers[0][0] = cmds.listRelatives( mmCurrentArmControllers[1][0], p = 1 )[0]
        mmCurrentArmControllers.append( [mmArm_Shoulder_Control] )

        cmds.select( mmArm_Shoulder_Control )
        
        mmTempChildrenChecker = cmds.listRelatives( c = 1 )
        mmTempChildrenCollection = []

        for mmTempChild in mmTempChildrenChecker:

            mmNameChecker = mmTempChild.split("_")

            if ( mmNameChecker[1] == "Control"):

                mmTempChildrenCollection.append( mmTempChild )
        
        mmCurrentArmControllers.append( mmTempChildrenCollection )

        cmds.select( mmCurrentArmControllers[3][0] )

        mmTempChildrenChecker = cmds.listRelatives( c = 1 )
        mmTempChildrenCollection = []

        for mmTempChild in mmTempChildrenChecker:

            mmNameChecker = mmTempChild.split("_")

            if ( mmNameChecker[1] == "Control"):

                mmTempChildrenCollection.append( mmTempChild )


        mmCurrentArmControllers.append( mmTempChildrenCollection )

        cmds.select( mmCurrentArmControllers[4][0] )

        mmTempChildrenChecker = cmds.listRelatives( c = 1 )
        mmTempChildrenCollection = []

        for mmTempChild in mmTempChildrenChecker:

            mmNameChecker = mmTempChild.split("_")

            if ( mmNameChecker[1] == "Control"):

                mmTempChildrenCollection.append( mmTempChild )

        mmCurrentArmControllers.append( mmTempChildrenCollection )

        '''
        #Guide for mmCurrentArmControllers
        0-Parent (torso)
        1-Clavicle
        2-Shoulder
        3-Fore Arm
        4-Hand
        5-fingers/thumb/weapon holder
        '''

        mmCurrentArmLocators = []

        #Make a dupe list of Locators
        for mmLocList in mmCurrentArmControllers:

            mmTempList = []

            for mmLoc in mmLocList:
                mmNameChecker = mmLoc.split( "_" )

                if ( len( mmNameChecker ) > 1 ):

                    mmLocName = mmNameChecker[0] + "_loc"

                    mmTempList.append( mmLocName )

            mmCurrentArmLocators.append( mmTempList )


        #Store current loc of forearm
        mmForearmPad = cmds.group( em = 1 )

        mmForearmPad = cmds.rename( mmCurrentArmControllers[3][0] + "_pad" )

        mmTempPC = cmds.pointConstraint( mmCurrentArmControllers[3][0], mmForearmPad, mo = 0 )

        cmds.delete( mmTempPC )

        cmds.select( mmCurrentArmControllers[3][0] )

        mmOldParent = cmds.listRelatives( p = 1 )[0]

        cmds.parent( mmCurrentArmControllers[3][0], mmForearmPad )
        cmds.parent( mmForearmPad, mmOldParent )

        #Set to world trans
        mmGWT.main()


        #Create a list with the things needed in the order needed.
        mmSelectList = []

        if ( mmArmName == "right" ):
            mmSelectList.append( mmCurrentArmControllers[2][0] )
            mmSelectList.append( mmRootControl )
            mmSelectList.append( "headExtra_Control" )
            mmSelectList.append( mmCurrentArmControllers[0][0] )
            mmSelectList.append( "pelvis_Control" )
            mmSelectList.append( mmExtraArmController )

            mmRF.spaceSwitcherMulti( 3, mmCurrentArmControllers[3][0], [mmForearmPad], mmSelectList )

            #Save the forearm for this arm to use on the next arm
            mmLastForearmController = mmCurrentArmControllers[3][0]
            mmLastHandController = mmCurrentArmControllers[4][0]

        elif ( mmArmName == "left" ):
            mmSelectList.append( mmCurrentArmControllers[2][0] )
            mmSelectList.append( mmRootControl )
            mmSelectList.append( "headExtra_Control" )
            mmSelectList.append( mmCurrentArmControllers[0][0] )
            mmSelectList.append( "pelvis_Control" )
            mmSelectList.append( mmLastForearmController )
            mmSelectList.append( mmLastHandController )
            mmSelectList.append( mmExtraArmController )

            mmRF.spaceSwitcherMulti( 3, mmCurrentArmControllers[3][0], [mmForearmPad], mmSelectList )

        ######################################
        #Use mmRF.handCreator() to create and connect hand icons
        ######################################

        cmds.select( mmCurrentArmControllers[4][0], r = 1 )
        #Select proper locs first, remove holder
        for mmObject in mmCurrentArmLocators[5]:
            #Do not select the holder
            if ( mmObject != "mainHand_loc" and mmObject != "offHand_loc" ):
                cmds.select( mmObject, add = 1 )

        #Run Hand Creator, passing it some info to help build
        mmNewControlsCreated = mmRF.handCreator( True, 1, 1, 1, "ZXY", "XYZ" )

        mmTrashParentHolder = []
        #Ensure that new controls are Parented in properly
        for mmControl in mmNewControlsCreated:
            mmTempSideChecker = mmControl.split("_")
            mmTempLen = len(mmTempSideChecker)
            if ( mmTempLen > 3 and mmTempSideChecker[mmTempLen - 2][0:6] == "Master" ):
                mmTempParent = cmds.listRelatives(mmControl, p = 1)[0]
                #print "mmTempParent1", mmTempParent
                
                mmTempParent = cmds.listRelatives(mmTempParent, p = 1)[0]
                #print "mmTempParent2", mmTempParent

                mmTrashParent = cmds.listRelatives(mmTempParent, p = 1)[0]
                #print "mmTrashParent", mmTrashParent

                cmds.parent( mmTempParent, mmCurrentArmControllers[4][0] )
                mmTrashParentHolder.append(mmTrashParent)

        mmTrashParentHolder = list(set(mmTrashParentHolder))

        for mmTrashParent in mmTrashParentHolder:
            cmds.delete(mmTrashParent)

        mmNewControlsCreated.append( mmExtraArmController )

        ######################################
        #Disconnect the Shoulder and reconnect as needed
        ######################################
        
        #need to delete the parent constraint holding the mesh in place with this control
        cmds.select( mmCurrentArmLocators[2][0] )
        mmTempRelatives = cmds.listRelatives( type = "transform" )

        #print "mmTempRelatives", mmTempRelatives
        for mmTempRelative in mmTempRelatives:
            mmChecker = mmTempRelative.split("_")

            mmLenChecker = len(mmChecker)

            if ( mmChecker[mmLenChecker-1][0:16] == "parentConstraint" ):

                cmds.delete(mmTempRelative)

        #Need to dupe the shoulder control and scale it down so it looks different
        mmCurrentShoulderName = mmCurrentArmControllers[2][0].split("_")[0]
        mmCurrentArmName = mmCurrentArmControllers[3][0].split("_")[0]

        cmds.select(cl = 1)

        cmds.duplicate(mmCurrentArmControllers[2][0], name = mmCurrentShoulderName + "_Minor_Control", rc = 1)

        cmds.select(mmCurrentShoulderName + "_Minor_Control")

        mmMinorShoulderControl = cmds.ls(sl = 1)[0]

        mmShoulderParent = cmds.listRelatives(mmMinorShoulderControl, p = 1)

        mmAllChildren = cmds.listRelatives(mmMinorShoulderControl, c = 1)

        #Delete other children nodes - don't want to create a duplicate of the entire arm
        for mmChild in mmAllChildren:
            if ( mmChild != mmMinorShoulderControl + "Shape" ):

                cmds.delete( mmChild )

        cmds.select(mmMinorShoulderControl)

        #Scale down so its offset from original control
        cmds.scale( 0.5, 0.5, 1.2 )

        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

        mmMinorShoulderControlPad = mmOF.mmGroupInPlace( mmMinorShoulderControl )

        #Need to set the minor shoulder control to 0,0,0
        cmds.select(mmMinorShoulderControl)
        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

        #Connect minor shoulder control into the rig        
        cmds.parentConstraint( mmMinorShoulderControl, mmCurrentArmLocators[2][0], mo = 1 )

        mmSelectList = []

        #Create a space switcher which defaults to On so it mimics all old animations
        #cmds.parent( mmMinorShoulderControlPad, mmCurrentArmControllers[2][0] )
        mmSelectList.append(mmCurrentArmControllers[2][0])
        mmSelectList.append(mmCurrentArmControllers[1][0])
        mmSelectList.append(mmRootControl)

        mmRF.spaceSwitcherMulti(3, mmMinorShoulderControl, [mmMinorShoulderControlPad], mmSelectList)

        #Create a way for the shoulder mesh to "Look At" the elbow, without it screwing up as the body spins around (or whatever it does)
        #   Did not end up doing this as it ended up being more trouble than it was worth, and manually animating the shoulder to match the arm ended up being easy enough.

        '''
        #Guide for mmCurrentArmControllers
        0-Parent (torso)
        1-Clavicle
        2-Shoulder
        3-Fore Arm
        4-Hand
        5-fingers/thumb/weapon holder
        '''

        ######################################
        #Create Weapon Space Switcher
        ######################################
        for mmControl in mmCurrentArmControllers[5]:
            mmTempSideChecker = mmControl[0:4]

            #Create a list with the things needed in the order needed.
            mmSelectList = []

            #print "mmControl", mmControl

            if ( mmTempSideChecker == "main" or mmTempSideChecker == "offH" ):

                #Need to group the mmControl in place
                mmCreatedPad = mmOF.mmGroupInPlace(mmControl)

                #And then give it space switching
                mmSelectList.append( mmCurrentArmControllers[4][0] )
                mmSelectList.append( mmRootControl )
                mmSelectList.append( mmExtraArmController )

                mmRF.spaceSwitcherMulti( 3, mmControl, [mmCreatedPad], mmSelectList )

                #need to set control to 0,0,0
                cmds.select(mmControl)
                cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)



        mmCounter += 1


        ######################################
        #Make sure the controls which come back are colored
        ######################################
    for mmControl in mmNewControlsCreated:
        mmTempSideChecker = mmControl[0:4]


        cmds.select( mmControl, r = 1 )

        if ( mmTempSideChecker == "left" or mmTempSideChecker == "offH" ):
            mmOF.changeColor( 6 )    
        elif ( mmTempSideChecker == "righ" or mmTempSideChecker == "main"  ):
            mmOF.changeColor( 13 )
        else:
            mmOF.changeColor( 14 )


        #Organization - put things into folders
        # mmGroup_Hidden = "_Group_Hidden"
        # mmGroup_MainBones = "_Group_MainBones" 
        # mmGroup_Controls = "_Group_Controls"
        # mmGroup_BuildLocator = "_Group_BuildLocators"

        #cmds.parent( mmHoldInPlace, mmArmLocatorPointer, mmArmIKHandle, mmShoulderLocatorPointer, mmGroup_Arm_Hidden )
        #cmds.parent( mmShoulderBonePad, mmGroup_Arm_MainBone )

    cmds.select(cl = 1)

'''
This function connects the Carry bone appropriately.
'''
def mmCreateCarryRig( mmCarryControlName ):

    #Want a space switcher
    #   Carry:
    #       world by Default
    #       right arm
    #       left arm
    #       head
    #       torso
    #       pelvis

    mmCarryControlPad = mmOF.mmGroupInPlace( mmCarryControlName )

    mmNameChecker = mmCarryControlName.split("_")

    mmCarryLoc = mmNameChecker[0] + "_loc"

    mmCarryMesh = mmNameChecker[0]


    '''
    mmFindPC = cmds.listRelatives( mmCarryMesh, c = 1 )

    #Delete other children nodes (looking for parent constraint)
    for mmChild in mmFindPC:
        if ( mmChild != mmCarryMesh + "Shape" ):

            cmds.delete( mmChild )
    '''
    mmSelectList = []
    
    mmSelectList.append("root_Control")
    mmSelectList.append("rightArm_Control")
    mmSelectList.append("leftArm_Control")
    mmSelectList.append("head_Control")
    mmSelectList.append("torso_Control")
    mmSelectList.append("pelvis_Control")

    mmRF.spaceSwitcherMulti(3, mmCarryControlName, [mmCarryControlPad], mmSelectList)


    cmds.select(mmCarryControlName, r = 1 )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)


    #cmds.parent( mmCarryControlPad, "root_Control" )

    #Want a vis-swap
    #mmRF.mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
    #Example: mmRF.mmCreateSDK( mmFootRollAttr, mmCarryMesh, ".rotateX",  [-10, 10], [90, 0], 1 )

    #First create an attribute on the Root_Control
    cmds.select( "root_Control" )
    cmds.addAttr( longName="CarryVis", attributeType='enum', en = "on:off:", dv=0, k = 1 )
    mmCarryVis = "root_Control" + ".CarryVis"

    mmRF.mmCreateSDK( mmCarryVis, mmCarryMesh, ".visibility",  [0, 1], [1, 0], 1 )
    mmRF.mmCreateSDK( mmCarryVis, mmCarryControlName, ".visibility",  [0, 1], [1, 0], 1 )

'''
This function creates an attachment point over the cog of the rig.
'''
def mmCreateAttachmentOverCOG( mmCreatureType = "general", *args):

    #Find bounding box values of all meshes in the scene
    mmAllMeshesInScene = mmSAP.main(["mesh"])

    #Don't look at meshes that begin with "ATT"
    mmMeshesInSceneNotATT = []

    for mmChild in mmAllMeshesInScene:
        if ( not mmChild.startswith('ATT') ):
            mmMeshesInSceneNotATT.append(mmChild)

    mmBoundingBoxList = mmRF.mmGrabBoundingBoxInfo( mmMeshesInSceneNotATT )
    #mmGrabBoundingBoxInfo returns mmDictOfBoundingBoxLists with this information:
    # [
    #     "mmOverallMin":       [X, Y, Z],
    #     "mmOverallMidPoint":  [X, Y, Z],
    #     "mmOverallMax":       [X, Y, Z],
    #     "mmOverallTotal":     [X, Y, Z],
    #     "mmOverallPiv":       [X, Y, Z]
    # ]

    if ( mmCreatureType == "general" ):
        mmNewYMax = (mmBoundingBoxList["total"][1] * (1+1.0/2))/2 + mmBoundingBoxList["midPoint"][1]

    elif ( mmCreatureType == "human" ):
        mmNewYMax = (mmBoundingBoxList["total"][1] * (1+1.0/3))/2 + mmBoundingBoxList["midPoint"][1]

    cmds.polyCube( n = "ATTOVERCOG" )

    cmds.move( mmBoundingBoxList["midPoint"][0], mmNewYMax, mmBoundingBoxList["midPoint"][2] )

    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    mmCLAP.main()

'''
Need a function which hides/unhides the 'folder' groups appropriately
'''
def mmRigGroupHideToggle(*args):
    #
    #Does not currently toggle, need to fix
    #

    #Grab Global Group Variables
    global mmGroup_Hidden
    global mmGroup_MainBones
    global mmGroup_BuildLocator
    global mmGroup_ExportLocator

    mmGroup_Hidden = "_Group_Hidden"
    mmGroup_MainBones = "_Group_MainBones" 
    mmGroup_BuildLocator = "_Group_BuildLocators"
    mmGroup_ExportLocator = "_Group_ExportLocators"


    #Hide Hidden Group
    cmds.select( mmGroup_Hidden, r = 1 )
    mmTempItemsToSelect = cmds.listRelatives( mmGroup_Hidden )
    cmds.select( mmTempItemsToSelect, add = True )
    
    #Hide Bone Group
    cmds.select( mmGroup_MainBones, add = True )
    mmTempItemsToSelect = cmds.listRelatives( mmGroup_MainBones )
    cmds.select( mmTempItemsToSelect, add = True )

    #Hide Build Locators Group
    cmds.select( mmGroup_BuildLocator, add = True )
    mmTempItemsToSelect = cmds.listRelatives( mmGroup_BuildLocator )
    cmds.select( mmTempItemsToSelect, add = True )

    #Hide Export Locators Group
    cmds.select( mmGroup_ExportLocator, add = True )
    mmTempItemsToSelect = cmds.listRelatives( mmGroup_ExportLocator )
    cmds.select( mmTempItemsToSelect, add = True )
    
    cmds.HideSelectedObjects()
    cmds.select( cl = 1 )
    
'''
This function will search through all meshes on an object, detect if they are set to normal or reference, and toggle them to the opposite.
'''
def mmToggleGeoManipulation( mmFirstTime = False, *args):

    mmBoolChecker = False

    #Grab all Meshes in scene
    mmGeoShapeList = cmds.ls( type = "mesh" )
    mmGeoList = cmds.listRelatives( mmGeoShapeList, p = 1 )

    #print "mmGeoList", mmGeoList

    #If this is just a random time, then check if we need to do ref or norm.
    if ( mmFirstTime == False ):
        #Check just one, and then toggle all based on that check
        item = cmds.listRelatives( mmGeoList[0], c = 1 )[0]


        # print "item", item

        mmOverrideDisplayChecker = cmds.getAttr(item + ".overrideDisplayType")
        mmOverrideEnabledChecker = cmds.getAttr(item + ".overrideEnabled")

        # print "mmOverrideDisplayChecker", mmOverrideDisplayChecker
        # print "mmOverrideEnabledChecker", mmOverrideEnabledChecker

        if ( mmOverrideDisplayChecker == 0 and mmOverrideEnabledChecker == 0 ):
            mmBoolChecker = True

        else:
            mmBoolChecker = False


    else:
        mmBoolChecker = True

    #Actually go change everything
    for geoItem in mmGeoList:

        mmItemList = cmds.listRelatives( geoItem, c = 1 )

        for item in mmItemList:

            #Select both the mesh and the group it is in.
            cmds.select( geoItem, r = 1 )
            cmds.select( item, add = 1)

            if ( mmBoolChecker ):
                mmOF.refDisplayType()

            else:
                mmOF.normDisplayType()

    cmds.select(cl = 1)

'''
Need to turn off the vis swap option for all controls - doesn't provide anything and just adds to confusion.
***
May some day want to come back and re-address this.  There is a use for disabling visibility via the controls.
For example: This would let me hide the arms and legs while working on the body.
'''
def mmHideVisOptionOnControls( *args ):
    
    mmObjectInScene = cmds.ls( type = "transform" )

    #mmObjectInScene = cmds.ls( sl = 1)


    for mmObject in mmObjectInScene:

        mmNameChecker = mmObject.split("_")
        mmNameCheckerlen = len(mmNameChecker)

        
        if ( mmNameCheckerlen == 2 and mmNameChecker[1] == "Control" ):
            
            mmSelected = mmObject + ".v"
            cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False)

    cmds.select(cl = 1)

'''
This function should make the visibility parameter keyable again.  Should require no inputs, assumes a mesh with objects in the scene.
    Damages nothing if run multiple times.
'''
def mmRemoveVisLock(*args):

    
    mmAllSelected = mmSAP.main(["mesh", "nurbsCurve"])

    for mmObject in mmAllSelected:
        cmds.setAttr( mmObject + ".v", lock=False, keyable=True, channelBox=False )


'''
Fix Display of Maya to render how it is most useful.
'''
def mmFixUI(*args):

    cmds.modelEditor('modelPanel4', e=1, displayTextures=1, displayLights='all', ao = 1)
    cmds.modelEditor('modelPanel4', e=1, displayLights='all')
    cmds.modelEditor( 'modelPanel4', e=True, da= "smoothShaded" ) # Set the renderer used for a 3d modeling viewport
    mel.eval ('setAttr "hardwareRenderingGlobals.ssaoEnable" 1;' )

'''
This function toggles visibility of self.  It also manually ignores and toggles some nodes depending on input.
'''
def mmToggleVisOptionOnSelf( *args ):

    mmBoolChecker = False
    mmMeshExists = False
    mmMeshToSave = None

    # Take selected control and put it in a list, then cycle through all children and grabs those controls as well
    mmOriginalControl = cmds.ls( sl = 1 )[0]

    #Need to account for either referenced rigs or not
    mmNameChecker = mmOriginalControl.split(":")
    mmNameCheckerlen = len(mmNameChecker)

    if ( mmNameCheckerlen > 1 ):

        mmOriginalControl = mmNameChecker[1]
        mmPrefix = mmNameChecker[0]

        mmNameChecker = mmOriginalControl.split("_")

            
        # Grab all meshes from these controls
        # Check if there is a mesh for this control, and save it if it exists
        if (cmds.objExists(mmPrefix + ":" + mmNameChecker[0])):
            mmMeshToSave = mmNameChecker[0]
            mmMeshExists = True


        # Toggle visibility of all meshes and controls in the lists
        if ( cmds.getAttr( mmPrefix + ":" + mmOriginalControl + ".v" ) == 1 ):
            mmBoolChecker = True

        if ( mmBoolChecker ):
            cmds.setAttr( mmPrefix + ":" + mmOriginalControl + ".v", 0 )
            
            if ( mmMeshExists ):
                cmds.setAttr( mmPrefix + ":" + mmMeshToSave + ".v", 0 )
        else:
            cmds.setAttr( mmPrefix + ":" + mmOriginalControl + ".v", 1 )
            if ( mmMeshExists ):
                cmds.setAttr( mmPrefix + ":" + mmMeshToSave + ".v", 1 )

        cmds.select( mmPrefix + ":" + mmOriginalControl )
    else:

        mmNameChecker = mmOriginalControl.split("_")

            
        # Grab all meshes from these controls
        # Check if there is a mesh for this control, and save it if it exists
        if (cmds.objExists(mmNameChecker[0])):
            mmMeshToSave = mmNameChecker[0]


        # Toggle visibility of all meshes and controls in the lists
        if ( cmds.getAttr( mmOriginalControl + ".v" ) == 1 ):
            mmBoolChecker = True

        if ( mmBoolChecker ):
            cmds.setAttr( mmOriginalControl + ".v", 0 )
            cmds.setAttr( mmMeshToSave + ".v", 0 )
        else:
            cmds.setAttr( mmOriginalControl + ".v", 1 )
            cmds.setAttr( mmMeshToSave + ".v", 1 )

        cmds.select( mmOriginalControl )

'''
This function toggles visibility of children nodes.  It also manually ignores and toggles some nodes depending on input.
'''
def mmToggleVisOptionOnChildren( *args ):

    mmListOfControls = []
    mmListOfMeshes = []
    mmBoolChecker = False
    mmIsReferenced = False
    mmPrefix = None

    # Take selected control and put it in a list, then cycle through all children and grabs those controls as well
    mmOriginalControl = cmds.ls( sl = 1 )[0]

    #Need to account for either referenced rigs or not
    mmNameChecker = mmOriginalControl.split(":")
    mmNameCheckerlen = len(mmNameChecker)

    if ( mmNameCheckerlen > 1 ):
        mmIsReferenced = True
        mmOriginalControl = mmNameChecker[1]
        mmPrefix = mmNameChecker[0]

    mmNameChecker = mmOriginalControl.split("_")

    mmChildrenList = cmds.listRelatives( ad = 1 )

    for mmChild in mmChildrenList:

        if ( mmIsReferenced ):
            mmChild = mmChild.split(":")[1]

        # Cancel out if mmControl is looking at certain controls
        if ( mmChild == "carry_Control" ):
            print "found carry_Control"

        else:    
            #cmds.select( mmChild )


            mmNameChecker = mmChild.split("_")
            mmNameCheckerlen = len(mmNameChecker)
            
            #Verify we have a control
            if ( mmNameCheckerlen == 2 and mmNameChecker[1] == "Control" ):

                #Add control to list
                mmListOfControls.append(mmChild)

                #select current control
                #cmds.select( mmChild )
                
                if ( mmIsReferenced ):
                    mmNameChecker[0] = mmPrefix + ":" + mmNameChecker[0]
                
                # Discover if a mesh exists for the control, and save it if it does
                if ( cmds.objExists( mmNameChecker[0] ) ):
                    mmMeshToSave = mmNameChecker[0]

                
                    if ( mmIsReferenced ):
                        mmMeshToSave = mmMeshToSave.split(":")[1]

                    #Add mesh to list
                    if ( mmMeshToSave != "offHand" and mmMeshToSave != "mainHand" and mmMeshToSave != "bodyPosition"):
                        mmListOfMeshes.append( mmMeshToSave )

                    if ( mmMeshToSave == "leftFoot" ):
                        mmListOfMeshes.append( "leftToe" )

                    if ( mmMeshToSave == "rightFoot" ):
                        mmListOfMeshes.append( "rightToe" )

    print "mmListOfControls", mmListOfControls
    # Toggle visibility of all meshes and controls in the lists
    if ( mmIsReferenced ):
        if ( cmds.getAttr( mmPrefix + ":" + mmListOfControls[0] + ".v" ) == 1 ):
            mmBoolChecker = True
    else:
        if ( cmds.getAttr( mmListOfControls[0] + ".v" ) == 1 ):
            mmBoolChecker = True

    for mmObject in mmListOfControls:
        if ( mmBoolChecker ):
            if ( mmIsReferenced ):
                cmds.setAttr( mmPrefix + ":" + mmObject + ".v", 0 )

            else:
                cmds.setAttr( mmObject + ".v", 0 )
        else:
            if ( mmIsReferenced ):
                cmds.setAttr( mmPrefix + ":" + mmObject + ".v", 1 )

            else:
                cmds.setAttr( mmObject + ".v", 1 )
    
    for mmObject in mmListOfMeshes:
        if ( mmBoolChecker ):
            if ( mmIsReferenced ):
                cmds.setAttr( mmPrefix + ":" + mmObject + ".v", 0 )

            else:
                cmds.setAttr( mmObject + ".v", 0 )
        else:
            if ( mmIsReferenced ):
                cmds.setAttr( mmPrefix + ":" + mmObject + ".v", 1 )

            else:
                cmds.setAttr( mmObject + ".v", 1 )

    if ( mmIsReferenced ):
        cmds.select( mmPrefix + ":" + mmOriginalControl )

    else:
        cmds.select( mmOriginalControl )

'''
This function will add a weapon (or other mesh) to any controller (like the mainHand or offHand controllers for swords or hammers, etc.) for visibility while working in Maya.
    This will not add anything to the export.
    To use this function properly:
        Select any controller which you would like the item to be a part of.
        Then select every item which you would like to add to the rig.
        Then press the button.
'''
#trying to make this work with a function that monitors the enum
def mmAddItemToRig(*args):

    global mmGroup_ExtraObject

    mmGroup_ExtraObject = "_Group_ExtraObject"


    mmSelectedObject = cmds.ls(sl=True)

    mmWeaponHolder = mmSelectedObject[0]

    mmWeaponHolderAttr = mmWeaponHolder+'.ExtraVis'

    mmSelectedObjectLen = len(mmSelectedObject)
    # print "mmSelectedObjectLen: ", mmSelectedObjectLen

    mmCounter = 1

    while mmCounter < mmSelectedObjectLen :

        #Query the current vis swap holders of the selected control attr
        mmCurrentVisSwaps = cmds.addAttr(mmWeaponHolderAttr, q = 1, enumName = 1 )

        #Need to make sure there are no ":" in the attribute name - as when we are using a referenced model
        mmNameOfAttr = mmSelectedObject[mmCounter].split(":")[0]

        #Add new vis swap
        mmCurrentVisSwaps = mmCurrentVisSwaps + ":" + mmNameOfAttr + ":"

        cmds.addAttr( mmWeaponHolderAttr, e=True, en = mmCurrentVisSwaps )

        #Find out how many vis swaps exist
        mmCurrentVisSwapsSplit = mmCurrentVisSwaps.split(":")

        mmTotalNumberOfVisSwaps = len(mmCurrentVisSwapsSplit) - 1

        # print "mmTotalNumberOfVisSwaps", mmTotalNumberOfVisSwaps
        # print "mmCurrentVisSwaps", mmCurrentVisSwaps
        # print "mmCurrentVisSwapsSplit", mmCurrentVisSwapsSplit

        #After adding our new enum value, need to create an expression which make the added ones only display for their correct mesh.
     
        #SDKs aren't working, so lets just create an expression which only monitors the piece we need.
        mmVisWatcherExpression = "if(" + mmWeaponHolderAttr + " == " + str(mmTotalNumberOfVisSwaps-1) + "){ " + mmSelectedObject[mmCounter] + ".visibility = 1 ;} else{  " + mmSelectedObject[mmCounter] + ".visibility = 0 ;}"
        
        cmds.expression(s= mmVisWatcherExpression, n = ( "Vis_Watcher_for_"+mmSelectedObject[mmCounter] ), ae=0, uc=all )

        #Next need to make sure that the imported object is snapped to the rig appropriately
        cmds.parentConstraint( mmWeaponHolder, mmSelectedObject[mmCounter], mo = 0 )
        #Give it a scale constraint too
        cmds.scaleConstraint( mmWeaponHolder, mmSelectedObject[mmCounter], mo = 0 )

        #Need to take the new geo pieces added in, turn off their geo selections, and put them into a folder
        cmds.parent( mmSelectedObject[mmCounter], mmGroup_ExtraObject)

        mmCounter += 1


    #Toggle geo manipulation - we don't want anything selectable.
    mmToggleGeoManipulation(1)

    cmds.select( mmWeaponHolder, r = 1)

'''
Need a nice and easy way to bring in a referenced model without going to the reference editor.
Unfortunately I need a function to call another function because of MayaHappyFun.
'''
def mmCallBringInReference( *args ):
    mmBringInReference()

def mmBringInReference( mmRigFilename = None, *args ):
    #---------------------------------------------

    if ( mmRigFilename == None):
        #Ask the user what Rig should be referenced in.
        mmStartingDirectory = "C:/Radiant/stonehearth-assets/assets/models/entities"
        mmDialogueCaption = "Please select the Rig to Reference in and apply animation to."
        mmRigNamespace = "ReferencedAnimRig_Male"

        #Open a dialogue box where user can input information
        mmRigFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 1, fileFilter = 'MA (*.ma)', selectFileFilter = 'MA (*.ma)', dir = mmStartingDirectory )
        #print "mmRigFilename "
        #print mmRigFilename

    mmSavedDirectory = mmRFOF.main( mmRigFilename, 0 )
    # print "mmRigFilename"
    # print mmRigFilename

    mmSavedFilename = mmRFOF.main( mmRigFilename, 1 )

    # print "mmSavedFilename"
    # print mmSavedFilename

    #Need to import Referenced Rig
    cmds.file( mmRigFilename, r = 1, type = "mayaAscii", ignoreVersion = 1, gl = 1, mergeNamespacesOnClash = False, namespace = mmSavedFilename, options = "v=0;" )

    return mmSavedFilename
    #---------------------------------------------

'''
This function will load all referenced files, useful when you reference a file with children - this will load in those children (they are not brought in by default).
'''
def mmLoadAllReferences(*args):

    mmSelectedBefore = cmds.ls(sl = 1)

    mmAllReferences = cmds.ls(type = 'reference')

    mmAllReferencesLen = len (mmAllReferences) - 1

    mmCounter = 0

    while mmCounter < mmAllReferencesLen:
        
        if (mmAllReferences[mmCounter] != 'sharedReferenceNode' ):
            mmReferencePath = cmds.referenceQuery( mmAllReferences[mmCounter], filename = True)
            
            cmds.file( mmReferencePath, loadReferenceDepth = "asPrefs", loadReference = mmAllReferences[mmCounter] )
        mmCounter += 1

    cmds.select( mmSelectedBefore )

'''
This function will load in an OBJ file and remove its prefix.  This is the cleanest way to bring in a mesh.
'''
def mmBringInObj(*args):

    #Ask user where the OBJ is that they want to import
    #Create default path
    mmImportObjFilePath = "C:/Radiant/stonehearth-assets/assets/models/entities/humans/male/voxels/civ.obj"


    mmStartingDirectory = "C:/Radiant/stonehearth/source/stonehearth_data/mods/stonehearth/entities"
    mmDialogueCaption = "Please select a name and location for OBJ you would like to import."
    mmfileFilterName = 'OBJ'
    mmfileFilterType = '.obj'
    mmFilepathAndFilename = ""
    mmDesiredReturn = 0

    mmNewMesh = True

    #Open a dialogue box where user can input information
    mmImportObjFilePath = cmds.fileDialog2( cap = mmDialogueCaption, fm = 1, fileFilter = mmfileFilterName + ' (*' + mmfileFilterType + ')', selectFileFilter = mmfileFilterName + ' (*' + mmfileFilterType + ')', dir = mmStartingDirectory)

    #------------------------------------------

    #Actually import the file

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
    mmNewTransformNameList = []
    mmTempList = []

    #Want to store the prefix we are removing
    mmPrefixRemoved = ""

    for mmTransformName in mmSelectedTransformsInScene:

        #print ""
        #print "starting loop"
        #print "mmTransformName", mmTransformName

        #print "mmImportNamespace", mmImportNamespace


        #Remove the | from the name (not sure where it came from)
        mmTransformNameSplit = mmTransformName.split('|')

        #print "mmTransformNameSplit", mmTransformNameSplit

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

        #print "mmNewTransformList", mmNewTransformList

        if ( len(mmNewTransformList) > 1 ):

            mmPrefixRemoved = mmNewTransformList[0]
            mmNewTransformName = mmNewTransformList[1]

            #This portion will ensure that the meshes are clean - no weird centers or strange pivots or anything.

            mmChildren = cmds.listRelatives( mmTransformName, c = 1 )
            
            mmNodeTypeChecker = cmds.nodeType(mmChildren[0])
            
            if ( len(mmChildren) > 0 and mmNodeTypeChecker == "mesh"):

                cmds.ConvertSelectionToFaces()
                mmFaceSelection = cmds.ls(sl = 1)
     
                mmNameChecker = mmFaceSelection[0].split(".")

                
                mmNameCheckerLen = len(mmNameChecker[1])
                    
                mmMaxNumberBeforeAddingCube = int(mmNameChecker[1][4:mmNameCheckerLen-1])
                
                #Create cube and combine in with the mesh currently working with
                
                mmNewCube = cmds.polyCube( name = "mmNewCube")
                
                cmds.select(mmTransformName, r = 1)
                cmds.select(mmNewCube, add = 1)
                
                mmTransformName = cmds.polyUnite( mmTransformName, mmNewCube, ch = 1, mergeUVSets = 1, name = mmNameChecker[0] )
                
                cmds.select( mmTransformName[0] + ".f[" + str(mmMaxNumberBeforeAddingCube + 1) + ":" + str(mmMaxNumberBeforeAddingCube + 6) + "]" )
                
                cmds.delete()
                
                cmds.select( mmTransformName[0] )
                
                cmds.DeleteHistory()
            

            #Rename mesh without prefix
            cmds.rename( mmTransformName[0], mmNewTransformName )




            #mmNewTransformNameList.append(mmNewTransformName)

    #Delete any unused nodes - otherwise more and more are created each time script is run
    #  This is things like material nodes and what not
    mel.eval( 'MLdeleteUnused;' )

    #print "mmNewTransformNameList", mmNewTransformNameList

    #------------------------------------------

    #Want to brighten material's Ambient color so it looks like it is supposed to

    #setAttr "civ1:civ_simpletex1.ambientColor" -type double3 1 1 1 ;
    # print ""
    # print "Trying to fix the material brought in to be the proper ambient color."
    # print "mmPrefixRemoved", mmPrefixRemoved
    # print "mmImportNamespace", mmImportNamespace
    cmds.setAttr( mmPrefixRemoved + ":" + mmPrefixRemoved + "_simpletex1.ambientColor", 1,1,1, type = "double3")

    #And fix viewport
    mmFixUI()

    #------------------------------------------


    #Do need to toggle geo lock, as this is disabling what was there.. should we check and then restore to what it was?
    #  No, just disable.  99% of the time, we want geo manipulation disabled.
    #Actually don't want to run this - it prevents you from selecting it and attaching it to the rig.
    #   Instead, run this function after attaching to the rig.
    #mmToggleGeoManipulation(1)


    #------------------------------------------

    #mmSelectedItems = cmds.ls( sl = 1 )
        
'''
Need a function to load all the view only helpers (like weapons or tools) so I don't need to do it manually each time.
*****
I should really add a way to check if these already exist - because ATM I can't run this script multiple times.
'''
def mmLoadAllViewOnlyHelpersHumanRig(*args):

    #May want to add something that removes all currently connected referenced objects first - checks for and removes.
    #   That way we never run into the issue of duplicates.  But it would remove anything manually added, is that a problem?

    #Create a big list of asset paths
    mmBigListOfThingsToReference = []

    mmBigListOfThingsToReference = [
        #Weapons/Armor
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/weapons/wooden_sword/wooden_sword_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/weapons/short_sword/short_sword_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/weapons/long_sword/long_sword_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/weapons/bow/bow_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/weapons/giant_bone_axe/giant_bone_axe_equipped.ma"] ],
        [ "leftArm_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/armor/wooden_shield/wooden_shield.ma"] ],
        [ "leftArm_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/armor/knights_shield/knights_shield.ma"] ],
        #Tools
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/tools/mining_pick/mining_pick.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/tools/worker_axe/worker_axe.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/tools/worker_hammer/worker_hammer.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/blacksmith/blacksmith_hammer/blacksmith_hammer_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/carpenter/carpenter_saw/carpenter_saw_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/cleric/cleric_tome/cleric_tome_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/cook/cook_spoon/cook_spoon_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/engineer/engineer_wrench/engineer_wrench_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/farmer/farmer_hoe/farmer_hoe_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/herbalist/herbalist_staff/herbalist_staff_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/mason/mason_hammer/mason_hammer_equipped.ma"] ],
        [ "offHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/mason/mason_chisel/mason_chisel_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/herbalist/herbalist_pestle/herbalist_pestle_equipped.ma"] ],
        [ "offHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/herbalist/herbalist_mortar/herbalist_mortar_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/potter/potter_cutter/potter_cutter_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/shepherd/shepherd_crook/shepherd_crook_equipped.ma"] ],
        [ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/jobs/trapper/trapper_knife/trapper_knife_equipped.ma"] ],
        #Toys
        [ "carry_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/toys/plushie_toy_rabbit/plushie_toy_rabbit.ma"] ],
        [ "carry_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/food/teacup/teacup.ma"] ]

    ]

    #Find out the current file name
    mmRigFilepathAndFilename = cmds.file(q = 1, loc = 1)

    #Get the filename
    mmMainFilename = mmRFOF.main( str(mmRigFilepathAndFilename), 1 )

    #Find out which rig it is
    mmNameSplit = mmMainFilename.split("_")
    print "here is the mmNameSplit", mmNameSplit

    #Rig specific additions
    if ( mmNameSplit[1] == "Male" or mmNameSplit[1] == "male" ):
        mmBigListOfThingsToReference.append([ "torso_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/armor/simple_quiver/simple_quiver.ma"] ])
        mmBigListOfThingsToReference.append([ "headExtra_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/armor/steel_helmet/steel_helmet.ma"] ])

    elif ( mmNameSplit[1] == "Female" or mmNameSplit[1] == "female" ):
        mmBigListOfThingsToReference.append([ "torso_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/armor/simple_quiver/simple_quiver_female.ma"] ])
        mmBigListOfThingsToReference.append([ "headExtra_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/armor/steel_helmet/steel_helmet_female.ma"] ])
        
    elif ( mmNameSplit[1] == "Goblin" or mmNameSplit[1] == "goblin" ):
        mmBigListOfThingsToReference.append([ "mainHand_Control", ["C:/Radiant/stonehearth-assets/assets/models/entities/weapons/jagged_cleaver/jagged_cleaver_equipped.ma"] ])



    #Load in each file, then find and save its meshes somewhere
    for mmThing in mmBigListOfThingsToReference:

        mmSmallListOfThingsWhichHaveBeenReferenced = []

        mmItemPrefix = mmBringInReference( mmThing[1] )

        #print "mmThing[1]", mmThing[1]

        mmAllMeshes = cmds.listRelatives(cmds.ls( type = "mesh" ), p = 1)

        for mmMesh in mmAllMeshes:

            mmNameChecker = mmMesh.split(":")

            for mmName in mmNameChecker:
                if ( mmName == mmItemPrefix ):
                    mmSmallListOfThingsWhichHaveBeenReferenced.append(mmMesh)

        cmds.select( mmThing[0], r = 1 )
        for mmSmallThing in mmSmallListOfThingsWhichHaveBeenReferenced:
            #print "mmSmallThing", mmSmallThing
            cmds.select( mmSmallThing, add = 1 )

        mmAddItemToRig()

'''
This function creates a root at the lower central point of the model and parents all geo under it
'''
def mmRigPrep( boolCenterChecker = False, boolCenterPassIn = False, *args ):

    #Grab from the UI if the user wants to center pivots
    if ( boolCenterChecker == False ):
        boolCenter = cmds.checkBoxGrp("centerPivotsChkBox", q = 1, v1 = 1)
    else:
        boolCenter = boolCenterPassIn

    cmds.select(all = 1)

    mmBoundingBoxList = cmds.exactWorldBoundingBox( )

    mmXMin = mmBoundingBoxList[0]
    mmYMin = mmBoundingBoxList[1]
    mmZMin = mmBoundingBoxList[2]
    mmXMax = mmBoundingBoxList[3]
    mmYMax = mmBoundingBoxList[4]
    mmZMax = mmBoundingBoxList[5]

    #Find size user wants
    #Find total size
    mmXTotal = abs(mmXMax - mmXMin)
    mmYTotal = abs(mmYMax - mmYMin)
    mmZTotal = abs(mmZMax - mmZMin)

    #Find halfway point (i.e. center of object)
    mmXMidPoint = mmXMax - mmXTotal/2
    mmYMidPoint = mmYMax - mmYTotal/2
    mmZMidPoint = mmZMax - mmZTotal/2

    '''
    #This is just a visual of what is going on - appears to work great... would have been nice to have found this sooner.
    cmds.curve( d= 1, p=[(mmXMin, mmYMin, mmZMin), (mmXMax, mmYMin, mmZMin), (mmXMax, mmYMax, mmZMin), (mmXMin, mmYMax, mmZMin), (mmXMin, mmYMin, mmZMin), 
          (mmXMin, mmYMin, mmZMax), (mmXMax, mmYMin, mmZMax), (mmXMax, mmYMax, mmZMax), (mmXMin, mmYMax, mmZMax), (mmXMin, mmYMin, mmZMax),
          (mmXMax, mmYMin, mmZMax), (mmXMax, mmYMin, mmZMin), (mmXMax, mmYMax, mmZMin), (mmXMax, mmYMax, mmZMax), (mmXMin, mmYMax, mmZMax), (mmXMin, mmYMax, mmZMin) ],
          k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ))
    '''

    mmNewYMax = mmYTotal + mmYTotal/4

    mmRootLocator = cmds.spaceLocator( n = "root" )

    cmds.move( mmXMidPoint, mmYMin, mmZMidPoint )

    mmAllMeshes = cmds.listRelatives(cmds.ls( type = "mesh" ), p = 1)


    for mmMesh in mmAllMeshes:

        objectParent = cmds.listRelatives( mmMesh, p = 1 )
        #print "objectParent", objectParent

        #If user wants to center the pivots
        if ( boolCenter ):
            #Center the pivot of the mesh
            cmds.xform(mmMesh, cp=1)
    
        #If there is a parent of the current bone, store it here.
        if ( objectParent == None ):

            cmds.parent( mmMesh, mmRootLocator)

'''
This function looks at all meshes and if their names have "_blah" at the end, we remove it
'''
def mmMeshNameFixer( *args ):
    mmMeshesInScene = mmSAP.main(["mesh"])
    
    for mmMesh in mmMeshesInScene:

        # If mmMesh name has multiple parts, take only the first part and delete the rest
        mmMeshNameChecker = mmMesh.split("_")

        if ( len(mmMeshNameChecker) > 0 ):
            print "mmMesh", mmMesh
            print "mmMeshNameChecker[0]", mmMeshNameChecker[0]
            cmds.rename(mmMesh, mmMeshNameChecker[0])

    cmds.select(cl = 1)

'''
This function will take whatever is selected, attach a cube to it, then delete the faces of the cube.
This process cleans the mesh and removes any weird import issues (like strange bounding boxes).
'''
def mmCleanMesh( mmPassedItems = False, *args):
    # print "mmPassedItems", mmPassedItems

    if (mmPassedItems != False):
        mmSelectedItems = mmPassedItems
    else:
        mmSelectedItems = cmds.ls( sl = 1 )

    for mmItem in mmSelectedItems:
            
        mmChildren = cmds.listRelatives( mmItem, c = 1 )
        #print mmChildren
        
        mmCollectionOfChildrenMeshes = []
        mmCollectionOfChildrenTransforms = []
            
        for mmChild in mmChildren:
            mmNodeTypeChecker = cmds.nodeType(mmChild)

            #if we find a mesh object, store it as something to operate on later
            if ( mmNodeTypeChecker == "mesh"):

                cmds.select(mmChild)
                mmChildsParent = cmds.listRelatives(p = 1)

                mmCollectionOfChildrenMeshes.append( mmChildsParent[0] )

            #if we find a non-mesh, then it is likely a transform.  I am assuming here, but I think its gonna be generally ok.
            #unparent the object, and then parent it back in later.
            else:

                # print "non-mesh child: ", mmChild
                # print "un parenting it"

                cmds.select(mmChild)
                cmds.parent(w = 1)

                mmCollectionOfChildrenTransforms.append( mmChild )

        for mmGoodChild in mmCollectionOfChildrenMeshes:

            cmds.select(mmGoodChild)

            cmds.ConvertSelectionToFaces()
            mmFaceSelection = cmds.ls(sl = 1)

            mmNameChecker = mmFaceSelection[0].split(".")
            
            #For information purposes:
            #mmNameChecker[0] = name of shapenode selected
            #mmNameChecker[1] = f[#:#]
            #These are strings
            
            mmNameCheckerLen = len(mmNameChecker[1])
                
            mmMaxNumberBeforeAddingCube = int(mmNameChecker[1][4:mmNameCheckerLen-1])
            
            #Create cube and combine in with the mesh currently working with
            
            mmNewCube = cmds.polyCube( name = "mmNewCube")

            cmds.select(mmGoodChild, r = 1)

            #Find parent of mesh so you can re-parent later
            mmCurrentParent = cmds.listRelatives(mmGoodChild, p = 1)
            mmCurrentPivot = cmds.xform( q = 1, pivots = 1, ws = 1 )
            
            cmds.select(mmGoodChild, r = 1)
            cmds.select(mmNewCube, add = 1)
            
            mmItemNew = cmds.polyUnite( mmGoodChild, mmNewCube, ch = 1, mergeUVSets = 1, name = "trashname" )

            cmds.select( mmItemNew[0] + ".f[" + str(mmMaxNumberBeforeAddingCube + 1) + ":" + str(mmMaxNumberBeforeAddingCube + 6) + "]" )
            
            cmds.delete()
            
            cmds.select( mmItemNew[0] )
            
            cmds.DeleteHistory()

            mmItemNew[0] = cmds.rename( mmItemNew[0], mmGoodChild )

            
            cmds.parent( mmItemNew[0], mmCurrentParent[0] )

            cmds.xform( pivots = (mmCurrentPivot[0], mmCurrentPivot[1], mmCurrentPivot[2]), ws = 1 )

            for mmOldChild in mmCollectionOfChildrenTransforms:
                cmds.parent( mmOldChild, mmItemNew[0] )

            cmds.select(cl = 1)

'''
Need to clean off the meshes completely for transfering purposes later (as long as this doesn't break stuff).
'''
def mmFreezeTransOnGeo(*args):

    mmMeshesInScene = mmSAP.main(["mesh"])
    
    for mmMesh in mmMeshesInScene:

        cmds.select(mmMesh, r = 1)

        cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    cmds.select(cl = 1)

'''
This function should add scale to a rig which has already been created with the other scripts.  Should require no inputs.
***********************************
****This function does not work - on non-human rigs****
If Maya gives an error about 'decomposeMatrix not working' go to Maya plugins and enable the "Matrix" plug in.
***********************************
'''
def mmAddScaleToRig(*args):

    mmParentConstraintStorage = []
    mmIndividualStorage = []
    mmAllConstraintStorage = []
    mmGroup_ExportLocator = "_Group_ExportLocators"

    cmds.select( cl = 1 )

    mmAllSelected = cmds.ls( type = "transform" )

    #Search all transforms and grab their children to find any parentConstraints
    #Skip feet because they are giving problems
    for mmSelected in mmAllSelected:

        cmds.select( mmSelected, r = 1 )
            
        mmListedRelatives = cmds.listRelatives(  )

        if ( mmListedRelatives != None ):
            
            for mmRelative in mmListedRelatives:
                    
                if ( mmRelative.find( "parentConstraint" ) != -1 ):
                    
                    if ( mmRelative.find( "Toe_loc" ) != -1 ):
                        
                        print "found Toe_loc: " + mmRelative + ", skipping scaleConstraint"

                    else:

                        if ( mmRelative.find( "Foot" ) != -1 ):

                            print "found Foot: " + mmRelative + ", skipping scaleConstraint"


                        mmParentConstraintStorage.append( mmRelative )
                    
    #Need to verify that there is only one entry for each entry (no duplicates)
    #Need to remove duplicates and sort
    mmParentConstraintStorage = list(set(mmParentConstraintStorage))
    mmParentConstraintStorage.sort()

    #raise Exception, mmParentConstraintStorage


    #Grab info out of each parent constraint
    for mmCurrentParentConstraint in mmParentConstraintStorage:
            
        if ( "parentConstraint" in mmCurrentParentConstraint ):
            
            #Constraint Info Nodes
            mmConstraintName = ""
            mmConstraintType = 3
            mmParentNode = ""
            mmTargetNodes = []
                    
            mmTargetNodes = cmds.parentConstraint( mmCurrentParentConstraint, q = 1, targetList = 1 )
            
            cmds.select( mmCurrentParentConstraint )
                
            mmParentNode = cmds.listRelatives( p = 1 )

            mmConstraintName = mmCurrentParentConstraint
                    
            mmConstraintType = 3
                    
            mmIndividualStorage = [
                mmConstraintName,
                mmConstraintType,
                mmParentNode,
                mmTargetNodes
                ]
                    
            mmAllConstraintStorage.append(mmIndividualStorage)

    #Splitting apart for ease of thinking: finding out info in one loop and changing info in the next loop.

    for mmConstraint in mmAllConstraintStorage:
        
        mmInfoObjConstrained = None
        mmInfoObj = None
        mmLocFound = False

        #Need to find the name of the object which the parentConstraint is named for
        #Just remove "parentConstraint" plus one character before for the "_" and one after for the number of constraint.
        #  The number after may not always be there, this should account for that.

        if ( mmConstraint[0][ (len(mmConstraint[0]) - 19) ] == "_" ):
            mmInfoObjConstrained = mmConstraint[0][ 0 : (len(mmConstraint[0]) - 19) ]
            
        elif ( mmConstraint[0][ (len(mmConstraint[0]) - 18) ] == "_" ):
            mmInfoObjConstrained = mmConstraint[0][ 0 : (len(mmConstraint[0]) - 18) ]
            
        elif ( mmConstraint[0][ (len(mmConstraint[0]) - 17) ] == "_" ):
            mmInfoObjConstrained = mmConstraint[0][ 0 : (len(mmConstraint[0]) - 17) ]
        
        else:
            print "parentConstraint name did not match available models"
        
        #Finding the name of the object under the pad which was constrained by the parent constraint
        #   Only works for a parent constraint from a "_pad" group
        if ( mmInfoObjConstrained[ (len(mmInfoObjConstrained) - 4):len(mmInfoObjConstrained) ] == "_pad" ):
            mmInfoObj = mmInfoObjConstrained[ 0 : (len( mmInfoObjConstrained ) - 4) ]

        #Finding the name of the object under the pad which was constrained by the parent constraint
        #   Only works for a parent constraint from a "_pad#" group
        elif ( mmInfoObjConstrained[ (len(mmInfoObjConstrained) - 5):len(mmInfoObjConstrained) - 1 ] == "_pad" ):
            mmInfoObj = mmInfoObjConstrained[ 0 : (len( mmInfoObjConstrained ) - 5) ]
            
        #Finding the name of the object under the pad which was constrained by the parent constraint
        #   Only works for a parent constraint from a "_loc" group
        elif ( mmInfoObjConstrained[ (len(mmInfoObjConstrained) - 4):len(mmInfoObjConstrained) ] == "_loc" ):
            mmInfoObj = mmInfoObjConstrained
            mmLocFound = True
            
        #Finding the name of the object under the pad which was constrained by the parent constraint
        #   Only works for a parent constraint from a "_Control"
        elif ( mmInfoObjConstrained[ (len(mmInfoObjConstrained) - 7):len(mmInfoObjConstrained) ] == "_Control" ):
            mmInfoObj = mmInfoObjConstrained
            #Shouldn't this never happen?
            
        #Finding the name of the object under the pad which was constrained by the parent constraint
        #   Only works for a parent constraint from a "_Control"
        elif ( mmInfoObjConstrained[ (len(mmInfoObjConstrained) - 6):len(mmInfoObjConstrained) ] == "_Group" ):
            mmInfoObj = mmInfoObjConstrained[ 0 : (len( mmInfoObjConstrained ) - 6) ]
            
        #If we find an "_loc", then we should group in place and move its constraint up onto its parent.
        if mmLocFound:
            #Group in place
            mmCreatedPad = mmOF.mmGroupInPlace( mmInfoObj, "_parentPad" )

            #Then create a replacement parent constraint to whatever it is currently constrained to.
            cmds.parentConstraint( mmConstraint[3], mmCreatedPad )

            #Then delete the old constraint.
            cmds.delete( mmConstraint[0] )
        
        #Search for parent constraints with more than 1 connections - then it is a space switcher.
        if ( len(mmConstraint[3]) > 1 ):

            cmds.select( mmInfoObjConstrained )
            
            #Need to find the object with the attributes on it - think it is the name of the constraint minus the constraint

            '''
            mmIndividualStorage = [
            0    mmConstraintName,
            1    mmConstraintType,
            2    mmParentNode,
            3    mmTargetNodes
                ]
            '''

            if (mmInfoObj != None):
                mmCreatedPad = mmOF.mmGroupInPlace( mmInfoObj, "_scalePad" )

                mmSelectList = []

                for mmEachTargetNode in mmConstraint[3]:
                    mmSelectList.append( mmEachTargetNode )

                mmRF.spaceSwitcherMulti( 4, mmCreatedPad, [mmConstraint[2]], mmSelectList, False )

        else:

            if (mmInfoObj != None):
                mmCreatedPad = mmOF.mmGroupInPlace( mmInfoObj, "_scalePad" )

                cmds.scaleConstraint( mmConstraint[3], mmCreatedPad )

    #--------------------------------------
    #Next need to find all Reverse Foot Systems and connect them up as well.
    #   Because they aren't parent constrained around - they are just constrained.

    mmFwFtJoints = []
    mmRevFtJoints = []
    mmMatchingJoints = []


    #grab all joints

    mmAllJointsSelected = cmds.ls( type = "joint" )

    #remove duplicates and sort
    mmAllJointsSelected = list(set(mmAllJointsSelected))
    mmAllJointsSelected.sort()

    #separate out the forward feet and the reverse feet
    for mmJoint in mmAllJointsSelected :

        if ( "FwFt" in mmJoint ):
            mmFwFtJoints.append(mmJoint)
            
        elif ( "RevFt" in mmJoint ):
            mmRevFtJoints.append(mmJoint)

        else:
            print "found joint which is not in fwft or revft"
    
    #Then separate out the various joints by comparing them to each other.
    for mmActualFwJoint in mmFwFtJoints:
        
        mmActualFwJointName_Option1 =  mmActualFwJoint[0:len(mmActualFwJoint)-5]
        mmActualFwJointName_Option2 =  mmActualFwJoint[0:len(mmActualFwJoint)-7]
        
        for mmActualRevJoint in mmRevFtJoints:
        
            mmActualRevJointName_Option1 =  mmActualRevJoint[0:len(mmActualRevJoint)-6]
            mmActualRevJointName_Option2 =  mmActualRevJoint[0:len(mmActualRevJoint)-8]
            
            if ( mmActualFwJointName_Option1 == mmActualRevJointName_Option1 ):

                mmMatchingJoints.append( mmActualFwJoint )
                mmMatchingJoints.append( mmActualRevJoint )
            
            elif ( mmActualFwJointName_Option2 == mmActualRevJointName_Option2 ):

                if ( mmActualFwJoint[len(mmActualFwJoint)-1] == mmActualRevJoint[len(mmActualRevJoint)-1] ):

                    mmMatchingJoints.append( mmActualFwJoint )
                    mmMatchingJoints.append( mmActualRevJoint )


    #Next, just connect the joints
    mmCounter = 0
    # print "suspect while loop:"

    while ( mmCounter <= len( mmMatchingJoints )-1 ):
            
        cmds.scaleConstraint( mmMatchingJoints[mmCounter+1], mmMatchingJoints[mmCounter], mo = 1 )
        # print "mmMatchingJoints", mmMatchingJoints

        mmCounter += 2

    print ""

    #Due to ikHandles being screwy, we need to:
    #  remove them from their current parent
    #  parent them under a good null (_Group_Foot_Hidden should work because ikHandles shouldn't exist anywhere else - and if they do, not the end of the world.)
    #  and point constrain them to their old parent.
    #?  This assumes that all ikHandles are in the feet - what about legs/shoulders/other places?  Breaks?

    mmListedParents = []

    mmAllikHandlesSelected = cmds.ls( type = "ikHandle" )

    for mmikHandle in mmAllikHandlesSelected:

        cmds.select( mmikHandle )
        
        mmListedParents = cmds.listRelatives( ap = 1 )
        
        if ( mmListedParents[0] != "_Group_Foot_Hidden" ):

            cmds.parent( mmikHandle, "_Group_Foot_Hidden" )

            cmds.parentConstraint( mmListedParents[0], mmikHandle, mo = 1 )

    #---------------------------------------

    #Next Steps:
    #   Need to grab each "_Control".
    mmControllerStoreArray = []
    mmLocatorToHide = []
    mmControllerCheatArray = []

    cmds.select( cl = 1 )

    mmAllSelected = cmds.ls( type = "transform" )

    #Grab all controller names for later
    for mmSelected in mmAllSelected:
        if ( mmSelected.endswith( "_Control" ) and mmSelected != "_Group_Controls" and mmSelected != "root_Control" and not mmSelected.endswith( "_Master_Control" ) ):
            mmControllerCheatArray.append( mmSelected )

    #Search all transforms and look for "_Control"
    for mmSelected in mmAllSelected:

        mmParentNode = None
        mmEachControlInfo = []
        mmCreatedObjectToFreeze = []
        mmFoundControllerPadBool = False

        cmds.select( mmSelected, r = 1 )

        if ( mmSelected.endswith( "_Control" ) and mmSelected != "_Group_Controls" and mmSelected != "root_Control" and not mmSelected.endswith( "_Master_Control" ) ):

            mmSelectedBaseName =  mmSelected[0:len(mmSelected)-8]

            #grab selected's parent
            mmParentNode = cmds.listRelatives( mmSelected, p = 1 )[0]
            if ( mmParentNode.endswith("_pad") or mmParentNode[len(mmParentNode)-5:len(mmParentNode)-2] == "pad" ):
                #?  Don't want to change the parent.. this is bad
                # mmParentNode = cmds.listRelatives( mmParentNode, p = 1 )[0]
                #?  No longer sure why this is important...
                print "FOUND A CONTROLLER PAD ON", mmSelected
                mmFoundControllerPadBool = True
            
            mmEachControlInfo.append( mmSelected )
            mmEachControlInfo.append( mmSelectedBaseName )
        
            #   Group in place 4 times and name them: Offset, Trans, Rot, Scale.
            mmOffsetPad = mmOF.mmGroupInPlace( mmSelected, "_OffsetPad" )
            mmTransPad = mmOF.mmGroupInPlace( mmSelected, "_TransPad" )
            mmRotPad = mmOF.mmGroupInPlace( mmSelected, "_RotPad" )
            mmScalePad = mmOF.mmGroupInPlace( mmSelected, "_ScalePad" )

            mmCreatedObjectToFreeze.append( mmOffsetPad )
            mmCreatedObjectToFreeze.append( mmTransPad )
            mmCreatedObjectToFreeze.append( mmRotPad )
            mmCreatedObjectToFreeze.append( mmScalePad )

            # #Create proper hierarchy - don't need to do this as everything is already in the heirarchy properly.
            # cmds.parent( mmScalePad, mmRotPad )
            # cmds.parent( mmRotPad, mmTransPad )
            # cmds.parent( mmTransPad, mmOffsetPad )

            #   Create a locator, Place locator at control's pivot, naming it the name of that control + "_ControlDriver".
            mmControlDriver = cmds.spaceLocator(  )

            mmTrashPConstraint = cmds.parentConstraint( mmSelected, mmControlDriver, w = 1, mo = 0 )

            cmds.delete(mmTrashPConstraint)

            mmControlDriver = cmds.rename( mmSelectedBaseName + "_ControlDriver" )

            mmCreatedObjectToFreeze.append(mmControlDriver)

            mmEachControlInfo.append( mmControlDriver )
            mmLocatorToHide.append( mmControlDriver )

            #   This new "_ControlDriver" locator needs to be parented under the controller's parent - even if it is a pad (pad is there for a reason).
            #       Eventually this must be parented under the "_MeshDriver" loc of that parent.
            cmds.parent( mmControlDriver, mmParentNode )

            #   Then parent the control to its Offset node.
            cmds.parent( mmSelected, mmOffsetPad )

            #   Need to create another locator under the Scale naming it the name of that control + "_MeshDriver".
            mmMeshDriver = cmds.spaceLocator(  )

            mmTrashPConstraint = cmds.parentConstraint( mmSelected, mmMeshDriver, w = 1, mo = 0 )

            cmds.delete(mmTrashPConstraint)

            mmMeshDriver = cmds.rename( mmSelectedBaseName + "_MeshDriver" )
            
            mmCreatedObjectToFreeze.append(mmMeshDriver)

            mmEachControlInfo.append( mmMeshDriver )
            mmLocatorToHide.append( mmMeshDriver )

            #   The "_MeshDriver" locator should be parented under the "Scale" pad.
            cmds.parent( mmMeshDriver, mmScalePad )

            # #This is where I should be freezing transforms to 0,0,0.
            # #select everything just created and freeze its transforms
            # for mmObject in mmCreatedObjectToFreeze:
            #?  Did I change my mind?  Why is this commented out?

            #     cmds.select( mmObject, r = 1 )

            #     cmds.makeIdentity( apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)

            #   Next constrain the trans, rot, and scale individually between the "_Control" and the corresponding group.
            cmds.pointConstraint( mmSelected, mmTransPad, w=1.0, mo=1 )
            cmds.orientConstraint( mmSelected, mmRotPad, w=1.0, mo=1 )

            #?  Instead of constraining the control to the scale pad, we want to connect the control to the mult/div
            #?      Maybe we need this, and then we also need to do the other bit
            cmds.scaleConstraint( mmSelected, mmScalePad, w=1.0, mo=1 )

            #################
            #? !!!! - Think this is where I need to inject a node with the parent's scale info !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #?  Will this work with the root?  Looks like I purposefully don't include it above.

            # print "mmSelected", mmSelected
            # print "mmParentNode", mmParentNode
            # print "mmScalePad", mmScalePad
            # print ""

            #Need another pad for the control's to get the scale info
            mmControllerScalePad = mmOF.mmGroupInPlace( mmSelected, "_scalePad#" )

            #Multiply divide node should multiply blend color into current scale
            #create needed multiply Divide node
            #No longer needed
            # multDivNodeName = cmds.shadingNode("multiplyDivide", au = 1, n = mmSelected + "_multDivNode#")

            #Create a blendColor node
            mmSNBlendColor = cmds.shadingNode("blendColors", au = 1, n = mmSelected + "_blendColors#")

            #Create Attr
            cmds.addAttr(mmSelected, ln= ("apply_parentScale"), at ="double", min= 0.0, max =1.0, dv=1, k=1)

            #Create a decompose matrix node
            mmDecomposeMatrixNode = cmds.createNode( 'decomposeMatrix', n = mmSelected + "_decomposeMatrix#" )
            # Mel: connectAttr -force leftHand_ControlShape.worldMatrix[0] decomposeMatrix1.inputMatrix;

            #And decompose matrix of parent, then connect the output scale to the blend color
            cmds.connectAttr(mmParentNode + ".worldMatrix[0]", mmDecomposeMatrixNode + ".inputMatrix", f =1)

            #Input
            #   Should take in from parent and created attribute
            cmds.connectAttr(mmDecomposeMatrixNode + ".outputScale", mmSNBlendColor + ".color1", f =1)
            cmds.setAttr(mmSNBlendColor + ".color2R", 1)
            cmds.setAttr(mmSNBlendColor + ".color2G", 1)
            cmds.setAttr(mmSNBlendColor + ".color2B", 1)
            cmds.connectAttr(mmSelected + ".apply_parentScale", mmSNBlendColor + ".b", f =1)
            #Output
            #   Should output to multiply divide node
            # cmds.connectAttr(mmSNBlendColor + ".output", multDivNodeName + ".input1", f =1)
            #?  Instead, lets plug this into the mmControllerScalePad
            cmds.connectAttr(mmSNBlendColor + ".output", mmControllerScalePad + ".scale", f =1)

            # #Connects the scale of the parent control to the input of the multiply divide node and output to a pad.
            # cmds.connectAttr( mmSelected + ".scale" , multDivNodeName + ".input2" )
            
            # cmds.connectAttr( multDivNodeName + ".o" , mmControllerScalePad + ".scale" )
            #?  Don't think we want to do this (its double)
            # cmds.connectAttr( multDivNodeName + ".o" , mmScalePad + ".scale" )

            #################

            #Save some info from the current control for the next pass
            mmEachControlInfo.append( mmParentNode )
            mmEachControlInfo.append( mmOffsetPad )
            mmEachControlInfo.append( mmScalePad )

            #   Store the control info in the controller store array.
            mmControllerStoreArray.append( mmEachControlInfo )
        
            #If there was a controller pad, drop into a cycle of scale constraints up the chain
            if  ( mmFoundControllerPadBool ):
                print "starting cycle to find a controller"
            while ( mmFoundControllerPadBool ):

                cmds.select( mmParentNode, r = 1 )
                    
                mmParentOfParent = cmds.listRelatives( p = 1 )[0]

                #? Scale constraint isn't working for some STRANGE reason
                # cmds.scaleConstraint( mmParentOfParent, mmParentNode, w=1.0, mo=1 )

                ############################
                # Try doing Direct Connect here instead.
                cmds.connectAttr(mmParentOfParent+".scale", mmParentNode+".scale" )

                print "mmParentNode", mmParentNode
                print "mmParentOfParent", mmParentOfParent

                #Break out of loop if we find a control in the main controller array
                if ( mmParentOfParent in mmControllerCheatArray ):

                    mmFoundControllerPadBool = False

                    print "Controller found"
                    print ""

                mmParentNode = mmParentOfParent

    #Start new for loop - so everything else should be finished and good to go.
    for mmSelectedControlInfo in mmControllerStoreArray:

        mmCurrentControl = mmSelectedControlInfo[0]
        mmCurrentBaseName = mmSelectedControlInfo[1]
        mmControlDriver = mmSelectedControlInfo[2]
        mmMeshDriver = mmSelectedControlInfo[3]
        mmParentNode = mmSelectedControlInfo[4]
        mmOffsetPad = mmSelectedControlInfo[5]
        mmScalePad = mmSelectedControlInfo[6]
        mmDesiredScalePad = ""
    
        #Can't run this stuff on controls which don't have corresponding '_loc' meshes, so need to figure out what work does need to be done on them as well.
        if ( mmCurrentBaseName.find( "armExtra" ) != -1 or 
            mmCurrentBaseName.find( "headExtra" ) != -1 or 
            mmCurrentBaseName.find( "Clavicle" ) != -1 or 
            mmCurrentBaseName.find( "Master" ) != -1 or 
            mmCurrentBaseName.find( "Minor" ) != -1 or 
            mmCurrentBaseName.find( "lookAt" ) != -1 or 
            mmCurrentBaseName.find( "cog" ) != -1 ):
            print "Found extra controller", mmCurrentBaseName
            
            # ? think this is needed, but gonna try something else first
            if ( mmCurrentControl != "root_Control" ):

                #Connect Control to ControlDriver
                cmds.parentConstraint( mmControlDriver, mmOffsetPad, mo = 1 )

            #   Next parent the Offset pad to the "_Group_Controls" node, as the hierarchy needs to be flat.
            cmds.parent( mmOffsetPad, "_Group_Controls" )

        else:
            # print "mmSelectedControlInfo", mmSelectedControlInfo

            #Search the "_loc" and grab their children to find any Constraints
            mmLocNode = mmCurrentBaseName + "_loc"

            cmds.select( mmLocNode, r = 1 )
                
            mmListedRelatives = cmds.listRelatives( c = 1 )
                
            if ( mmListedRelatives != None ):
                
                for mmRelative in mmListedRelatives:
                        
                    if ( mmRelative.find( "Constraint" ) != -1 ):

                        #   Then replace any constraint which goes between a "_loc" and "_Control" to instead
                        #       go between a "_loc" and this new "_MeshDriver" loc.
                        
                        #Gather info out of the current constraint
                        mmTargetNodes = []
                                
                        mmTargetNodes = cmds.parentConstraint( mmRelative, q = 1, targetList = 1 )
                        
                        cmds.delete( mmRelative )

                        # If there is a single target which this _loc is parented to, then parent instead to the meshdriver
                        if ( len(mmTargetNodes) == 1 ):

                            cmds.parentConstraint( mmTargetNodes[0], mmLocNode, mo = 1 )

                        else:
                            print "This is a space switcher, which this portion of the scale adder function is not designed to replace: ", mmRelative

            #   Here is where the "_ControlDriver" should be parented under the "_MeshDriver" of their parent.
            #   - and therefore this must be a separate loop, so we are sure everything is created.
            #       So check and see if there are any nodes with the name "_ControlDriver".
            #       If yes (because many bones don't have them), then parent it under the "_MeshDriver".
            #           No.. All bones have to have a "_ControlDriver", because we just created them above.

            if ( mmCurrentControl != "root_Control" ):
                #Must find ParentNode's _MeshDriver
                for mmParentController in mmControllerStoreArray:

                    if ( mmParentController[0] == mmParentNode ):
                        mmDesiredScalePad = mmParentController[6]

                        cmds.select( mmDesiredScalePad )

                        mmChildNodes = cmds.listRelatives( c = 1 )

                        for mmChild in mmChildNodes:

                            if ( mmChild.find( "_MeshDriver" ) != -1 ):
                                # print "mmChild", mmChild

                                cmds.parent( mmControlDriver, mmChild )

                            else:
                                #?  No longer sure why this is here.. lets assume it is ok for now...
                                print "mmChild", mmChild
                                print "Did not find a MeshDriver node."

                #Connect Control to ControlDriver
                cmds.parentConstraint( mmControlDriver, mmOffsetPad, mo = 1 )


            #   Next parent the Offset pad to the "_Group_Controls" node, as the hierarchy needs to be flat.
            cmds.parent( mmOffsetPad, "_Group_Controls" )

            #   Also need to reparent the "_loc" nodes to the ExportLocators group so that is flat as well.
            #To do that, we need to grab their scalePads and then parent pads and reparent them
            cmds.select( mmLocNode )
            mmScalePad = cmds.listRelatives( p = 1 )[0]
            cmds.select( mmScalePad )
            mmParentPad = cmds.listRelatives( p = 1 )[0]
            cmds.parent( mmParentPad, "_Group_ExportLocators" )

    #   Clean Up:
    #       Need to hide all the new background locators.
    for mmLocator in mmLocatorToHide:

        cmds.select( mmLocator )
        cmds.HideSelectedObjects()


    #Also need to ensure that all pads and locators are clean - otherwise we're going to be leaving tons of junk info.
    #   I think I did this along the way, but should definitely check.

    # cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

'''
_______________________________________________________________________________________________________________________________________________________
__________________________________________________________Creation Scripts_____________________________________________________________________________
_______________________________________________________________________________________________________________________________________________________
'''


'''
Run all script pieces to create a human rig
'''
def mmHumanRigRunAll(*args):

    mmFixUI()

    mmSDF3M.main( "root" )
    mmCreateRigGroups() #Need to go back and re-introduce cleanup as i go
    mmCreateCarryGeo( "root" )
    main()

    #Step 1 - create a set of locators for placement verification before rig creation
    mmCreateRevFootRigPrimer([], 1)
    mmCreateClavicleRigPrimer()

    #Step 2 - create the needed controllers for placement verification before rig creation
    mmDuplicateFootAndInvert("root", 1)
    mmDuplicateClavicleAndInvert("root")

    mmCreateBasicControllersHumanRig()

    #Step 3 - Begin Rig Creation
    mmConnectTheRigControlsUp()

    mmCreateHeadRig( "head_loc" )
    mmCreateRevFootRig( "leftFoot_loc", "rightFoot_loc" )
    mmCreateArmRig( "root_Control", "leftShoulder_loc", "rightShoulder_loc" )
    mmCreateCarryRig( "carry_Control" )
    mmCreateAttachmentOverCOG("human")

    #Step 4 - Clean Up Everything
    mmFreezeTransOnGeo()
    mmRigGroupHideToggle()
    mmHideVisOptionOnControls()
    mmToggleGeoManipulation(True)

    cmds.setAttr("root.visibility", 0)

    #Force Save
    cmds.file( force = 1, save = 1, type = 'mayaAscii' )

'''
Run individual scripts for human rig creation
'''
def mmHumanRigRunStep1(*args):

    mmFixUI()

    mmSDF3M.main( "root" )
    mmCreateRigGroups() #Need to go back and re-introduce cleanup as i go
    mmCreateCarryGeo( "root" )
    main()

'''
Run individual scripts for human rig creation
'''
def mmHumanRigRunStep2(*args):
    #Step 1 - create a set of locators for placement verification before rig creation
    mmCreateRevFootRigPrimer([], 1)
    mmCreateClavicleRigPrimer()

'''
Run individual scripts for human rig creation
'''
def mmHumanRigRunStep3(*args):
    #Step 2 - create the needed controllers for placement verification before rig creation
    mmDuplicateFootAndInvert("root", 1)
    mmDuplicateClavicleAndInvert("root")

    mmCreateBasicControllersHumanRig()

'''
Run individual scripts for human rig creation
'''
def mmHumanRigRunStep4(*args):
    #Step 3 - Begin Rig Creation
    mmConnectTheRigControlsUp()

    mmCreateHeadRig( "head_loc" )
    mmCreateRevFootRig( "leftFoot_loc", "rightFoot_loc" )
    mmCreateArmRig( "root_Control", "leftShoulder_loc", "rightShoulder_loc" )
    mmCreateCarryRig( "carry_Control" )
    mmCreateAttachmentOverCOG("human")

    #mmLoadAllViewOnlyHelpersHumanRig()

    #Clean Up Everything
    mmFreezeTransOnGeo()
    mmRigGroupHideToggle()
    mmHideVisOptionOnControls()
    mmToggleGeoManipulation(True)

    cmds.setAttr("root.visibility", 0)

    #Force Save
    cmds.file( force = 1, save = 1, type = 'mayaAscii' )

'''
Run all script pieces to create a generic rig
#?  Unsure that this is still working, also unsure why we would use it at this point.. most rigs will require a little hand holding, and that's ok.
'''
def mmGenericRunAll(*args):

    mmFixUI()


    mmHeadBool = False

    mmObjectsInScene = cmds.ls( type = ("mesh") )
    #print "mmObjectsInScene", mmObjectsInScene
    mmObjectsInScene = cmds.listRelatives( mmObjectsInScene, p = 1 )
    #print "mmObjectsInScene", mmObjectsInScene

    if "head" in mmObjectsInScene:
        mmHeadBool = True

    #Step 1 - create a basic set of controllers and allow user to manipulate them
    mmSDF3M.main( "root" )
    mmCreateRigGroups()
    main()
    mmCreateBasicControllersGenericRig()

    #Step 2 - Begin Rig Creation
    mmConnectTheRigControlsUp()
    if (mmHeadBool):

        mmCreateHeadRig( "head_loc" )

    mmCreateAttachmentOverCOG()

    #Clean Up
    mmFreezeTransOnGeo()
    mmRigGroupHideToggle()
    mmHideVisOptionOnControls()
    mmToggleGeoManipulation(True)

    cmds.setAttr("root.visibility", 0)

    #Force Save
    cmds.file( force = 1, save = 1, type = 'mayaAscii' )

'''
Run individual scripts for generic rig creation
'''
def mmGenericRigRunStep1(*args):

    mmFixUI()

    #Step 1 - create a basic set of controllers and allow user to manipulate them
    mmSDF3M.main( "root" )
    mmCreateRigGroups()
    main()
    mmCreateBasicControllersGenericRig()

'''
Add optional feet to generic rig
'''
def mmGenericRigAddFeet(*args):
    mmCreateLimbPrimer( [] )

'''
Run individual scripts for generic rig creation
'''
def mmGenericRigRunStep2(*args):
    #Step 2 - Begin Rig Creation

    #Connect all rig controls up
    mmConnectTheRigControlsUp()

'''
Add optional spine to generic rig
'''
def mmGenericRigAddSpine(*args):
    mmCreateQuadrupedSpinePrimer(  )

'''
Run individual scripts for generic rig creation
'''
def mmGenericRigRunStep3(*args):

    #Need to figure out if there is a head rig, and then create a rig off of it
    mmHeadBool = False

    mmObjectsInScene = cmds.ls( type = ("mesh") )
    mmObjectsInScene = cmds.listRelatives( mmObjectsInScene, p = 1 )

    #This assumes we named our head mesh "head" - don't like that we assume.
    if "head" in mmObjectsInScene:
        mmHeadBool = True

    #Need to figure out if there is a foot rig (or multiple), and then create a rig off of it
    mmLimbBool = False

    mmObjectsInScene = cmds.ls( type = ("transform") )
    

    for mmObject in mmObjectsInScene:

        mmNameChecker = mmObject.split("_")
        mmNameCheckerLen = len(mmNameChecker)
        
        if ( mmNameCheckerLen > 1 and mmNameChecker[1] == "limb" ):
            
            mmLimbBool = True

            #Need to grab the actual loc names off of the bones themselves as well, then store them and pass them in down below in the function call
                #?  Do I need to do this?  I guess this was never implemented.

    #Step 3 - Finish Rig Creation
    mmCreateSpineRig()

    if (mmHeadBool):
        mmCreateHeadRig( "head_loc" )

    if (mmLimbBool):
        mmCreateLimbActual()

    mmCreateAttachmentOverCOG()

    #Clean Up
    mmFreezeTransOnGeo()
    mmRigGroupHideToggle()
    # mmHideVisOptionOnControls()
    mmToggleGeoManipulation(True)

    #Force Save
    #?  Disabling for now.. and possibly always.  If the script messes up and crashes maya - we're stuck with a bad save.
    #?      User can just save the file, they are always responsible in the end.
    #?      We can't guarantee success when using the script, better to not force failure..
    # cmds.file( force = 1, save = 1, type = 'mayaAscii' )

    cmds.setAttr("root.visibility", 0)


'''

#########################
##### MUST FIX THIS #####
#########################

*Important:
mmDissassembleRig is broken if you add scale to your rig.  Need to make a new one/fix old one which accounts for both with scale or without.

Need to get all this stuff about rig creation into a separate file called 'rig creation' or something - does not belong in a conversion file.

Geo with a name with "_blah" (blah being anything) at the end is not considered a piece of geo. 
    If this is true (and we want this functionality), we should notify the user whenever one is brought in (because we know it will error later), and qubicle likes to create geo with that name all the time.



#########################
##########Ideas##########
#########################

What about spine IK?  That would also be nice sometimes, definitely on some monsters.. maybe do it later?
Adding a chest break would be beneficial to create "C" shapes, and a spineIK would help as well.  Maybe when I have all the time in the world : /.
Should figure out leg/arm/wrist/finger IKs as well when that happens.


#########################
######## Helpers ########
#########################

raise RuntimeError('# Problem is here #')


'''

"""
#############
Unfinished Code
#############

######################
#   Creating a carry geo and control and such on a general rig - really just needs a button.
mmCreateCarryGeo("root")
mmCreateCarryRig( "carry_Control" )

#   Need to remove all the named controls from mmCreateCarryRig and change it to selection or something

'''
This function connects the Carry bone appropriately.
'''
def mmCreateCarryRig( mmCarryControlName ):

    #Want a space switcher
    #   Carry:
    #       world by Default
    #       right arm
    #       left arm
    #       head
    #       torso
    #       pelvis

    mmCarryControlPad = mmOF.mmGroupInPlace( mmCarryControlName )

    mmNameChecker = mmCarryControlName.split("_")

    mmCarryLoc = mmNameChecker[0] + "_loc"

    mmCarryMesh = mmNameChecker[0]


    '''
    mmFindPC = cmds.listRelatives( mmCarryMesh, c = 1 )

    #Delete other children nodes (looking for parent constraint)
    for mmChild in mmFindPC:
        if ( mmChild != mmCarryMesh + "Shape" ):

            cmds.delete( mmChild )
    '''
    mmSelectList = []
    
    mmSelectList.append("root_Control")
    mmSelectList.append("headExtra_Control")
    mmSelectList.append("torso_Control")
    mmSelectList.append("body_Control")
    mmSelectList.append("bottom_Control")

    mmRF.spaceSwitcherMulti(3, mmCarryControlName, [mmCarryControlPad], mmSelectList)


    cmds.select(mmCarryControlName, r = 1 )
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)


    #cmds.parent( mmCarryControlPad, "root_Control" )

    #Want a vis-swap
    #mmRF.mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
    #Example: mmRF.mmCreateSDK( mmFootRollAttr, mmCarryMesh, ".rotateX",  [-10, 10], [90, 0], 1 )

    #First create an attribute on the Root_Control
    cmds.select( "root_Control" )
    cmds.addAttr( longName="CarryVis", attributeType='enum', en = "on:off:", dv=0, k = 1 )
    mmCarryVis = "root_Control" + ".CarryVis"

    mmRF.mmCreateSDK( mmCarryVis, mmCarryMesh, ".visibility",  [0, 1], [1, 0], 1 )
    mmRF.mmCreateSDK( mmCarryVis, mmCarryControlName, ".visibility",  [0, 1], [1, 0], 1 )





######################

######################
#   Creating Arms on a general rig
#       This assumes that the rig has all the pieces of a human rig - probably easy enough to change out what gets space switched to,
#       but this also creates extra shoulder controls - which probably isn't needed on many general rigs (quads).
#clear selection
cmds.select( cl = 1)
    
#Create a counter to go through both arms
mmCounter = 0
    
mmArmName = "bob"
mmCurrentController = None

mmLastForearmController = ""

mmNewControlsCreated = []

#Create an extra arm controller for use of various ideas
mmExtraArmControllerBase = mmOF.createCube()

mmExtraArmControllerHand1 = mmOF.createHand()
mmExtraArmControllerHand1 = cmds.rename( mmExtraArmControllerHand1, "hand_iconA" )

cmds.scale( 0.25, 0.25, 0.25 )
cmds.move( -2, 0, 0 )

cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

mmExtraArmControllerHand2 = mmOF.createHand()
mmExtraArmControllerHand2 = cmds.rename( mmExtraArmControllerHand2, "hand_iconB" )

cmds.scale( -0.25, 0.25, 0.25 )
cmds.move( 2, 0, 0 )

cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

#Create an empty group and move shape nodes into it
mmExtraArmController = cmds.group (em = 1)

cmds.select( mmExtraArmControllerBase + "Shape", r = 1)
cmds.select( mmExtraArmControllerHand1 + "Shape", add = 1 )
cmds.select( mmExtraArmControllerHand2 + "Shape", add = 1 )
cmds.select( mmExtraArmController, add = 1 )

cmds.parent( r = 1, s = 1 )

mmExtraArmController = cmds.rename( mmExtraArmController, "armExtra_Control" )

cmds.delete( mmExtraArmControllerBase )
cmds.delete( mmExtraArmControllerHand1 )
cmds.delete( mmExtraArmControllerHand2 )

#Find location of Root so we can offset the control just made
mmTempPC = cmds.pointConstraint( mmRootControl, mmExtraArmController )

cmds.delete( mmTempPC )

cmds.parent( mmExtraArmController, mmRootControl )

cmds.select( mmExtraArmController, r = 1 )

cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)


mmRootControl = "root_Control"
mmLeftShoulderLoc = "leftShoulder_loc"
mmRightShoulderLoc = "rightShoulder_loc"

#Need to create the required attributes on both arm controls, as well as required bones and heirarchy
while mmCounter < 2:

    #Create or blank out a list
    mmCurrentArmControllers = [[""], [""]]

    #Select the proper Arm Info
    if (mmCounter == 0):

        #then select the right arm controls
        #****Should this be able to figure out different names?****
        mmArm_Shoulder_Loc = mmRightShoulderLoc
        mmArm_Shoulder_Control = mmRightShoulderLoc.split("_")[0] + "_Control"
        mmArmName = "right"
    
    elif (mmCounter == 1):

        #Select the left arm controls
        #****Should this be able to figure out different names?****
        mmArm_Shoulder_Loc = mmLeftShoulderLoc
        mmArm_Shoulder_Control = mmLeftShoulderLoc.split("_")[0] + "_Control"
        mmArmName = "left"


    #New - Grab stuff and store it as you do

    cmds.select( mmArm_Shoulder_Control )

    mmCurrentArmControllers[1][0] = cmds.listRelatives( p = 1 )[0]
    mmCurrentArmControllers[0][0] = cmds.listRelatives( mmCurrentArmControllers[1][0], p = 1 )[0]
    mmCurrentArmControllers.append( [mmArm_Shoulder_Control] )

    cmds.select( mmArm_Shoulder_Control )
    
    mmTempChildrenChecker = cmds.listRelatives( c = 1 )
    mmTempChildrenCollection = []

    for mmTempChild in mmTempChildrenChecker:

        mmNameChecker = mmTempChild.split("_")

        if ( mmNameChecker[1] == "Control"):

            mmTempChildrenCollection.append( mmTempChild )
    
    mmCurrentArmControllers.append( mmTempChildrenCollection )

    cmds.select( mmCurrentArmControllers[3][0] )

    mmTempChildrenChecker = cmds.listRelatives( c = 1 )
    mmTempChildrenCollection = []

    for mmTempChild in mmTempChildrenChecker:

        mmNameChecker = mmTempChild.split("_")

        if ( mmNameChecker[1] == "Control"):

            mmTempChildrenCollection.append( mmTempChild )


    mmCurrentArmControllers.append( mmTempChildrenCollection )

    cmds.select( mmCurrentArmControllers[4][0] )

    mmTempChildrenChecker = cmds.listRelatives( c = 1 )
    mmTempChildrenCollection = []

    for mmTempChild in mmTempChildrenChecker:

        mmNameChecker = mmTempChild.split("_")

        if ( mmNameChecker[1] == "Control"):

            mmTempChildrenCollection.append( mmTempChild )

    mmCurrentArmControllers.append( mmTempChildrenCollection )

    '''
    #Guide for mmCurrentArmControllers
    0-Parent (torso)
    1-Clavicle
    2-Shoulder
    3-Fore Arm
    4-Hand
    5-fingers/thumb/weapon holder
    '''

    mmCurrentArmLocators = []

    #Make a dupe list of Locators
    for mmLocList in mmCurrentArmControllers:

        mmTempList = []

        for mmLoc in mmLocList:
            mmNameChecker = mmLoc.split( "_" )

            if ( len( mmNameChecker ) > 1 ):

                mmLocName = mmNameChecker[0] + "_loc"

                mmTempList.append( mmLocName )

        mmCurrentArmLocators.append( mmTempList )


    #Store current loc of forearm
    mmForearmPad = cmds.group( em = 1 )

    mmForearmPad = cmds.rename( mmCurrentArmControllers[3][0] + "_pad" )

    mmTempPC = cmds.pointConstraint( mmCurrentArmControllers[3][0], mmForearmPad, mo = 0 )

    cmds.delete( mmTempPC )

    cmds.select( mmCurrentArmControllers[3][0] )

    mmOldParent = cmds.listRelatives( p = 1 )[0]

    cmds.parent( mmCurrentArmControllers[3][0], mmForearmPad )
    cmds.parent( mmForearmPad, mmOldParent )

    #Set to world trans
    mmGWT.main()


    #Create a list with the things needed in the order needed.
    mmSelectList = []

    if ( mmArmName == "right" ):
        mmSelectList.append( mmCurrentArmControllers[2][0] )
        mmSelectList.append( mmRootControl )
        mmSelectList.append( "headExtra_Control" )
        mmSelectList.append( mmCurrentArmControllers[0][0] )
        mmSelectList.append( "pelvis_Control" )
        mmSelectList.append( mmExtraArmController )

        mmRF.spaceSwitcherMulti( 3, mmCurrentArmControllers[3][0], [mmForearmPad], mmSelectList )

        #Save the forearm for this arm to use on the next arm
        mmLastForearmController = mmCurrentArmControllers[3][0]
        mmLastHandController = mmCurrentArmControllers[4][0]

    elif ( mmArmName == "left" ):
        mmSelectList.append( mmCurrentArmControllers[2][0] )
        mmSelectList.append( mmRootControl )
        mmSelectList.append( "headExtra_Control" )
        mmSelectList.append( mmCurrentArmControllers[0][0] )
        mmSelectList.append( "pelvis_Control" )
        mmSelectList.append( mmLastForearmController )
        mmSelectList.append( mmLastHandController )
        mmSelectList.append( mmExtraArmController )

        mmRF.spaceSwitcherMulti( 3, mmCurrentArmControllers[3][0], [mmForearmPad], mmSelectList )

    ######################################
    #Use mmRF.handCreator() to create and connect hand icons
    ######################################

    cmds.select( mmCurrentArmControllers[4][0], r = 1 )
    #Select proper locs first, remove holder
    for mmObject in mmCurrentArmLocators[5]:
        #Do not select the holder
        if ( mmObject != "mainHand_loc" and mmObject != "offHand_loc" ):
            cmds.select( mmObject, add = 1 )

    #Run Hand Creator, passing it some info to help build
    mmNewControlsCreated = mmRF.handCreator( True, 1, 1, 1, "ZXY", "XYZ" )

    mmTrashParentHolder = []
    #Ensure that new controls are Parented in properly
    for mmControl in mmNewControlsCreated:
        mmTempSideChecker = mmControl.split("_")
        mmTempLen = len(mmTempSideChecker)
        if ( mmTempLen > 3 and mmTempSideChecker[mmTempLen - 2][0:6] == "Master" ):
            mmTempParent = cmds.listRelatives(mmControl, p = 1)[0]
            #print "mmTempParent1", mmTempParent
            
            mmTempParent = cmds.listRelatives(mmTempParent, p = 1)[0]
            #print "mmTempParent2", mmTempParent

            mmTrashParent = cmds.listRelatives(mmTempParent, p = 1)[0]
            #print "mmTrashParent", mmTrashParent

            cmds.parent( mmTempParent, mmCurrentArmControllers[4][0] )
            mmTrashParentHolder.append(mmTrashParent)

    mmTrashParentHolder = list(set(mmTrashParentHolder))

    for mmTrashParent in mmTrashParentHolder:
        cmds.delete(mmTrashParent)

    mmNewControlsCreated.append( mmExtraArmController )

    ######################################
    #Disconnect the Shoulder and reconnect as needed
    ######################################
    
    #need to delete the parent constraint holding the mesh in place with this control
    cmds.select( mmCurrentArmLocators[2][0] )
    mmTempRelatives = cmds.listRelatives( type = "transform" )

    #print "mmTempRelatives", mmTempRelatives
    for mmTempRelative in mmTempRelatives:
        mmChecker = mmTempRelative.split("_")

        mmLenChecker = len(mmChecker)

        if ( mmChecker[mmLenChecker-1][0:16] == "parentConstraint" ):

            cmds.delete(mmTempRelative)

    #Need to dupe the shoulder control and scale it down so it looks different
    mmCurrentShoulderName = mmCurrentArmControllers[2][0].split("_")[0]
    mmCurrentArmName = mmCurrentArmControllers[3][0].split("_")[0]

    cmds.select(cl = 1)

    cmds.duplicate(mmCurrentArmControllers[2][0], name = mmCurrentShoulderName + "_Minor_Control", rc = 1)

    cmds.select(mmCurrentShoulderName + "_Minor_Control")

    mmMinorShoulderControl = cmds.ls(sl = 1)[0]

    mmShoulderParent = cmds.listRelatives(mmMinorShoulderControl, p = 1)

    mmAllChildren = cmds.listRelatives(mmMinorShoulderControl, c = 1)

    #Delete other children nodes - don't want to create a duplicate of the entire arm
    for mmChild in mmAllChildren:
        if ( mmChild != mmMinorShoulderControl + "Shape" ):

            cmds.delete( mmChild )

    cmds.select(mmMinorShoulderControl)

    #Scale down so its offset from original control
    cmds.scale( 0.5, 0.5, 1.2 )

    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    mmMinorShoulderControlPad = mmOF.mmGroupInPlace( mmMinorShoulderControl )

    #Need to set the minor shoulder control to 0,0,0
    cmds.select(mmMinorShoulderControl)
    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    #Connect minor shoulder control into the rig        
    cmds.parentConstraint( mmMinorShoulderControl, mmCurrentArmLocators[2][0], mo = 1 )

    mmSelectList = []

    #Create a space switcher which defaults to On so it mimics all old animations
    #cmds.parent( mmMinorShoulderControlPad, mmCurrentArmControllers[2][0] )
    mmSelectList.append(mmCurrentArmControllers[2][0])
    mmSelectList.append(mmCurrentArmControllers[1][0])
    mmSelectList.append(mmRootControl)

    mmRF.spaceSwitcherMulti(3, mmMinorShoulderControl, [mmMinorShoulderControlPad], mmSelectList)
    
    '''
    #Guide for mmCurrentArmControllers
    0-Parent (torso)
    1-Clavicle
    2-Shoulder
    3-Fore Arm
    4-Hand
    5-fingers/thumb/weapon holder
    '''

    ######################################
    #Create Weapon Space Switcher
    ######################################
    for mmControl in mmCurrentArmControllers[5]:
        mmTempSideChecker = mmControl[0:4]

        #Create a list with the things needed in the order needed.
        mmSelectList = []

        #print "mmControl", mmControl

        if ( mmTempSideChecker == "main" or mmTempSideChecker == "offH" ):

            #Need to group the mmControl in place
            mmCreatedPad = mmOF.mmGroupInPlace(mmControl)

            #And then give it space switching
            mmSelectList.append( mmCurrentArmControllers[4][0] )
            mmSelectList.append( mmRootControl )
            mmSelectList.append( mmExtraArmController )

            mmRF.spaceSwitcherMulti( 3, mmControl, [mmCreatedPad], mmSelectList )

            #need to set control to 0,0,0
            cmds.select(mmControl)
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)



    mmCounter += 1

######################




"""