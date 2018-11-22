"""

Function: mmValueSwapper
Description: This function will take two selected objects, and then copy/paste the selected values between them.


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

######################################
############# DEFINES ################
######################################

def main(*args):
    print "Non-Functional"


def mmSwapTransX(*args):

    mmListToWorkWith = [1,0,0,
                        0,0,0,
                        0,0,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapTransY(*args):

    mmListToWorkWith = [0,1,0,
                        0,0,0,
                        0,0,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapTransZ(*args):

    mmListToWorkWith = [0,0,1,
                        0,0,0,
                        0,0,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapRotX(*args):

    mmListToWorkWith = [0,0,0,
                        1,0,0,
                        0,0,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapRotY(*args):

    mmListToWorkWith = [0,0,0,
                        0,1,0,
                        0,0,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapRotZ(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,1,
                        0,0,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapScaleX(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,0,
                        1,0,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapScaleY(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,0,
                        0,1,0]

    mmSwapWorker(mmListToWorkWith)


def mmSwapScaleZ(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,0,
                        0,0,1]

    mmSwapWorker(mmListToWorkWith)



def mmSwapWorker( mmListToWorkWith ):

    mmSelectedItems = cmds.ls(sl = 1)

    if ( len(mmSelectedItems) != 2 ):
        print "Two items must be selected."
        return

    mmSavedTrans = ["",""]
    mmSavedRot = ["",""]
    mmSavedScale = ["",""]

    mmCounter = 0

    for mmItem in mmSelectedItems:
        #create loc
        mmTempLoc = cmds.spaceLocator()[0]

        #snap to object
        mmTempParentConstraint = cmds.parentConstraint( mmItem, mmTempLoc, mo = 0 )

        #Delete parentConstraint
        cmds.delete(mmTempParentConstraint)


        #get trans from loc
        mmSavedTrans[mmCounter] = cmds.getAttr ( mmTempLoc + ".worldPosition" )[0]

        #get rot from loc
        mmSavedRot[mmCounter] = cmds.xform ( mmTempLoc, q = 1, rotation = 1 )

        #get scale from loc
        mmSavedScale[mmCounter] = cmds.xform ( mmTempLoc, q = 1, scale = 1, r = 1)

        #delete loc
        cmds.delete(mmTempLoc)

        mmCounter += 1

    mmCounter = 0

    for mmItem in mmSelectedItems:

        XTransValue = mmSavedTrans[mmCounter][0]
        YTransValue = mmSavedTrans[mmCounter][1]
        ZTransValue = mmSavedTrans[mmCounter][2]
        
        XRotValue = mmSavedRot[mmCounter][0]
        YRotValue = mmSavedRot[mmCounter][1]
        ZRotValue = mmSavedRot[mmCounter][2]
        
        XScaleValue = mmSavedScale[mmCounter][0]
        YScaleValue = mmSavedScale[mmCounter][1]
        ZScaleValue = mmSavedScale[mmCounter][2]

        #create new locs
        mmTempLoc = cmds.spaceLocator()[0]

        #move to location which was saved
        if (mmCounter == 0):
            if (mmListToWorkWith[0] == True):
                XTransValue = mmSavedTrans[1][0]
            if (mmListToWorkWith[1] == True):
                YTransValue = mmSavedTrans[1][1]
            if (mmListToWorkWith[2] == True):
                ZTransValue = mmSavedTrans[1][2]
                
            if (mmListToWorkWith[3] == True):
                XRotValue = mmSavedRot[1][0]
            if (mmListToWorkWith[4] == True):
                YRotValue = mmSavedRot[1][1]
            if (mmListToWorkWith[5] == True):
                ZRotValue = mmSavedRot[1][2]
                
            if (mmListToWorkWith[6] == True):
                XScaleValue = mmSavedScale[1][0]
            if (mmListToWorkWith[7] == True):
                YScaleValue = mmSavedScale[1][1]
            if (mmListToWorkWith[8] == True):
                ZScaleValue = mmSavedScale[1][2]
                
        else:
            if (mmListToWorkWith[0] == True):
                XTransValue = mmSavedTrans[0][0]
            if (mmListToWorkWith[1] == True):
                YTransValue = mmSavedTrans[0][1]
            if (mmListToWorkWith[2] == True):
                ZTransValue = mmSavedTrans[0][2]
                
            if (mmListToWorkWith[3] == True):
                XRotValue = mmSavedRot[0][0]
            if (mmListToWorkWith[4] == True):
                YRotValue = mmSavedRot[0][1]
            if (mmListToWorkWith[5] == True):
                ZRotValue = mmSavedRot[0][2]
                
            if (mmListToWorkWith[6] == True):
                XScaleValue = mmSavedScale[0][0]
            if (mmListToWorkWith[7] == True):
                YScaleValue = mmSavedScale[0][1]
            if (mmListToWorkWith[8] == True):
                ZScaleValue = mmSavedScale[0][2]


        cmds.move( XTransValue, YTransValue, ZTransValue )
        cmds.rotate( XRotValue, YRotValue, ZRotValue )
        cmds.scale( XScaleValue, YScaleValue, ZScaleValue )

        #parentConstrain the opposite way
        mmTempParentConstraint = cmds.parentConstraint( mmTempLoc, mmItem, mo = 0 )
        
        #Key the thing in place (because it very likely already has a key on it, and this is an animation tool)
        cmds.setKeyframe(mmItem)

        #THEN delete the constraint and loc
        #Delete parentConstraint
        cmds.delete(mmTempParentConstraint)

        #delete loc
        cmds.delete(mmTempLoc)

        mmCounter += 1

    #Clear selection
    cmds.select(cl = 1)

    #re-select previous selection
    for mmItem in mmSelectedItems:
        cmds.select(mmItem, add = 1)


'''
Negative Functions
'''

def mmNegativeTransX(*args):

    mmListToWorkWith = [1,0,0,
                        0,0,0,
                        0,0,0]

    mmNegativeWorker(mmListToWorkWith)


def mmNegativeTransY(*args):

    mmListToWorkWith = [0,1,0,
                        0,0,0,
                        0,0,0]

    mmNegativeWorker(mmListToWorkWith)
        

def mmNegativeTransZ(*args):

    mmListToWorkWith = [0,0,1,
                        0,0,0,
                        0,0,0]

    mmNegativeWorker(mmListToWorkWith)

        
def mmNegativeRotX(*args):

    mmListToWorkWith = [0,0,0,
                        1,0,0,
                        0,0,0]

    mmNegativeWorker(mmListToWorkWith)
    
        
def mmNegativeRotY(*args):

    mmListToWorkWith = [0,0,0,
                        0,1,0,
                        0,0,0]

    mmNegativeWorker(mmListToWorkWith)
    
        
def mmNegativeRotZ(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,1,
                        0,0,0]

    mmNegativeWorker(mmListToWorkWith)
    
        
def mmNegativeScaleX(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,0,
                        1,0,0]

    mmNegativeWorker(mmListToWorkWith)
    
        
def mmNegativeScaleY(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,0,
                        0,1,0]

    mmNegativeWorker(mmListToWorkWith)
    
        
def mmNegativeScaleZ(*args):

    mmListToWorkWith = [0,0,0,
                        0,0,0,
                        0,0,1]

    mmNegativeWorker(mmListToWorkWith)
    

def mmNegativeWorker( mmListToWorkWith ):

    mmSelectedItems = cmds.ls(sl = 1)

    mmCounter = 0

    for mmItem in mmSelectedItems:
        #create loc
        mmTempLoc = cmds.spaceLocator()[0]

        #snap to object
        mmTempParentConstraint = cmds.parentConstraint( mmItem, mmTempLoc, mo = 0 )

        #Delete parentConstraint
        cmds.delete(mmTempParentConstraint)


        #get trans from loc
        mmSavedTrans = cmds.getAttr ( mmTempLoc + ".worldPosition" )[0]

        #get rot from loc
        mmSavedRot = cmds.xform ( mmTempLoc, q = 1, rotation = 1 )

        #get scale from loc
        mmSavedScale = cmds.xform ( mmTempLoc, q = 1, scale = 1, r = 1)

        #delete loc
        cmds.delete(mmTempLoc)



        XTransValue = mmSavedTrans[0]
        YTransValue = mmSavedTrans[1]
        ZTransValue = mmSavedTrans[2]
        
        XRotValue = mmSavedRot[0]
        YRotValue = mmSavedRot[1]
        ZRotValue = mmSavedRot[2]
        
        XScaleValue = mmSavedScale[0]
        YScaleValue = mmSavedScale[1]
        ZScaleValue = mmSavedScale[2]

        #create new locs
        mmTempLoc = cmds.spaceLocator()[0]

        #move to location which was saved
        if (mmListToWorkWith[0] == True):
            XTransValue = mmSavedTrans[0]*-1
        if (mmListToWorkWith[1] == True):
            YTransValue = mmSavedTrans[1]*-1
        if (mmListToWorkWith[2] == True):
            ZTransValue = mmSavedTrans[2]*-1
            
        if (mmListToWorkWith[3] == True):
            XRotValue = mmSavedRot[0]*-1
        if (mmListToWorkWith[4] == True):
            YRotValue = mmSavedRot[1]*-1
        if (mmListToWorkWith[5] == True):
            ZRotValue = mmSavedRot[2]*-1
            
        if (mmListToWorkWith[6] == True):
            XScaleValue = mmSavedScale[0]*-1
        if (mmListToWorkWith[7] == True):
            YScaleValue = mmSavedScale[1]*-1
        if (mmListToWorkWith[8] == True):
            ZScaleValue = mmSavedScale[2]*-1
                

        print "XTransValue", XTransValue

        cmds.move( XTransValue, YTransValue, ZTransValue )
        cmds.rotate( XRotValue, YRotValue, ZRotValue )
        cmds.scale( XScaleValue, YScaleValue, ZScaleValue )

        #parentConstrain the opposite way
        mmTempParentConstraint = cmds.parentConstraint( mmTempLoc, mmItem, mo = 0 )
        
        #Key the thing in place (because it very likely already has a key on it, and this is an animation tool)
        cmds.setKeyframe(mmItem)

        #THEN delete the constraint and loc
        #Delete parentConstraint
        cmds.delete(mmTempParentConstraint)

        #delete loc
        cmds.delete(mmTempLoc)

        mmCounter += 1

    #Clear selection
    cmds.select(cl = 1)

    #re-select previous selection
    for mmItem in mmSelectedItems:
        cmds.select(mmItem, add = 1)

