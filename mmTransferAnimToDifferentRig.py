"""

Function: mmTransferAnimToDifferentRig
Description: This function will transfer animations from one referenced rig to another similar referenced rig (i.e. Human Male to Female).
    RIGS MUST BE REFERENCED.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.mel as mel
import os

#Local
import mmSelectAnimatingParts as mmSAP
import mmReturnFilepathOrFilename as mmRFOF
import mmExportAnimationAsJson as mmEAAJ
import mmConvert3DSMaxRigToMayaRig as mmCM2M

######################################
############# DEFINES ################
######################################



def main( mmRigFilepathAndFilename = None, mmOldAnimFilePath = None, *args):

    ############
    #There is a huge problem here - if the export window has its properties changed outside this script, this script doesn't reset those changes.
    #   This causes the script to fail.  To fix, you need to go into the Atom Export window in Maya, and reset the tool so it exports animations based on the timeline.
    ############

    #Verify if a rig was passed in
    mmPassedRig = False

    if ( mmRigFilepathAndFilename != None and mmOldAnimFilePath != None ):
        mmPassedRig = True

    # print ""
    # print "Start of mmTATDR"

    # print "mmRigFilepathAndFilename", mmRigFilepathAndFilename
    # print "type( mmRigFilepathAndFilename )", type( mmRigFilepathAndFilename )

    # print "mmOldAnimFilePath", mmOldAnimFilePath
    # print "type( mmOldAnimFilePath )", type( mmOldAnimFilePath )
    # print ""

    #---------------------------------------------
    
    mmCM2M.mmFixUI()

    #Cycle the Atom Export window just to make sure it is alive and working
    mel.eval( "ExportAnimOptions;" )
    mel.eval( "performExportAnim 1;" )
    mel.eval( "hideOptionBox;" )

    #Select everything we want to have selected
    selectionList = []
    selectionList = mmSAP.main(["mesh", "nurbsCurve"])
    
    #Copy selectionList just in case
    originalSelectionList = list(selectionList)

    #---------------------------------------------
    
    #Next we need to copy the animations from the original Rig onto the new Replacement Rig
    
    #---------------------------------------------
    
    #Don't want to create a template here, just want to use the existing one from the Rig export
    #     A template must exist already for this rig to be used in our game.
    #     (it is part of rig creation)

    #---------------------------------------------
    
    #if the rig is not passed in, then ask where to do the work.
    if ( mmPassedRig == False ):

        #---------------------------------------------
        
        #Don't need to ask the user what the name should be - we have the name because we can grab it from the file we are on.
        mmATOMFilepathAndFilename = cmds.file(q = 1, loc = 1)

        #Grab just the file name
        mmExportImportFilename = mmRFOF.main( mmATOMFilepathAndFilename , 1 )

        #---------------------------------------------

        #Need info for grabbing a rig
        #Ask the user what Rig should be referenced in and have animation applied to.
        mmStartingDirectory = "C:/Radiant/stonehearth-assets/assets/models"
        mmDialogueCaption = "Please select the Rig to Reference in and apply animation to."
        mmRigNamespace = "ReferencedAnimRig_Male"
        
        #Open a dialogue box where user can input information
        mmRigFilepathAndFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 1, fileFilter = 'MA (*.ma)', selectFileFilter = 'MA (*.ma)', dir = mmStartingDirectory )
        #print "mmRigFilename "
        #print mmRigFilename
        
        mmSavedDirectory = mmRFOF.main( mmRigFilepathAndFilename, 0 )
     
        mmSavedFilename = mmRFOF.main( mmRigFilepathAndFilename, 1 )

        #---------------------------------------------

        #Create a filepath for the atom export
        mmATOMFilepathAndFilename = mmSavedDirectory


    else:
        #if the rig is passed in, then don't ask about where to do anything.

        #create names to use later
        mmOldAnimSavedDirectory = mmRFOF.main( mmOldAnimFilePath, 0 )
     
        mmOldAnimSavedFilename = mmRFOF.main( mmOldAnimFilePath, 1 )

        
        #create names to use later
        mmNewRigSavedDirectory = mmRFOF.main( mmRigFilepathAndFilename, 0 )
     
        mmNewRigSavedFilename = mmRFOF.main( mmRigFilepathAndFilename, 1 )


        # #Else: use the passed in information
        # mmSavedDirectory = mmRFOF.main( mmRigFilepathAndFilename, 0 )
        
        # mmRigNamespace = mmRFOF.main( mmRigFilepathAndFilename, 1 )

        mmExportImportFilename = mmOldAnimSavedFilename

        #Tailor make a filepath and name to export an animation
        mmATOMFilepathAndFilename = mmNewRigSavedDirectory
        # print "mmNewRigSavedDirectory", mmNewRigSavedDirectory
        # print "type( mmNewRigSavedDirectory )", type( mmNewRigSavedDirectory )

        #---------------------------------------------

        #Need info for grabbing a rig
        mmSavedDirectory = mmNewRigSavedDirectory
     
        mmSavedFilename = mmNewRigSavedFilename

    #---------------------------------------------
    
    #Either way, ensure there is an "atom_exports" folder, and composite a proper filepath & name for the atom export
    mmNameChecker = True

    for item in os.listdir( mmATOMFilepathAndFilename ):
        if ( item == "atom_exports" ):
            mmNameChecker == False
    
    if ( mmNameChecker ):
        cmds.sysFile( mmSavedDirectory + "atom_exports/", makeDir=True )

    mmATOMFilepathAndFilename = mmATOMFilepathAndFilename + "atom_exports/" + mmExportImportFilename + ".atom"

    #---------------------------------------------
    
    #Export animation to specified file.
    mmMelExportAtomLine = 'doExportAtom(1,{ "' + mmATOMFilepathAndFilename + '" });'

    mel.eval(mmMelExportAtomLine)
    
    #Removing this line, as it was messing everything up in the other anim.
    #mel.eval('fileCmdCallback;')

    #---------------------------------------------
    
    #Next import the new Referenced Rig

    cmds.file( mmRigFilepathAndFilename, r = 1, type = "mayaAscii", ignoreVersion = 1, gl = 1, mergeNamespacesOnClash = False, namespace = mmSavedFilename, options = "v=0;" )
    
    #---------------------------------------------

    #Then remove the old referenced rig

    #Grab the first thing we selected before and grab its reference name.
    #We can assume this will always work because all files MUST be referenced in our game
    #     (from this point onward)
    mmPrefixRemoved = originalSelectionList[0].split(':')[0]

    #Create name of referenced node
    mmReferencedNode = mmPrefixRemoved + 'RN'

    #Remove the referenced file
    cmds.file( referenceNode = mmReferencedNode, removeReference = 1 )

    #The scene should now be empty.

    #---------------------------------------------

    #Check if a folder called "animations" exists for the future folder structure
    mmNewRigAnimFolderCheck = cmds.file( mmSavedDirectory + "animations/", q = 1, ex = 1 )
    # print "mmNewRigAnimFolderCheck", mmNewRigAnimFolderCheck

    #If there isn't an animations folder for the new rig, need to make one
    if ( mmNewRigAnimFolderCheck == False ):

        cmds.sysFile( mmNewRigSavedDirectory + "animations/", makeDir=True )

    #---------------------------------------------

    #Need to modify the original slection list so that it looks like what I am looking for
    #Not sure if this step is needed, I think I actually need to get the ATOM importer
    #     to do this for me. - Nah, its ok that i do it here.
    
    #create empty list
    mmModifiedSelectionList = []

    # print "originalSelectionList", originalSelectionList


    for mmOldName in originalSelectionList:

        # print "mmOldName", mmOldName

        #Split out the old namespace and attach the new one
        mmStoredBoneName = mmOldName.split( ':' )[1]

        #Add new namespace to the front
        mmNewBoneName = mmSavedFilename + ':' + mmStoredBoneName

        if cmds.objExists ( mmNewBoneName ):
            mmModifiedSelectionList.append( mmNewBoneName )

            cmds.select( mmNewBoneName, add = 1 )


    #Copy the list just in case
    mmOriginalBones = list(mmModifiedSelectionList)

    #---------------------------------------------

    #---------------------------------------------

    #Cycle the import window to make sure it is capable of running stuff.
    mel.eval("ImportAnimOptions;")
    mel.eval("performImportAnim 1;")

    mmSearchName = mmPrefixRemoved
    mmReplaceName = mmSavedFilename
    mmImportAnimFilePath = [mmATOMFilepathAndFilename]
    mmNameSpace = mmExportImportFilename

    # print "mmSearchName", mmSearchName
    # print "mmReplaceName", mmReplaceName
    # print "mmImportAnimFilePath", mmImportAnimFilePath
    # print "mmNameSpace", mmNameSpace

    mmCompiledOptionsForImportAnimations = ";;targetTime=3;option=insert;match=string;;selected=selectedOnly;search=" + mmSearchName + ";replace=" + mmReplaceName + ";prefix=;suffix=;mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;"

    #Importing animations onto new Rig
    cmds.file( mmImportAnimFilePath, i = 1, type = "atomImport", ra = True, namespace = mmNameSpace, options = mmCompiledOptionsForImportAnimations )

    #print "File Command: " + mmImportAnimFilePath + ", i = 1, type = 'atomImport', ra = True, namespace = " + mmNameSpace + ", options = " + mmCompiledOptionsForImportAnimations
    
    #mel.eval("fileCmdCallback;") # Removing this because it caused problems in other areas.
    #---------------------------------------------
    
    #Need to save out the file as .MA
    #Just place it in the "Animations" folder under where the rig was saved out.
    mmNewAnimFilenameAndFilepath = mmSavedDirectory + "animations/" + mmExportImportFilename + ".ma"
    
    cmds.file( rename = mmNewAnimFilenameAndFilepath )
    
    cmds.file( force = 1, save = 1, type = 'mayaAscii' )

    #---------------------------------------------
    if ( mmPassedRig == False ):

        #Export an animation as well
        mmEAAJ.main()

    else:

        #Export an animation as well
        mmEAAJ.main(False)

    