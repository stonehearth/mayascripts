"""

Function: mmMassConversionFunctions
Description: This file is a collection of functions which will help with mass conversion from 3DSMax to Maya.


"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.mel as mel
import time
import os
import pymel.core as pm
import pymel.core.uitypes as pmui
import subprocess

#Local
import mmScaleDownFrom3DSMax as mmSDF3M
import mmReturnFilepathOrFilename as mmRFOF
import mmOrganizationFunctions as mmOF
import mmSelectAnimatingParts as mmSAP
import mmRiggingFunctions as mmRF
import mmGetWorldTrans as mmGWT
import mmCreateLocAndParent as mmCLAP
import mmTransferAnimToReferencedRig as mmTATRR
import mmTransferAnimToDifferentRig as mmTATDR
import mmExportSkeletonAsJson as mmESAJ
import mmExportAnimationAsJson as mmEAAJ
import mmConvert3DSMaxRigToMayaRig as mmCM2M


######################################
############# GLOBALS ################
######################################

######################################
############# DEFINES ################
######################################



def main(*args):
    print "WIP"


'''
Need functions for calling the different versions
#Doesn't work, don't have enough information.
'''
# def mmQuickSaveFileAsRig():
#   mmQuickSaveFileAs("rig")

    
# def mmQuickSaveFileAsAnim():
#   mmQuickSaveFileAs("anim")
'''
This function should be run after the asset has been brought in from 3dsmax, it will simply open the 'save as' dialogue box.
It should then save the file as a name of the user's choosing (preferably with "ReferencedAnimRig_" at the beginning if it is a rig).
Rigs should be placed in the base creature folder - the same as the game folder structure - animations should be placed in that folder, under a separate folder
called "max_animconversions".  That will allow them to be found in the next script (hopefully).
The script will then clear Maya back to a new scene so it is ready for the next max import.
'''
def mmQuickSaveFileAs( mmTypeOfFile, *args ):

    #Do we need a way to determine rig versus anim on function call?
    # if (mmTypeOfFile == "rig"):
    #   print "Rig"
    # if (mmTypeOfFile == "anim"):
    #   print "Anim"
    #This doesn't help at all.. we don't have a filename or path : (.  Maybe could do a search of all files in the folder structure, but that would take a good long while.
    
    #---------------------------------------------
    
    #Open dialogue box asking for where to save
    #Need to save out the file as .MA
    
    #Ask the user where to save the rig.

    mmStartingDirectory = "C:/Radiant/stonehearth-assets/assets/models/entities/"
    mmDialogueCaption = "Please choose a name and decide where to save your file."
    
    
    #Open a dialogue box where user can input information
    mmRigFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 0, fileFilter = 'MA (*.ma)', selectFileFilter = 'MA (*.ma)', dir = mmStartingDirectory )
    #print mmRigFilename
    
    if (mmRigFilename):
        cmds.file( rename = mmRigFilename[0] )

        cmds.file( force = 1, save = 1, type = 'mayaAscii' )

    #---------------------------------------------

    #After saving, open a new file
    cmds.file( force = 1, new = 1 )


'''
This function should take the rig file which is currently being looked at, 
then find all animations in its folder structure,
then transfer all animations onto the rig file (currently open),
which will also export the file as part of that process,
then close and open the next file in that folder and repeat.
At the end it should pop a dialogue box open saying it has completed, and possibly which animations it has pushed out.
'''

def mmExportAllAnims(*args):

    #First the user must manually transfer all the animations for the particular rig
    #   from max to maya and save them in a folder called "max_animconversions" - mmSaveFileAs should help them do this.

    #Disable the viewport
    # Translation into python is easy, how to figure out the name of the panelayout is not
    #mel.eval("paneLayout -e -manage false $gMainPane")
    #cmds.refresh(suspend=True) #Works!

    #Find out the current file name
    mmRigFilepathAndFilename = cmds.file(q = 1, loc = 1)
    #print "mmRigFilepathAndFilename", mmRigFilepathAndFilename

    #Get the filepath
    mmMainFilepath = mmRFOF.main( str(mmRigFilepathAndFilename), 0 )
    #print "mmMainFilepath", mmMainFilepath

    #Get the file name
    mmMainFilename = mmRFOF.main( str(mmRigFilepathAndFilename), 1 )
    #print "mmMainFilepath", mmMainFilepath

    #Check if a folder called "max_animconversions" exists
    mmAnimFolderCheck = cmds.file( mmMainFilepath + "max_animconversions/", q = 1, ex = 1 )
    #print "mmAnimFolderCheck", mmAnimFolderCheck

    #If the "max_animconversions" folder doesn't exist, stop - we have nothing to do.
    if ( mmAnimFolderCheck == False ):
        print "max_animconversions folder not found, canceling script"
        return

    else:

        mmExportedPathsList = []
        mmExportedPaths = ""
        
        #If it does, we need to:
        #   First export the skeleton.
        #   Find out how many files are in the max_animconversions folder.
        #   Load in every file which is in the folder (individually).
        #   Run the transfer to referenced rig script - which also exports the animations.
        #   And ensure that the file is being saved as the proper name in the proper location.

        #---------------------------------------------
    

        #   First export the skeleton.
        mmESAJ.main(False)
        mmExportedPaths = "rig: " + mmMainFilename + "\n"

        #   Ensure that the file is being saved.
        #Save the file
        cmds.file( save = 1, force = 1 )

        #---------------------------------------------
    

        #   Find out how many files are in the max_animconversions folder.
        for item in os.listdir( mmMainFilepath + "max_animconversions/" ):
            #print "item", item

            mmAnimFilePath = mmMainFilepath + "max_animconversions/" + item
            #print "mmAnimFilePath", mmAnimFilePath

            #---------------------------------------------
    
            #   Load in every file which is in the folder (individually).
            #Open the file
            cmds.file( mmAnimFilePath, open = 1)

            #Disable the viewport
            #mel.eval("paneLayout -e -manage false $gMainPane")
            #cmds.refresh(suspend=True)

            #---------------------------------------------
    
            #   Run the transfer to referenced rig script - which also exports the animations.
            #Run the anim transfer to rig script
            mmTATRR.main( str(mmRigFilepathAndFilename), str(mmAnimFilePath) )

            #---------------------------------------------
    
            #   And ensure that the file is being saved.
            #Save the file
            cmds.file( save = 1, force = 1 )

            mmExportedPathsList.append(item)

        
        #---------------------------------------------
    
        for mmPath in mmExportedPathsList:
            mmExportedPaths = mmExportedPaths + "anim: " + mmPath + "\n"

        #Open the file
        cmds.file( mmRigFilepathAndFilename, open = 1)

        #---------------------------------------------
        
        #display to the user that their export is complete, and what was exported.
        cmds.confirmDialog( title = 'Export Complete', message = 'File(s) Exported:\n' + 
            mmExportedPaths + '\nFilepath exported to:\n' + mmMainFilepath + "animations/"
            , button = ['OK'], defaultButton = 'OK' )


    #Re-enable the viewport
    # Translation into python is easy, how to figure out the name of the panelayout is not
    #mel.eval("paneLayout -e -manage true $gMainPane")
    #cmds.refresh(suspend=False)


'''
Need to break apart the previous function into separate functions which call themselves in order

This function should take the rig file which is currently being looked at, 
then find all animations in its folder structure,
then transfer all animations onto the rig file (currently open),
which will also export the file as part of that process,
then close and open the next file in that folder and repeat.
At the end it should pop a dialogue box open saying it has completed, and possibly which animations it has pushed out.
'''
def mmConvAndExportAllAnimsSequential_1(*args):

    #First the user must manually transfer all the animations for the particular rig
    #   from max to maya and save them in a folder called "max_animconversions" - mmSaveFileAs should help them do this.

    #Disable the viewport
    # Translation into python is easy, how to figure out the name of the panelayout is not
    #mel.eval("paneLayout -e -manage false $gMainPane")
    #cmds.refresh(suspend=True) #Works!

    #Find out the current file name
    mmRigFilepathAndFilename = cmds.file(q = 1, loc = 1)
    #print "mmRigFilepathAndFilename", mmRigFilepathAndFilename

    #Get the filepath
    mmMainFilepath = mmRFOF.main( str(mmRigFilepathAndFilename), 0 )
    #print "mmMainFilepath", mmMainFilepath

    #Check if a folder called "max_animconversions" exists
    mmAnimFolderCheck = cmds.file( mmMainFilepath + "max_animconversions/", q = 1, ex = 1 )
    #print "mmAnimFolderCheck", mmAnimFolderCheck

    #If the "max_animconversions" folder doesn't exist, stop - we have nothing to do.
    if ( mmAnimFolderCheck == False ):
        print "max_animconversions folder not found, canceling script"
        return

    else:

        mmExportedPathsList = []
        #If it does, we need to:
        #   First export the skeleton.
        #   Find out how many files are in the max_animconversions folder.
        #   Load in every file which is in the folder (individually).
        #   Run the transfer to referenced rig script - which also exports the animations.
        #   And ensure that the file is being saved as the proper name in the proper location.

        #---------------------------------------------
    

        #   First export the skeleton.
        mmESAJ.main(False)
        #   Ensure that the file is being saved.
        #Save the file
        cmds.file( save = 1, force = 1 )

        #---------------------------------------------
    

        #   Find out how many files are in the max_animconversions folder.
        for item in os.listdir( mmMainFilepath + "max_animconversions/" ):
            #print "item", item

            if (item != ".mayaSwatches"):

                mmExportInfoList = []

                mmAnimFilePath = mmMainFilepath + "max_animconversions/" + item
                #print "mmAnimFilePath", mmAnimFilePath
                mmExportInfoList.append( item )
                mmExportInfoList.append( mmAnimFilePath )
                mmExportInfoList.append( mmRigFilepathAndFilename )
                mmExportInfoList.append( mmMainFilepath )

                #Store all animation filenames in a list
                mmExportedPathsList.append(mmExportInfoList)

        #Next we need to end with a call to a function which will call itself until it is done.. right?
        mmIterate = 0
        mmConvAndExportAllAnimsSequential_2 ( mmExportedPathsList, mmIterate )



def mmConvAndExportAllAnimsSequential_2( mmExportedPathsList = [], mmIterate = None, *args):

    #---------------------------------------------
    #This loads in an animation file and runs the transfer to referenced rig script
    #print "mmExportedPathsList", mmExportedPathsList

    mmAnimName = mmExportedPathsList[mmIterate][0]
    mmAnimFilePath = mmExportedPathsList[mmIterate][1]
    mmRigFilepathAndFilename = mmExportedPathsList[mmIterate][2]
    mmMainFilepath = mmExportedPathsList[mmIterate][3]
    #print "mmRigFilepathAndFilename", mmRigFilepathAndFilename


    #---------------------------------------------

    #   Load in the next file which is in the folder.
    #Open the file
    cmds.file( mmAnimFilePath, open = 1)

    #Disable the viewport
    #mel.eval("paneLayout -e -manage false $gMainPane")
    #cmds.refresh(suspend=True)

    #---------------------------------------------
    #---------------------------------------------

    #   Run the transfer to referenced rig script - which also exports the animations.
    ############################################
    #Instead need to transplant the anim transfer script here so we actually wait for its functionality - don't see another way to do this
    #mmTATRR.main( str(mmRigFilepathAndFilename), str(mmAnimFilePath) )

    mmCM2M.mmFixUI()

    
    #Cycle the Atom Export window just to make sure it is alive and working
    mel.eval( "ExportAnimOptions;" )
    mel.eval( "performExportAnim 1;" )
    mel.eval( "hideOptionBox;" )

    #Grab everything that should be selected
    selectionList = []
    selectionList = mmSAP.main()

    #print "selectionList", selectionList
    
    #create lists for use later
    mmOriginalBones = list(selectionList)
    mmProperBoneList = []
    mmCopyLocList = []
    mmModifiedNames = []

    mmTransferFromMaxBool = True

    mmSearchingSuffix = "_Control"

    mmTempLocSuffix = "_TransferLoc"
    
    #First need to ensure the scale of the animation is 1 so transfer works properly

    objectName = 'root'
    if objectName in selectionList:
        
        #clear selection
        cmds.select (cl = 1)
         
        #select only the root
        cmds.select (objectName)

        #Scale down the selected value
        mmSDF3M.main(objectName)


    #Find out total number of frames

    #Store the original time before running the script
    mmOriginalTime = cmds.currentTime( query=True )

    #Find First Frame of Timeline
    mmFirstFrame = cmds.playbackOptions( minTime=1, query=True )

    #Find Last Frame of Timeline
    mmLastFrame = cmds.playbackOptions( maxTime=1, query=True )
    #mmLastFrame -= 1

    #Find Total Frames
    mmTotalFrames = mmLastFrame - mmFirstFrame

    #Set animation to first frame
    mmCurrentTime = cmds.currentTime( mmFirstFrame, update=False )


    #Need to parent constrain a locator to every bone.. then pull animation out of these attached locators.
    #  This is because the axis are expected to be rotated 90 degrees in X
    
    #Clear out duplicates & Sort
    #Just converting the list to a "set" and back to a "list" causes all duplicates to be removed.
    mmOriginalBones = list(set(mmOriginalBones))
    mmOriginalBones.sort()


    #---------------------------------------------

    ######################################
    #Think I need to import the new rig now so I can use it for the Transfer_Loc rig creation
    ######################################

    #Had to move this upwards in the script because I need the information sooner, *should* be no issues.
    #  The list of selected items was made before this was pulled in, should be ok.


    #use the passed in information

    # mmAnimFilePath
    # mmRigFilepathAndFilename



    mmSavedDirectory = mmRFOF.main( mmRigFilepathAndFilename, 0 )
    
    mmRigNamespace = mmRFOF.main( mmRigFilepathAndFilename, 1 )



    #Need to import Referenced Rig
    #Original Mel:
    #file -r -type "mayaAscii"  -ignoreVersion -gl -mergeNamespacesOnClash false -namespace "ReferencedAnimRig_Male" -options "v=0;" "C:/Radiant/stonehearth-assets/assets/models/entities/humans/male/ReferencedAnimRig_Male.ma";
    cmds.file( mmRigFilepathAndFilename, r = 1, type = "mayaAscii", ignoreVersion = 1, gl = 1, mergeNamespacesOnClash = False, namespace = mmRigNamespace, options = "v=0;" )

    

    #Need to save bones and parents
    mmNewRigStoreArray = []
    mmCounterA = 0

    #Select all of the original selection bones
    for objectCounter in mmOriginalBones:
        #print "objectCounter", objectCounter

        #While we are here, lets check to see if there are non suffix items.
        #We don't know if this is an animation from 3dsmax where the suffixs do not exist, or one from Maya where they do. 
        #If this is TRUE, then it means we have Controls in the scene, and we should be transfering from THEM instead of geo,
        #And we save the names for later to replace the original bones names.

        #####################################
        #I dont think this will pick up referenced assets - it isn't searching for names with ":" in front.
        #  Maybe we should be checking for both referenced and not?  or.. not really, non-referenced controls shouldn't happen.
        #####################################

        mmNameChecker = objectCounter.split(":")

        if ( len(mmNameChecker) > 1 ):

            mmProperBoneName = mmNameChecker[1].split("_")

            mmTempSuffix = mmSearchingSuffix.split("_")[1]

            if ( len(mmProperBoneName) > 1 and mmProperBoneName[1] == mmTempSuffix ):
                mmProperBoneList.append(mmProperBoneName[0])
                print "Added Proper Bone: ", mmProperBoneName[0]

                mmTransferFromMaxBool = False

        else:

            #Each new bone is given an array to store its name and its parent.
            mmNewBoneStoreArray = []

            #Store the name of the bone into the array, as well as its parent.
            objectCounterNewName = objectCounter + mmTempLocSuffix
            mmNewBoneStoreArray.append(objectCounterNewName)

            objectParent = cmds.listRelatives( objectCounter, p = 1 )

            #Also create the names of the bones which the rig will have.
            mmModifiedName = mmRigNamespace + ":" + objectCounter + mmSearchingSuffix
            mmModifiedNames.append(mmModifiedName)
            #print "mmModifiedNames[mmCounterA]", mmModifiedNames[mmCounterA]
     
            if ( objectParent != None ):
                objectParent[0] += mmTempLocSuffix

                mmNewBoneStoreArray.append(objectParent[0])
                
            else:
                mmNewBoneStoreArray.append(None)

            mmNewRigStoreArray.append(mmNewBoneStoreArray)

            #print "mmNewBoneStoreArray", mmNewBoneStoreArray

            mmCounterA += 1
            mmTransferFromMaxBool = True

    #Clear out duplicates & Sort
    #Just converting the list to a "set" and back to a "list" causes all duplicates to be removed.
    
    if ( mmTransferFromMaxBool == False ): 
        mmProperBoneList = list(set(mmProperBoneList))
        mmProperBoneList.sort()
    
    elif ( mmTransferFromMaxBool == True ):
        mmCopyLocList = list(set(mmCopyLocList))
        mmCopyLocList.sort()
        mmModifiedNames = list(set(mmModifiedNames))
        mmModifiedNames.sort()

    mmRootBone = ""
    mmRootTempLoc = ""

    if (mmTransferFromMaxBool):
        mmCounterB = 0

        for objectCounter in mmOriginalBones:
            #Create a locator and parent it to the correct bone so it mimics the movement of its parent, then transfer that animation over.
            #This assumes that my rig is clean - but my rigs are NOT clean, I know this.  So instead, I need a way to create these locators,
            #  then pin them in place where they SHOULD be, then move them to where they ARE, THEN transfer the animation.
            mmTempLoc = cmds.spaceLocator( n = objectCounter + mmTempLocSuffix )[0]

            ####################################
            ####################################
            #This is where I need to constrain to the rig, freeze transforms, then re-constrain to the original meshes (and do not freeze transforms).
            #Hopefully this gets us to the correct location, and proper animation after that.  NOPE
            ####################################
            ####################################

            mmTempPC1 = cmds.pointConstraint( mmModifiedNames[mmCounterB], mmTempLoc, mo = 0 )
            cmds.delete(mmTempPC1)

            cmds.select(mmTempLoc)

            mmCopyLocList.append( mmTempLoc )

            #This may not be needed if the root temploc is set to world space
            # if (objectCounter == "root"):
            #    mmRootBone = objectCounter
            #    mmRootTempLoc = mmModifiedNames[mmCounterB]

            mmCounterB += 1


    #Next need to take the templocs and parent them appropriately
    objectStoredArray= []


    for rigStoredArray in mmNewRigStoreArray:
     
        #print objectStoredArray

        if ( rigStoredArray[1] != None ):
            cmds.parent( rigStoredArray[0], rigStoredArray[1])

        if ( rigStoredArray[0] != "root" + mmTempLocSuffix ):
            cmds.select(rigStoredArray[0])
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)



    #Next need to move the templocs to where they should be in space
    ####################################
    #I'm sure this is horrible, because they are parented, and now we are not maintaining offset constrainting them : /
    ####################################

    #FIRST: the root must line up


    mmCounterC = 0
    while mmCounterC < len(mmOriginalBones):
        
        #Padding it wont help : (
        #mmLocPad = mmOF.mmGroupInPlace( mmCopyLocList[mmCounterC] )

        mmTempPC2 = cmds.parentConstraint( mmOriginalBones[mmCounterC], mmCopyLocList[mmCounterC], mo = 0 )
        cmds.delete(mmTempPC2)

        #Must fix the rotation from Max somehow
        cmds.select(mmCopyLocList[mmCounterC])
        
        #Arbitrary 90 degree rotation isn't benefical, just does wonky stuff.  What is actually happening?
        cmds.rotate( 90, 0, 0, r = 1, os = 1 )

        #Try swapping Y and Z values (probably wont work, but trying it)
        #mmBoneRot = cmds.getAttr(mmOriginalBones[mmCounterC] + ".rotate")
        #print "mmBoneRot", mmBoneRot
        #cmds.rotate( mmBoneRot[0][0], -mmBoneRot[0][2], mmBoneRot[0][1], r =1 )

        mmTempPC3 = cmds.parentConstraint( mmOriginalBones[mmCounterC], mmCopyLocList[mmCounterC], mo = 1 )

        mmCounterC += 1 

    #This selects all temp locs and export the animation.
    if (mmTransferFromMaxBool):

        cmds.select(cl = 1)

        for mmTempLoc in mmCopyLocList:

            cmds.select( mmTempLoc, add = True )



    #Else: use the passed in information
    mmSavedDirectory = mmRFOF.main( mmRigFilepathAndFilename, 0 )
    
    mmRigNamespace = mmRFOF.main( mmRigFilepathAndFilename, 1 )

    mmExportImportFilename = mmRFOF.main( mmAnimFilePath, 1 )
    
    mmFullDirectoryPathFiletype = mmSavedDirectory + "atom_exports/" + mmExportImportFilename + ".atom"

    #-----------------------------

    ############
    #Need to make sure that the  atom_exports folder exists, and if not, create it.
    ############

    for item in os.listdir( mmMainFilepath ):
        if ( item != "atom_exports" ):
            cmds.sysFile( mmMainFilepath + "atom_exports/", makeDir=True )

    #-----------------------------

    #Export animation to specified file.
    mmMelExportAtomLine = 'doExportAtom(1,{ "' + mmSavedDirectory + "atom_exports/" + mmExportImportFilename + '" });'
    #print mmMelExportAtomLine
    mel.eval(mmMelExportAtomLine)
    
    #mel.eval('fileCmdCallback;')




    #print "mmOriginalBones", mmOriginalBones
    #print "mmProperBoneList", mmProperBoneList

    #Next we need to copy the animations from the original Rig onto the new Replacement Rig

    
    #---------------------------------------------
    
    #remove the gathering of selectionList again
    #selectionList = cmds.ls(orderedSelection = True)
    
    #Clear selection
    cmds.select( cl = 1 )
    
    #Create counter and set to 0
    mmCounterA = 0
    
    #Check to see if there are any "mmProperBoneName"s in the mmProperBoneList
    #Take all the original bones and select the Suffix version of them within the Referenced Rig file
    
    for mmBone in mmOriginalBones:
        
        if ( mmTransferFromMaxBool == True ):

            # mmModifiedName = mmRigNamespace + ":" + mmBone + mmSearchingSuffix
            # mmModifiedNames.append(mmModifiedName)
            # print "mmModifiedNames[mmCounterA]", mmModifiedNames[mmCounterA]
        
            cmds.select( mmModifiedNames[mmCounterA], add = True )
        else:

            ###################################
            #This looks broken - unsure what this was even supposed to do.. why would I only want to select one bone?
            ###################################

            if (mmCounterA == 1):

                cmds.select( mmBone, add = True )
        
        mmCounterA += 1
    
    mmSelectedNames = cmds.ls(sl = 1)
    #print "mmSelectedNames - right before import: ", mmSelectedNames
    
    
    #***Forcing test, these lines are trash in the long run***
    #mmExportImportFilename = "run"
    #mmRigNamespace = "ReferencedAnimRig_Male"
    #mmFullDirectoryPathFiletype = "C:/Users/mmalley/Documents/Work/AnimationExports/run.atom"
    #mmATOMOriginalName = "HumanMaleOriginal"
    
    
    if ( mmTransferFromMaxBool == True ):

        mmATOMImportPrefix = mmRigNamespace + ":"
        mmATOMImportSuffix = ""
        mmSearchName = mmTempLocSuffix
        mmReplaceName = mmSearchingSuffix
        
    else: 
        mmATOMImportPrefix = mmRigNamespace + ":"
        mmATOMImportSuffix = ""
        mmSearchName = ""
        mmReplaceName = ""
    
    # print mmExportImportFilename
    # print mmRigNamespace
    # print mmFullDirectoryPathFiletype[0]
    # print mmATOMOriginalName
    # print "mmATOMImportPrefix", mmATOMImportPrefix
    # print "mmATOMImportSuffix", mmATOMImportSuffix
    
    '''
    #not working
    #mmCompileMelCommandForImportAnimations = 'file -import -type "atomImport" -ra true -namespace "' + mmExportImportFilename + '" -options ";;targetTime=3;option=insert;match=string;;template=' + mmATOMOriginalName + ';;selected=template;view=0;search=;replace=;prefix=' + mmATOMImportPrefix + ';suffix=' + mmATOMImportSuffix + ';mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;" "' + mmFullDirectoryPathFiletype + '";'
    #removing template
    mmCompileMelCommandForImportAnimations = 'file -import -type "atomImport" -ra true -namespace "' + mmExportImportFilename + '" -options ";;targetTime=3;option=insert;match=string;;selected=selectedOnly;search=;replace=;prefix=' + mmATOMImportPrefix + ';suffix=' + mmATOMImportSuffix + ';mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;" "' + mmFullDirectoryPathFiletype[0] + '";'
    
    #print mmCompileMelCommandForImportAnimations
    
    #Importing animations onto new Locator Rig
    mel.eval(mmCompileMelCommandForImportAnimations)

    mel.eval("fileCmdCallback;")
    
    #mel.eval('file -import -type "atomImport" -ra true -namespace "run" -options ";;targetTime=3;option=insert;match=string;;template=HumanMaleOriginal;;selected=template;search=;replace=;prefix=ReferencedAnimRig_Male:;suffix=_loc;mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;" "C:/Users/mmalley/Documents/Work/AnimationExports/run.atom";')
    #Trying to find python equivalent, Failing
    #cmds.file( import = True, type = "atomImport", ra = True, namespace = "idle_breathe", options = ";;targetTime=3;option=insert;match=string;selected=template;suffix='_loc';mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;" "C:/Users/mmalley/Documents/Work/AnimationExports/idle_breathe/idle_breathe.atom")
    '''


    #Find out total number of frames

    #Store the original time before running the script
    mmOriginalTime = cmds.currentTime( query=True )

    #Find First Frame of Timeline
    mmFirstFrame = cmds.playbackOptions( minTime=1, query=True )

    #Find Last Frame of Timeline
    mmLastFrame = cmds.playbackOptions( maxTime=1, query=True )
    #mmLastFrame -= 1

    #Find Total Frames
    mmTotalFrames = mmLastFrame - mmFirstFrame

    # #Set animation to first frame
    # mmCurrentTime = cmds.currentTime( mmFirstFrame, update=False )


    #---------------------------------------------
    
    #Copying from 'mmTransferAnimToDifferentRig'
    #Re-select the desired components

    #print "mmFullDirectoryPathFiletype", mmFullDirectoryPathFiletype

    #Should this be mmFullDirectoryPathFiletype[0]? - NOPE!?!?!!  I dont know, it works now.
    mmImportAnimFilePath = mmFullDirectoryPathFiletype

    mmCompiledOptionsForImportAnimations = ";;targetTime=3;option=insert;match=string;;selected=selectedOnly;search=" + mmSearchName + ";replace=" + mmReplaceName + ";prefix=" + mmATOMImportPrefix + ";suffix=" + mmATOMImportSuffix + ";mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;"

    #Importing animations onto new Rig
    cmds.file( mmImportAnimFilePath, i = 1, type = "atomImport", ra = 1, namespace = "run", options = mmCompiledOptionsForImportAnimations )

    cmds.viewFit( all = True )
    
    #---------------------------------------------
    #Try checking what the current frame is and how long has passed

    mmRunTheLoop = True
    mmLastFrame = mmOriginalTime

    while (mmRunTheLoop):
        time.sleep(.1)
        mmCurrentFrame = cmds.currentTime( query=True )
        if (mmCurrentFrame == mmLastFrame):
            time.sleep(.1)
            if (mmCurrentFrame == mmLastFrame):
                mmRunTheLoop = False

        mmLastFrame = mmCurrentFrame

    #---------------------------------------------
    
    #Need to delete old 3dsmax Rig
    
    #Need to clear selection
    cmds.select( cl = 1 )
    
    #Take all the original bones and delete them - because we just brought in a replacement
    for objectCounter in mmOriginalBones:
        
        
        cmds.select( objectCounter, add = True )
        
        #Check for Parent Pads as well
        mmAreThereParents = cmds.listRelatives(objectCounter, p = 1)

        if (mmAreThereParents):

            cmds.select( mmAreThereParents[0], add = True )

    cmds.delete()

    
    #Also need to delete the created temp locator rig
    for mmTempLoc in mmNewRigStoreArray:
        
        cmds.select( mmTempLoc[0], add = True )
        
    cmds.delete()
    

    #---------------------------------------------
    #Clean Up

    #Reset time to original frame
    cmds.currentTime( mmOriginalTime )
    

    
    #---------------------------------------------
    
    #Need to save out the file as .MA
    #Just place it in the "Animations" folder under where the rig was saved out.
    mmNewAnimFilenameAndFilepath = mmSavedDirectory + "animations/" + mmExportImportFilename + ".ma"
    
    cmds.file( rename = mmNewAnimFilenameAndFilepath )
    
    cmds.file( force = 1, save = 1, type = 'mayaAscii' )

    
    #---------------------------------------------
    
    #Export an animation as well
    mmEAAJ.main(False)
    
    #---------------------------------------------

    #   And ensure that the file is being saved.
    #Save the file
    cmds.file( save = 1, force = 1 )

    #---------------------------------------------
    
    #Need to check if we should call ourself or the end function
    if ( len(mmExportedPathsList) == mmIterate + 1 ):
        #Then call the final function
        mmConvAndExportAllAnimsSequential_3 ( mmExportedPathsList )

    else:
        #call itself again with then next iterate loaded
        mmConvAndExportAllAnimsSequential_2 ( mmExportedPathsList, mmIterate + 1 )


def mmConvAndExportAllAnimsSequential_3( mmExportedPathsList = [], *args):
    #---------------------------------------------
    #This re-loads the rig, and informs the user that the script has finished its work.
    mmExportedPaths = ""

    mmRigFilepathAndFilename = mmExportedPathsList[0][2]

    #Get the filepath
    mmMainFilepath = mmRFOF.main( str(mmRigFilepathAndFilename), 0 )
    #print "mmMainFilepath", mmMainFilepath

    #Get the file name
    mmMainFilename = mmRFOF.main( str(mmRigFilepathAndFilename), 1 )
    #print "mmMainFilepath", mmMainFilepath

    mmExportedPaths = "rig: " + mmMainFilename + "\n"

    print "mmExportedPathsList", mmExportedPathsList
    for mmList in mmExportedPathsList:
        mmAnimName = mmList[0]
        mmAnimFilePath = mmList[1]

        mmExportedPaths = mmExportedPaths + "anim: " + mmAnimName + "\n"

    #Open the file
    cmds.file( mmRigFilepathAndFilename, open = 1)

    #---------------------------------------------
    
    #display to the user that their export is complete, and what was exported.
    cmds.confirmDialog( title = 'Export Complete', message = 'File(s) Exported:\n' + 
        mmExportedPaths + '\nFilepath exported to:\n' + mmMainFilepath + "animations/"
        , button = ['OK'], defaultButton = 'OK' )


    #Re-enable the viewport
    #This actually shouldn't be needed, but just in case.
    # Translation into python is easy, how to figure out the name of the panelayout is not
    #mel.eval("paneLayout -e -manage true $gMainPane")
    #cmds.refresh(suspend=False)


def mmFixBrokenViewport(*args):
    
    cmds.refresh(suspend=False)


'''
This function will export all animations from this folder structure without converting them from the 3dsmax anim files.
'''

def mmExportAllAnimsSequential_1(*args):

    #First the user must manually transfer all the animations for the particular rig
    #   from max to maya and save them in a folder called "max_animconversions" - mmSaveFileAs should help them do this.

    #Disable the viewport
    # Translation into python is easy, how to figure out the name of the panelayout is not
    #mel.eval("paneLayout -e -manage false $gMainPane")
    #cmds.refresh(suspend=True) #Works!

    #Find out the current file name
    mmRigFilepathAndFilename = cmds.file(q = 1, loc = 1)
    #print "mmRigFilepathAndFilename", mmRigFilepathAndFilename

    #Get the filepath
    mmMainFilepath = mmRFOF.main( str(mmRigFilepathAndFilename), 0 )
    #print "mmMainFilepath", mmMainFilepath

    #Check if a folder called "max_animconversions" exists
    mmAnimFolderCheck = cmds.file( mmMainFilepath + "animations/", q = 1, ex = 1 )
    #print "mmAnimFolderCheck", mmAnimFolderCheck

    #If the "max_animconversions" folder doesn't exist, stop - we have nothing to do.
    if ( mmAnimFolderCheck == False ):
        print "animation folder not found, canceling script"
        return

    else:

        mmExportedPathsList = []
        #If it does, we need to:
        #   First export the skeleton.
        #   Find out how many files are in the animations folder.
        #   Load in every file which is in the folder (individually).
        #   Run the transfer to referenced rig script - which also exports the animations.
        #   And ensure that the file is being saved as the proper name in the proper location.

        #---------------------------------------------
    

        #   First export the skeleton.
        mmESAJ.main(False)
        #   Ensure that the file is being saved.
        #Save the file
        cmds.file( save = 1, force = 1 )

        #---------------------------------------------
    

        #   Find out how many files are in the animations folder.
        for item in os.listdir( mmMainFilepath + "animations/" ):
            # print "item", item

            mmNameChecker = item.split(".")

            if (len(mmNameChecker) > 1 and mmNameChecker[1] == "ma" and item != ".mayaSwatches"):

                mmExportInfoList = []

                mmAnimFilePath = mmMainFilepath + "animations/" + item
                #print "mmAnimFilePath", mmAnimFilePath
                mmExportInfoList.append( item )
                mmExportInfoList.append( mmAnimFilePath )
                mmExportInfoList.append( mmRigFilepathAndFilename )
                mmExportInfoList.append( mmMainFilepath )

                #Store all animation filenames in a list
                mmExportedPathsList.append(mmExportInfoList)

        #Next we need to end with a call to a function which will call itself until it is done.. right?
        mmIterate = 0
        mmExportAllAnimsSequential_2 ( mmExportedPathsList, mmIterate )


def mmExportAllAnimsSequential_2( mmExportedPathsList = [], mmIterate = None, *args):

    #---------------------------------------------
    #This loads in an animation file and runs the transfer to referenced rig script
    #print "mmExportedPathsList", mmExportedPathsList

    mmAnimName = mmExportedPathsList[mmIterate][0]
    mmAnimFilePath = mmExportedPathsList[mmIterate][1]
    mmRigFilepathAndFilename = mmExportedPathsList[mmIterate][2]
    mmMainFilepath = mmExportedPathsList[mmIterate][3]
    #print "mmRigFilepathAndFilename", mmRigFilepathAndFilename


    #---------------------------------------------

    #   Load in the next file which is in the folder.
    #Open the file
    # print "mmAnimFilePath", mmAnimFilePath
    cmds.file( mmAnimFilePath, open = 1)

    #---------------------------------------------
    
    #Export an animation as well
    mmEAAJ.main(False)
    
    #---------------------------------------------

    #   And ensure that the file is being saved.
    #Save the file
    cmds.file( save = 1, force = 1 )

    #---------------------------------------------
    
    #Need to check if we should call ourself or the end function
    if ( len(mmExportedPathsList) == mmIterate + 1 ):
        #Then call the final function
        mmExportAllAnimsSequential_3 ( mmExportedPathsList )

    else:
        #call itself again with then next iterate loaded
        mmExportAllAnimsSequential_2 ( mmExportedPathsList, mmIterate + 1 )


def mmExportAllAnimsSequential_3( mmExportedPathsList = [], *args):
    #---------------------------------------------
    #This re-loads the rig, and informs the user that the script has finished its work.
    mmExportedPaths = ""

    mmRigFilepathAndFilename = mmExportedPathsList[0][2]

    #Get the filepath
    mmMainFilepath = mmRFOF.main( str(mmRigFilepathAndFilename), 0 )
    #print "mmMainFilepath", mmMainFilepath

    #Get the file name
    mmMainFilename = mmRFOF.main( str(mmRigFilepathAndFilename), 1 )
    #print "mmMainFilepath", mmMainFilepath

    mmExportedPaths = "rig: " + mmMainFilename + "\n"

    # print "mmExportedPathsList", mmExportedPathsList
    for mmList in mmExportedPathsList:
        mmAnimName = mmList[0]
        mmAnimFilePath = mmList[1]

        mmExportedPaths = mmExportedPaths + "anim: " + mmAnimName + "\n"

    #Open the file
    cmds.file( mmRigFilepathAndFilename, open = 1)

    #---------------------------------------------
    
    #display to the user that their export is complete, and what was exported.
    cmds.confirmDialog( title = 'Export Complete', message = 'File(s) Exported:\n' + 
        mmExportedPaths + '\nFilepath exported to:\n' + mmMainFilepath + "animations/"
        , button = ['OK'], defaultButton = 'OK' )


    #Re-enable the viewport
    #This actually shouldn't be needed, but just in case.
    # Translation into python is easy, how to figure out the name of the panelayout is not
    #mel.eval("paneLayout -e -manage true $gMainPane")
    #cmds.refresh(suspend=False)


'''
This function will transfer animations from one rig onto another.  They must have the same names (or animation will not transfer),
however, they should be able to be have similarities between the two rigs and only the similarities should transfer - but it needs to be tested.
'''

def mmTransferAndExportAllAnims(*args):

    #First the user must manually transfer all the animations for the particular rig
    #   from max to maya and save them in a folder called "max_animconversions" - quicksavefileas should help them do this.

    #Need to ask the user what rig they want to transfer these animations onto.

    #Ask the user what Rig should be referenced in and have animation applied to.
    mmStartingDirectory = "C:/Radiant/stonehearth-assets/assets/models"
    mmDialogueCaption = "Please select the replacement Rig to Reference in and apply animation to."
    mmRigNamespace = "ReferencedAnimRig_Male"

    #Open a dialogue box where user can input information
    mmNewRigFilepathAndFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 1, fileFilter = 'MA (*.ma)', selectFileFilter = 'MA (*.ma)', dir = mmStartingDirectory )

    mmNewRigFilepath = mmRFOF.main( mmNewRigFilepathAndFilename, 0 )

    mmNewRigFilename = mmRFOF.main( mmNewRigFilepathAndFilename, 1 )

    #Find out the Old file name
    mmOldRigFilepathAndFilename = cmds.file(q = 1, loc = 1)

    #Get the filepath
    mmOldRigFilepath = mmRFOF.main( str(mmOldRigFilepathAndFilename), 0 )

    #Get the file name
    mmOldRigFilename = mmRFOF.main( str(mmOldRigFilepathAndFilename), 1 )

    #Check if a folder called "animations" exists for the Old folder structure
    mmOldRigAnimFolderCheck = cmds.file( mmOldRigFilepath + "animations/", q = 1, ex = 1 )

    #If the "animations" folder doesn't exist, stop - we have nothing to do.
    if ( mmOldRigAnimFolderCheck == False ):
        print "No Animations folder to copy from, canceling script."
        return

    else:

        mmExportedPathsList = []
        mmExportedPaths = ""
        
        #If it does, we need to:
        #   Find out how many files are in the animations folder.
        #   Load in every file which is in the folder (individually).
        #   Run the transfer to referenced rig script - which also exports the animations.
        #   And ensure that the file is being saved as the proper name in the proper location.

        #---------------------------------------------
    
        #   Find out how many files are in the max_animconversions folder.
        for item in os.listdir( mmOldRigFilepath + "animations/" ):

            mmNameChecker = item.split(".")

            if ( len(mmNameChecker) > 1 and mmNameChecker[1] == "ma" ):

                mmOldAnimFilePath = mmOldRigFilepath + "animations/" + item

                #---------------------------------------------
        
                #   Load in every file which is in the folder (individually).
                #Open the file
                cmds.file( mmOldAnimFilePath, open = 1)

                # Disable the viewport
                mel.eval("paneLayout -e -manage false $gMainPane")
                cmds.refresh(suspend=True)

                #---------------------------------------------
        
                #   Run the transfer to different rig script - which also exports the animations.
                #Run the anim transfer to rig script
                mmTATDR.main( mmNewRigFilepathAndFilename, mmOldAnimFilePath )

                #---------------------------------------------
        
                #   And ensure that the file is being saved.
                #Save the file
                cmds.file( save = 1, force = 1 )

                mmExportedPathsList.append(item)

        
        #---------------------------------------------
    
        for mmPath in mmExportedPathsList:
            mmExportedPaths = mmExportedPaths + "anim: " + mmPath + "\n"

        #Open the original file
        cmds.file( mmOldRigFilepathAndFilename, open = 1)

        #---------------------------------------------
        
        #display to the user that their export is complete, and what was exported.
        cmds.confirmDialog( title = 'Export Complete', message = 'File(s) Exported:\n' + 
            mmExportedPaths + '\nFilepath exported to:\n' + mmOldRigFilepath + "animations/"
            , button = ['OK'], defaultButton = 'OK' )


    #Re-enable the viewport
    # Translation into python is easy, how to figure out the name of the panelayout is not
    mel.eval("paneLayout -e -manage true $gMainPane")
    cmds.refresh(suspend=False)


def mmFixBrokenViewport(*args):
    
    #Re-enable the viewport
    # Translation into python is easy, how to figure out the name of the panelayout is not
    mel.eval("paneLayout -e -manage true $gMainPane")
    cmds.refresh(suspend=False)