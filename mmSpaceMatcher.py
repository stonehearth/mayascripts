"""

Function: mmSpaceMatcher
Description: This function will take the selected objects, store their world location/translation/scale,
then allow you to change frames or space switch and paste the old values onto the objects.
Note! - Be sure to select in the order of heirarchy.  i.e. If attempting to copy/paste the arm - start by selecting the shoulder, then arm, then wrist, etc.
If you don't, then each time parent object is set in place after its children, the children will be moved to a new location.


"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

#Local


######################################
############# GLOBALS ################
######################################

mmSavedTrans = []
mmSavedRot = []
mmSavedScale = []

######################################
############# DEFINES ################
######################################

'''
This is the WIP function where I was figuring stuff out.  Will probably come back to it later for a 'true' space matcher with UI and what not.
'''
def main(*args):
    #Space Matching
    #Take selected object
    mmSelected = cmds.ls(sl = 1)[0]

    #create loc
    mmTempLoc = cmds.spaceLocator()[0]

    #snap to object
    mmTempParentConstraint = cmds.parentConstraint( mmSelected, mmTempLoc, mo = 0 )

    #Delete parentConstraint
    cmds.delete(mmTempParentConstraint)

    #get trans from loc
    mmBaseRootWorldPos = cmds.getAttr (mmTempLoc + ".worldPosition")[0]

    #SpaceSwitch
    cmds.setAttr("head_Control.head_Control", 0)
    cmds.setAttr("head_Control.root_loc", 10)

    #parentConstrain the opposite way
    mmTempParentConstraint = cmds.parentConstraint( mmTempLoc, mmSelected, mo = 0 )

    #Delete parentConstraint
    cmds.delete(mmTempParentConstraint)
    #delete loc
    cmds.delete(mmTempLoc)

    #reselect original object
    cmds.select(mmSelected)


'''
Copy function should store information and be able to paste it later at any time (unless you shut down maya)
'''
def mmCopySpace(*args):

    #Grab Global Group Variables
    global mmSavedTrans
    global mmSavedRot
    global mmSavedScale


    #Space Matching
    #Take selected object
    mmSelected = cmds.ls(sl = 1)

    mmCounter = 0

    for mmEachSelected in mmSelected:
        #create loc
        mmTempLoc = cmds.spaceLocator()[0]

        #snap to object
        mmTempParentConstraint = cmds.parentConstraint( mmEachSelected, mmTempLoc, mo = 0 )

        #Delete parentConstraint
        cmds.delete(mmTempParentConstraint)

        bob = 0

        mmSavedTrans.append(bob)
        mmSavedRot.append(bob)
        mmSavedScale.append(bob)

        #get trans from loc
        mmSavedTrans[mmCounter] = cmds.getAttr ( mmTempLoc + ".worldPosition" )[0]
        # print "mmSavedTrans", mmSavedTrans

        #get rot from loc
        mmSavedRot[mmCounter] = cmds.xform ( mmTempLoc, q = 1, rotation = 1 )
        # print "mmSavedRot", mmSavedRot

        #get scale from loc
        mmSavedScale[mmCounter] = cmds.xform ( mmTempLoc, q = 1, scale = 1, r = 1)
        # print "mmSavedScale", mmSavedScale

        #delete loc
        cmds.delete(mmTempLoc)

        mmCounter += 1

    cmds.select(cl = 1)

    #reselect original objects in order
    for mmEachSelected in mmSelected:
        cmds.select( mmEachSelected, add = 1 )


'''
Copy function should store information and be able to paste it later at any time (unless you shut down maya)
'''
def mmPasteSpace(*args):

    #Grab Global Group Variables
    global mmSavedTrans
    global mmSavedRot
    global mmSavedScale

    # print "mmSavedTrans", mmSavedTrans
    # print "mmSavedRot", mmSavedRot
    # print "mmSavedScale", mmSavedScale

    #Space Matching
    #Take selected object
    mmSelected = cmds.ls(sl = 1)

    mmCounter = 0

    for mmEachSelected in mmSelected:
        #create loc
        mmTempLoc = cmds.spaceLocator()[0]

        #move to location which was saved before
        cmds.move( mmSavedTrans[mmCounter][0], mmSavedTrans[mmCounter][1], mmSavedTrans[mmCounter][2] )
        cmds.rotate( mmSavedRot[mmCounter][0], mmSavedRot[mmCounter][1], mmSavedRot[mmCounter][2])
        cmds.scale( mmSavedScale[mmCounter][0], mmSavedScale[mmCounter][1], mmSavedScale[mmCounter][2])

        #parentConstrain the opposite way
        mmTempParentConstraint = cmds.parentConstraint( mmTempLoc, mmEachSelected, mo = 0 )
        
        #Key the thing in place (because it very likely already has a key on it, and this is an animation tool)
        cmds.setKeyframe(mmEachSelected)

        #THEN delete the constraint
        #Delete parentConstraint
        cmds.delete(mmTempParentConstraint)

        #delete loc
        cmds.delete(mmTempLoc)

        mmCounter += 1

    cmds.select(cl = 1)

    #reselect original objects in order
    for mmEachSelected in mmSelected:
        cmds.select( mmEachSelected, add = 1 )
