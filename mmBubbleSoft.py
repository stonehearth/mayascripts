"""

Function: mmBubbleSoft
Description: This function will take a mesh, create a lattice around it, and apply opporators which poof out the shape like a bubble.

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
    mmSelectedInScene = cmds.ls(sl = 1)

    mmOverallBoundingBoxList = cmds.exactWorldBoundingBox( )
    print "mmOverallBoundingBoxList", mmOverallBoundingBoxList

    mmOverallXMin = mmOverallBoundingBoxList[0]
    mmOverallYMin = mmOverallBoundingBoxList[1]
    mmOverallZMin = mmOverallBoundingBoxList[2]
    mmOverallXMax = mmOverallBoundingBoxList[3]
    mmOverallYMax = mmOverallBoundingBoxList[4]
    mmOverallZMax = mmOverallBoundingBoxList[5]

    #Find size user wants
    #Find total size
    mmOverallXTotal = abs(mmOverallXMax - mmOverallXMin)
    mmOverallYTotal = abs(mmOverallYMax - mmOverallYMin)
    mmOverallZTotal = abs(mmOverallZMax - mmOverallZMin)
    '''
    print "mmBoundingBoxList[5]", mmBoundingBoxList[5]
    print "mmOverallZMax", mmOverallZMax
    print "mmOverallZMin", mmOverallZMin
    print "mmOverallZTotal", mmOverallZTotal
    '''

    #Find halfway point (i.e. center of object)
    mmOverallXMidPoint = mmOverallXMax - mmOverallXTotal/2
    mmOverallYMidPoint = mmOverallYMax - mmOverallYTotal/2
    mmOverallZMidPoint = mmOverallZMax - mmOverallZTotal/2
    '''
    print "mmOverallZMidPoint", mmOverallZMidPoint
    '''

    for mmItem in mmSelectedInScene:
        
        cmds.select(mmItem, r = 1)
        
        mmScaleGrowValueOverall = 0.01
        mmScaleRateOfShrink = 1.05 #Must be higher than 1
        mmCheckerValue = 5
        mmLatticeSize = 10
        
        mmNewLattice = cmds.lattice(  divisions = (mmLatticeSize, mmLatticeSize, mmLatticeSize), objectCentered = True, ldv = ( 2, 2, 2) )

        mmLatticeMax = mmLatticeSize

        mmLatticeHigh = mmLatticeMax-1
        mmLatticeLow = 0

        
        
        mmBoundingBoxList = cmds.exactWorldBoundingBox( )
        #print "mmBoundingBoxList", mmBoundingBoxList

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
        
        #print "mmNewLattice[1]", mmNewLattice[1]

        #mmPivot = [ mmXMidPoint, mmYMidPoint, mmZMidPoint ]
        mmCheckFunction = mmOverallZMidPoint - mmZMidPoint
        #print "mmCheckFunction", mmCheckFunction
        #print "mmOverallZMidPoint", mmOverallZMidPoint
        #print "mmZMidPoint", mmZMidPoint
        

        #Modify the pivot point based on various information
        mmXFinalValue = mmXMidPoint
        mmYFinalValue = mmYMidPoint
        mmZFinalValue = mmZMidPoint

        #if the bounding box Ymin of the current selection equates to the bounding box Ymin of the all selections
        if ( mmYMin == mmOverallYMin ):
            
            mmYFinalValue = mmYMin
        
        #if the mmCheckFunction is greater than the mmCheckerValue, than move the pivot to the mmZMax
        if ( mmCheckFunction > mmCheckerValue ):
            
            mmZFinalValue = mmZMax
            
        #if the mmCheckFunction is less than the mmCheckerValue, than move the pivot to the mmZMin
        elif ( mmCheckFunction < mmCheckerValue  ):

            mmZFinalValue = mmZMin
            



        #Setting final values
        mmPivot = [ mmXFinalValue, mmYFinalValue, mmZFinalValue ]        
        
        mmListX = [1]
        mmListY = [0]
        mmListZ = [0]
        
        #print mmListX
        
        #Pass 1 - in X
        mmScaleGrowValue = mmScaleGrowValueOverall
        mmLatticeLow = mmLatticeMax/2-1
        mmLatticeHigh = mmLatticeMax/2
        
        mmScaleGrowValue = mmScaleGrowValueOverall
        
        while ( mmLatticeLow != 0 ):
            #cmds.select( mmNewLattice[1] + ".pt" + str(mmListX) + str(mmListY) + str(mmListZ), r = 1 )
            #print mmNewLattice[1] + ".pt[" + str(mmLatticeLow) +" : " + str(mmLatticeHigh) + "][0:" + str(mmLatticeMax) + "][0:" + str(mmLatticeMax) + "]"
            
            cmds.select( mmNewLattice[1] + ".pt[" + str(mmLatticeLow) +" : " + str(mmLatticeHigh) + "][0:" + str(mmLatticeMax) + "][0:" + str(mmLatticeMax) + "]", r = 1 )
            
            cmds.scale( 1, 1 + mmScaleGrowValue, 1 + mmScaleGrowValue, pivot = mmPivot )
            mmScaleGrowValue = mmScaleGrowValue*mmScaleRateOfShrink
            mmLatticeHigh += 1
            mmLatticeLow -= 1


        #Pass 2new - in Y
        
        #Reset Values        
        mmScaleGrowValue = mmScaleGrowValueOverall
        mmLatticeLow = mmLatticeMax/2-1
        mmLatticeHigh = mmLatticeMax/2
        
        while ( mmLatticeLow != 0 ):
            #cmds.select( mmNewLattice[1] + ".pt" + str(mmListX) + str(mmListY) + str(mmListZ), r = 1 )
            
            cmds.select( mmNewLattice[1] + ".pt[0:" + str(mmLatticeMax) + "][" + str(mmLatticeLow) +" : " + str(mmLatticeHigh) + "][0:" + str(mmLatticeMax) + "]", r = 1 )
            
            cmds.scale( 1 + mmScaleGrowValue, 1, 1+ mmScaleGrowValue, pivot = mmPivot )
            mmScaleGrowValue = mmScaleGrowValue*mmScaleRateOfShrink
            mmLatticeHigh += 1
            mmLatticeLow -= 1


        #Pass 3new - in Z
        
        #Reset Values        
        mmScaleGrowValue = mmScaleGrowValueOverall
        mmLatticeLow = mmLatticeMax/2-1
        mmLatticeHigh = mmLatticeMax/2

        while ( mmLatticeLow != 0 ):
            #cmds.select( mmNewLattice[1] + ".pt" + str(mmListX) + str(mmListY) + str(mmListZ), r = 1 )
            
            cmds.select( mmNewLattice[1] + ".pt[0:" + str(mmLatticeMax) + "][0:" + str(mmLatticeMax) + "][" + str(mmLatticeLow) +" : " + str(mmLatticeHigh) + "]", r = 1 )
            
            cmds.scale( 1 + mmScaleGrowValue, 1+ mmScaleGrowValue, 1, pivot = mmPivot )
            mmScaleGrowValue = mmScaleGrowValue*mmScaleRateOfShrink
            mmLatticeHigh += 1
            mmLatticeLow -= 1



        cmds.select(mmNewLattice, r = 1)
        
        cmds.HideSelectedObjects()