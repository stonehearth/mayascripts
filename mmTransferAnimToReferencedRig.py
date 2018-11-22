"""

Function: mmTransferAnimToReferencedRig
Description: This function will take an animation which has been 'sent to' from 3dsmax to maya and convert it onto a rig of the user's choosing.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.mel as mel
import time

#Local
import mmSelectAnimatingParts as mmSAP
import mmReturnFilepathOrFilename as mmRFOF
import mmScaleDownFrom3DSMax
import mmExportAnimationAsJson as mmEAAJ
import mmConvert3DSMaxRigToMayaRig as mmCM2M

######################################
############# DEFINES ################
######################################


def main( mmRigFilepathAndFilename = None, mmAnimFilePath = None, *args):

    mmPassedRig = False

    if ( mmRigFilepathAndFilename != None and mmAnimFilePath != None ):
        mmPassedRig = True

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
    mmProperBoneName = []
    mmProperBoneList = []
    mmCopyLocList = []
    mmModifiedNames = []

    mmTransferFromMaxBool = True

    mmSearchingSuffix = "_Control"

    mmTempLocSuffix = "_TransferLoc"
    
    #Clear out duplicates & then sort
    #Just converting the list to a "set" and back to a "list" causes all duplicates to be removed.
    mmOriginalBones = list(set(mmOriginalBones))
    mmOriginalBones.sort()

    #First need to ensure the scale of the animation is 1 so transfer works properly

    objectName = 'root'
    if objectName in mmOriginalBones:
        
        #clear selection
        cmds.select (cl = 1)
         
        #select only the root
        cmds.select (objectName)

        #Scale down the selected value
        #This is an assumption - may want to have a check before running this.
        mmScaleDownFrom3DSMax.main(objectName)


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
    

    #---------------------------------------------

    ######################################
    #Think I need to import the new rig now so I can use it for the Transfer_Loc rig creation
    ######################################

    #if the rig is passed in, then don't ask about where to do anything
    if ( mmPassedRig == False ):

        #---------------------------------------------
        
        #Ask the user what Rig should be referenced in and have animation applied to.

        #---------------------------------------------
        
        mmStartingDirectory = "C:/Radiant/stonehearth-assets/assets/models/entities/"
        mmDialogueCaption = "Please select the Rig to Reference in and apply animation to."
        mmRigNamespace = "ReferencedAnimRig_Male"
        
        #Open a dialogue box where user can input information
        mmRigFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 1, fileFilter = 'MA (*.ma)', selectFileFilter = 'MA (*.ma)', dir = mmStartingDirectory )
        #print mmRigFilename    
        
        mmSavedDirectory = mmRFOF.main( mmRigFilename, 0 )
        #print mmSavedDirectory

        mmRigNamespace = mmRFOF.main( mmRigFilename, 1 )
            
        #And then import those animations onto the Referenced Rig
        
        #Need to import Referenced Rig
        #Original Mel:
        #file -r -type "mayaAscii"  -ignoreVersion -gl -mergeNamespacesOnClash false -namespace "ReferencedAnimRig_Male" -options "v=0;" "C:/Radiant/stonehearth-assets/assets/models/entities/humans/male/ReferencedAnimRig_Male.ma";
        cmds.file( mmRigFilename, r = 1, type = "mayaAscii", ignoreVersion = 1, gl = 1, mergeNamespacesOnClash = False, namespace = mmRigNamespace, options = "v=0;" )
    
    #---------------------------------------------
    
    else:
        #use the passed in information

        # mmAnimFilePath
        # mmRigFilepathAndFilename



        #Else: use the passed in information
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
        #?  I dont think this will pick up referenced assets - it isn't searching for names with ":" in front.
        #       Maybe we should be checking for both referenced and not?  or.. not really, non-referenced controls shouldn't happen.
        #       Some confusion here - does this script need to transfer between a 3dsmax anim and the maya rig, or also from two maya rigs?
        #       The difference is whether or not the anim which is being transfered is coming from a referenced rig or not.
        #####################################
        #?  There is another issue where someone (me) screws up and animates on a rig in maya which is not referenced.
        #       Its happened twice so far, I should probably account for it.
        #####################################

        mmNameChecker = objectCounter.split(":")

        if ( len(mmNameChecker) > 1 ):

            #Then this should mean I have a referenced rig which I am pulling from.

            mmProperBoneName = mmNameChecker[1].split("_")

            #mmSearchingSuffix is up above just incase I need to change it at some point (without digging through the code to find this line).
            #Here we are comparing the mmSearchingSuffix with the mmProperBoneName[1] and verifying that we have a control selected.
            mmTempSuffix = mmSearchingSuffix.split("_")[1]

            if ( len(mmProperBoneName) > 1 and mmProperBoneName[1] == mmTempSuffix ):

                #If everything checks out, we save the bone name in a list
                mmProperBoneList.append(mmProperBoneName[0])

                mmTransferFromMaxBool = False

        else:

            #This means I am pulling from either a 3dsmax transfered rig, or a maya rig which is not referenced.
            #?  The later I do not believe we account for,
            #       though it is possible we converted it over at some point and didn't maintain the original purpose :(.

            #Each new bone is given an array to store its name and its parent.
            mmNewBoneStoreArray = []

            #Store the name of the bone into the array, as well as its parent.
            objectCounterNewName = objectCounter + mmTempLocSuffix
            mmNewBoneStoreArray.append(objectCounterNewName)

            objectParent = cmds.listRelatives( objectCounter, p = 1 )

            #Also create the names of the bones which the rig will have.
            mmModifiedName = mmRigNamespace + ":" + objectCounter + mmSearchingSuffix
            mmModifiedNames.append(mmModifiedName)
            # print "mmModifiedNames[mmCounterA]", mmModifiedNames[mmCounterA]
     
            if ( objectParent != None ):
                objectParent[0] += mmTempLocSuffix

                mmNewBoneStoreArray.append(objectParent[0])
                
            else:
                mmNewBoneStoreArray.append(None)

            mmNewRigStoreArray.append(mmNewBoneStoreArray)

            # print "mmNewBoneStoreArray", mmNewBoneStoreArray

            mmCounterA += 1
            mmTransferFromMaxBool = True

    mmRootBone = ""
    mmRootTempLoc = ""

    if (mmTransferFromMaxBool):
        mmCounterB = 0

        for objectCounter in mmOriginalBones:
            #Create a locator and parent it to the correct bone so it mimics the movement of its parent, then transfer that animation over.
            #?This assumes that my rig is clean - but my rigs are NOT clean, I know this.  So instead, I need a way to create these locators,
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


    #Clear out duplicates & Sort
    #Just converting the list to a "set" and back to a "list" causes all duplicates to be removed.
    
    if ( mmTransferFromMaxBool == False ): 
        mmProperBoneList = list(set(mmProperBoneList))
        mmProperBoneList.sort()
    
    if ( mmTransferFromMaxBool == True ):

        mmCopyLocList = list(set(mmCopyLocList))
        mmCopyLocList.sort()
        mmModifiedNames = list(set(mmModifiedNames))
        mmModifiedNames.sort()

    #Think this only applies if its a 3dsmax rig - not sure.
    for rigStoredArray in mmNewRigStoreArray:
    
        if ( rigStoredArray[1] != None ):
            cmds.parent( rigStoredArray[0], rigStoredArray[1])

        if ( rigStoredArray[0] != "root" + mmTempLocSuffix ):
            cmds.select(rigStoredArray[0])
            cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)



    #Next need to move the templocs to where they should be in space
    ####################################
    #I'm sure this is horrible, because they are parented, and now we are not maintaining offset constrainting them : /
    #  Seems to work regardless - I should check.
    ####################################
    #This is actually horrible because this is assuming that mmCopyLocList exists, but if it is not a 3dsmax rig, then it wont.  This script is half unfinished.
    #  Think I started combining this and 'mmTransferAnimToDifferentRig'
    ####################################

    #FIRST: the root must line up


    mmCounterC = 0
    while mmCounterC < len(mmOriginalBones):
        
        #Padding it wont help : (
        #mmLocPad = mmOF.mmGroupInPlace( mmCopyLocList[mmCounterC] )

        print "mmOriginalBones[mmCounterC]", mmOriginalBones[mmCounterC]
        print "mmCopyLocList[mmCounterC]", mmCopyLocList[mmCounterC]

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

    if ( mmPassedRig == False ):

        #---------------------------------------------
        
        #Ask the user what location the ATOM Animation should be saved to.
        
        #---------------------------------------------
        
        #Export animations as ATOM animations to a file location which the user specifies
        #mmExportImportFilename = "C:/Users/mmalley/Documents/Work/AnimationExports/idle_breathe/idle_breathe.atom"
        
        #####################
        #Change this starting directory to be more generic once set up - probably in the Radiant folder
        #####################

        mmStartingDirectory = "C:/Users/mmalley/Documents/Work/AnimationExports"
        mmDialogueCaption = "Please select a name and location for ATOM Animations."
        mmfileFilterName = 'ATOM'
        mmfileFilterType = '.atom'
        
        #Open a dialogue box where user can input information
        mmFullDirectoryPathFiletype = cmds.fileDialog2( cap = mmDialogueCaption, fm = 0, fileFilter = mmfileFilterName + ' (*' + mmfileFilterType + ')', selectFileFilter = mmfileFilterName + ' (*' + mmfileFilterType + ')', dir = mmStartingDirectory)
        #print mmExportImportFilenameAndPath
        
        mmExportImportFilename = mmRFOF.main( mmFullDirectoryPathFiletype , 1 )
        
        
        #print mmFullDirectoryPathFiletype
        
        #Export animation to specified file.
        mmMelExportAtomLine = 'doExportAtom(1,{ "' + mmFullDirectoryPathFiletype[0] + '" });'
        #print mmMelExportAtomLine
        mel.eval(mmMelExportAtomLine)
        
        mel.eval('fileCmdCallback;')

    else:


        mmExportImportFilename = mmRFOF.main( mmAnimFilePath, 1 )
        
        mmFullDirectoryPathFiletype = mmSavedDirectory + mmExportImportFilename + ".atom"

        #Export animation to specified file.
        mmMelExportAtomLine = 'doExportAtom(1,{ "' + mmSavedDirectory + mmExportImportFilename + '" });'
        #print mmMelExportAtomLine
        mel.eval(mmMelExportAtomLine)
        
        mel.eval('fileCmdCallback;')



    #print "mmOriginalBones", mmOriginalBones
    #print "mmProperBoneList", mmProperBoneList

    #Next we need to copy the animations from the original Rig onto the new Replacement Rig
    '''   
    #Don't want to create a template here, just want to use the existing one from the Rig export
    #**Are templates even needed?  Why not just overload onto 'trash' every time?
    #Python version of Atom Template Creator - saves it as the file name specified
    #mel.eval('atomTemplateCallback  OptionBoxWindow|formLayout242|tabLayout37|formLayout244|tabLayout38|columnLayout172 1; hideOptionBox;')
    
    #Ask the user what location the Character Template should be saved to.
    mmStartingDirectory = "C:/Users/mmalley/Documents/Work/CharacterTemplates"
    mmDialogueCaption = "Please select a name and location for the Character Template."
    mmATOMOriginalName = "HumanMaleOriginal"
    
    #Open a dialogue box where user can input information
    mmTemplateFilename = cmds.fileDialog2( cap = mmDialogueCaption, fm = 0, fileFilter = 'Template (*.template)', selectFileFilter = 'template (*.template)', dir = mmStartingDirectory)
    print "mmTemplateFilename[0]", mmTemplateFilename[0]
    
    mmATOMOriginalName = mmRFOF.main( mmTemplateFilename , 1 )
    print "mmATOMOriginalName", mmATOMOriginalName
    
    #Old, Doesn't work: cmds.containerTemplate( mmATOMOriginalName, force = 1, edit = 1, layoutMode = 1, addView = 0, fromSelection = 1, useHierarchy = 1, allKeyable = 1, save = 1, fileName = mmTemplateFilename[0] )
    if (mmTemplateFilename[0]):
        #cmds.containerTemplate( "HumanMaleOriginal", force = 1, edit = 1, layoutMode = 1, addView = 0, fromSelection = 1, useHierarchy = 1, allKeyable = 1, save = 1, fileName = mmTemplateFilename[0] )
        cmds.containerTemplate( mmATOMOriginalName, force = 1, fromSelection = 1, useHierarchy = 1, allKeyable = 1 )
        cmds.containerTemplate( mmATOMOriginalName, save = 1, fileName = mmTemplateFilename[0] )
        cmds.containerTemplate( mmATOMOriginalName, force = 1, edit = 1, layoutMode = 1, addView = 0, fromSelection = 1, useHierarchy = 1, allKeyable = 1 )
        cmds.containerTemplate( mmATOMOriginalName, save = 1, fileName = mmTemplateFilename[0] )
    '''
    
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
    # print "mmSelectedNames - right before import: ", mmSelectedNames
    
    
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
    #Copying from 'mmTransferAnimToDifferentRig'
    #Re-select the desired components

    # print "mmFullDirectoryPathFiletype", mmFullDirectoryPathFiletype

    #Should this be mmFullDirectoryPathFiletype[0]? - NOPE!?!?!!  I dont know, it works now.
    mmImportAnimFilePath = mmFullDirectoryPathFiletype

    mmCompiledOptionsForImportAnimations = ";;targetTime=3;option=insert;match=string;;selected=selectedOnly;search=" + mmSearchName + ";replace=" + mmReplaceName + ";prefix=" + mmATOMImportPrefix + ";suffix=" + mmATOMImportSuffix + ";mapFile=C:/Users/mmalley/Documents/maya/projects/default/data/;"


    #Importing animations onto new Rig
    cmds.file( mmImportAnimFilePath, i = 1, type = "atomImport", ra = 1, namespace = "run", options = mmCompiledOptionsForImportAnimations )
    

    # Works, but I don't want to waste 5 seconds every time - and maybe I'll need to wait 10 seconds for some.. who knows?
    #time.sleep( 5 )


    #input("Press Enter to continue...")
    #os.system("pause") #doesn't work because maya waits til the end of the function to call this import

    cmds.viewFit( all = True )
    
    #Can't do this, it creates an infinite loop.
    # while bob == bob:
    # cmds.pause( sec = 0.1 )
    
    
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
    
    #Don't want to save out the file right now
    #Need to save out the file as .MA
    #Just place it in the "Animations" folder under where the rig was saved out.
    mmNewAnimFilenameAndFilepath = mmSavedDirectory + "animations/" + mmExportImportFilename + ".ma"
    
    cmds.file( rename = mmNewAnimFilenameAndFilepath )
    
    cmds.file( force = 1, save = 1, type = 'mayaAscii' )

    
    #---------------------------------------------
    
    #Export an animation as well
    mmEAAJ.main(True)
    
#---------------------------------------------
#Need a function for returning the filepath or filename of an asset?
