"""

Function: mmRiggingFunctions
Description: This is a collection of functions which help out with Rigging in general.

"""
#This treats everything as a float if it matters (during division only)
from __future__ import division

__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import time
import re as regex

#Local
import mmUVFunctions as mmUVF
import mmOrganizationFunctions as mmOF
import mmModelingFunctions as mmMF
import mmGetWorldTrans as mmGWT

######################################
############# DEFINES ################
######################################

#------------------------------------------------------------
#Rigging Functions   
#------------------------------------------------------------

'''
Function: Creates an auto IK/FK switch and corresponding Attribute for a selected Joint Skeleton on a Nurbs Curve
Must select a controlling icon, and then the first bone of a 3 joint chain
'''
def autoIKFK( mmNumberOfBonesInLegSystem = None, mmListOfIconAndBoneChain = [], mmIKControlPreviouslyMade = None, *args ):

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

    #Need to keep track of things we are creating, and then pass them back to the whatever called the function.
    mmDictOfIKFKSwitchLists = {}
    mmIKCreations = []
    
    #Get info if possible
    switchLabel = cmds.textFieldButtonGrp("ikfkSwitchLabel", q = 1, text = 1)
    if (switchLabel == "Switch Label"):
        switchLabel = "ik_fk_switch"

    if ( mmListOfIconAndBoneChain == [] ):
        mmSelectedInScene = cmds.ls(sl=1)

        #break if nothing selected
        if(mmSelectedInScene == []):
            print "Nothing is selected"
            return None

        nurbsCurveVal = mmSelectedInScene[0]
        jointSystemChain = cmds.ls(mmSelectedInScene[1], dag = 1)
        mmOriginalJointChain = jointSystemChain
    else:
        nurbsCurveVal = mmListOfIconAndBoneChain[0]
        jointSystemChain = cmds.ls(mmListOfIconAndBoneChain[1], dag = 1)
        mmOriginalJointChain = jointSystemChain

    if ( mmNumberOfBonesInLegSystem == None ):
        mmNumberOfBonesInLegSystem = cmds.intField("createIKSplineArmNumBonesVal", q = 1, v = 1)
            

    
    #Create a master group to put everything that isn't spline in, to clean up the outliner
    overallGroup = cmds.group(n = switchLabel + "_overall_group#", em = 1)
    
    #Check if user wants Stretchyness of arm
    stretchyActivation = cmds.checkBoxGrp("ikfkSwitchChkBoxes", q = 1, v1 = 1)
    
    #Creates a new attribute to switch on the curve selected between ik and fk arms
    cmds.addAttr (nurbsCurveVal, ln = switchLabel,  at = 'double', min = 0, max = 10, dv = 0)
    nurbsCurveAttr = nurbsCurveVal + "." + switchLabel
    cmds.setAttr (nurbsCurveAttr, e= 1, k = 1)
    
    #Creates a new attribute to toggle the stretchyness
    if (stretchyActivation):
        cmds.addAttr (nurbsCurveVal, ln = "stretch_toggle",  at = 'enum', en = "off:on:", dv = 1)
        nurbsStretchAttr = nurbsCurveVal + ".stretch_toggle"
        cmds.setAttr (nurbsStretchAttr, e= 1, k = 1)
    
    #Before duplicating, lets ensure that the joints are oriented properly
    mmCounterInner = 0
    mmOriginalJointChainLen = len(mmOriginalJointChain)

    for mmJoint in mmOriginalJointChain:
    
        cmds.select( mmOriginalJointChain[mmCounterInner] )
        #If there is a next joint, and if it is higher in Y than this joint, then flip the Z orientation so that all bones rotate the 'same way' when in FK mode.
        if ( mmCounterInner < mmOriginalJointChainLen - 1 ):

            mmCurrentJointYValue = cmds.xform(q = 1, pivots = 1, ws = 1)[1]

            cmds.select( mmOriginalJointChain[mmCounterInner+1] )
            mmNextJointYValue = cmds.xform(q = 1, pivots = 1, ws = 1)[1]

            #re-select the one you want
            cmds.select( mmOriginalJointChain[mmCounterInner] )

            if ( mmCurrentJointYValue > mmNextJointYValue ):
                cmds.joint( edit = True, orientJoint = 'yzx', secondaryAxisOrient = 'zup', children = False, zeroScaleOrient = True )
            else:
                cmds.joint( edit = True, orientJoint = 'yzx', secondaryAxisOrient = 'zdown', children = False, zeroScaleOrient = True )


        else:
            cmds.joint( edit = True, orientJoint = 'yzx', secondaryAxisOrient = 'zup', children = False, zeroScaleOrient = True )

        mmCounterInner += 1

    #duplicate the joint chain twice
    ikSystemChain = cmds.duplicate(mmOriginalJointChain, rr = 1, rc = 1)
    
    fkSystemChain = cmds.duplicate(mmOriginalJointChain, rr = 1, rc = 1)

    #If there are additional bones created, delete all except how many we want in the leg system
    originalJointLen = len(mmOriginalJointChain)

    if ( originalJointLen > mmNumberOfBonesInLegSystem ):

        mmCounter = originalJointLen - 1
        while ( ( len(ikSystemChain) ) > mmNumberOfBonesInLegSystem ):
        
            cmds.select( ikSystemChain[mmCounter] )
            cmds.delete()
            del ikSystemChain[ mmCounter ]
            mmCounter -= 1

        mmCounter = originalJointLen - 1
        while ( ( len(fkSystemChain) ) > mmNumberOfBonesInLegSystem ):
            cmds.select( fkSystemChain[mmCounter] )
            cmds.delete()
            del fkSystemChain[ mmCounter ]
            mmCounter -= 1

    #rename original joint chain to mark it as the bind chain
    mmBoolCheck = True
    mmFirstName = ""

    for jt in jointSystemChain:

        newName = "bind_" + jt
        #This while loop is here to check if a name exists - since maya doesn't do that for us)
        while cmds.objExists(newName):
            #This crazy stuff is regex, its looking within the string, splitting apart what it finds into a bunch of stuff and some (or no) digits at the end,
            #   Then increments that value (or starts at 1) and checks that name
            jointName, jointNum = regex.match(r'^(.*?)(\d*)$', newName).groups()
            newName = jointName + str(1 + int(jointNum or '0'))

        cmds.rename(jt,newName)

        if (mmBoolCheck):
            mmFirstName = newName
            mmBoolCheck = False

    originalChainName = cmds.ls((mmFirstName),dag=1)

    #rename 1st duplicate joint chain to mark it as the ik chain
    mmBoolCheck = True
    mmFirstName = ""

    for jt in ikSystemChain:

        newName = "ik_" + jt
        while cmds.objExists(newName):
            jointName, jointNum = regex.match(r'^(.*?)(\d*)$', newName).groups()
            newName = jointName + str(1 + int(jointNum or '0'))

        cmds.rename(jt,newName)

        if (mmBoolCheck):
            mmFirstName = newName
            mmBoolCheck = False

    newIKChain = cmds.ls((mmFirstName),dag=1)

    #rename 2nd duplicate joint chain to mark it as the fk chain
    mmBoolCheck = True
    mmFirstName = ""

    for jt in fkSystemChain:

        newName = "fk_" + jt
        while cmds.objExists(newName):
            jointName, jointNum = regex.match(r'^(.*?)(\d*)$', newName).groups()
            newName = jointName + str(1 + int(jointNum or '0'))

        cmds.rename(jt,newName)

        if (mmBoolCheck):
            mmFirstName = newName
            mmBoolCheck = False

    newFKChain = cmds.ls((mmFirstName),dag=1)

    #Save joint chains to pass back later
    mmDictOfIKFKSwitchLists["bindBone"] = (originalChainName)
    mmDictOfIKFKSwitchLists["ikBone"] = (newIKChain)
    mmDictOfIKFKSwitchLists["fkBone"] = (newFKChain)

    #---------------------------------------------------------------------------------------

    #Create an IK Handle on the IK Arm
    ikHandleBaseJoint = newIKChain[0] + ".rotatePivot"
    ikHandleEndJoint = newIKChain[mmNumberOfBonesInLegSystem - 1] + ".rotatePivot"

    cmds.select( ikHandleBaseJoint, r = 1)
    cmds.select( ikHandleEndJoint, add = 1)

    #For now, just use RP
    cmds.ikHandle(ap = 1, sol = "ikRPsolver", n = mmOriginalJointChain[0] + "_ikHandle")

    '''
    #Want to use a spring solver for more than 3 bones.
    #?  Removing this because ikSpringSolver appears to not work when scale is involved.
    #If a 3 bone system, use normal rotation plane solver.
    if ( mmNumberOfBonesInLegSystem == 3 ):
        cmds.ikHandle(ap = 1, sol = "ikRPsolver", n = mmOriginalJointChain[0] + "_ikHandle")
    #Otherwise use a spring solver.
    elif ( mmNumberOfBonesInLegSystem > 3 ):
        mel.eval("ikSpringSolver;")
        cmds.ikHandle(ap = 1, sol = "ikSpringSolver", n = mmOriginalJointChain[0] + "_ikHandle")
    #Or error.
    else:
        bob = "ERROR: IKFK system requires 3 or more bones."
        print bob
        return bob
    '''

    overallArmIKHandleName = cmds.ls(sl = 1)[0]
    
    cmds.parent(overallArmIKHandleName, overallGroup)
    
    #create an icon for the IK arm and connect it to the ikHandle
    #   If a control wasn't made before, otherwise use that.
    if ( mmIKControlPreviouslyMade == None ):
        ikIconName = mmOF.createTextBox( "IK", None, [0,0,0], [1,1,1], [1,1,1], "box" )
        ikIconName = cmds.rename(ikIconName, overallArmIKHandleName + "_Control")
        mmTrashPC = cmds.pointConstraint(overallArmIKHandleName, ikIconName, mo = 0)
        cmds.delete(mmTrashPC)
        
        cmds.parent(ikIconName, overallGroup)

    else:
        ikIconName = mmIKControlPreviouslyMade

    IKHandleConstraint = cmds.pointConstraint(ikIconName, overallArmIKHandleName, mo = 1)

    #Store IK Icons for passing back
    mmIKCreations.append(ikIconName)
    mmIKCreations.append(overallArmIKHandleName)
    mmIKCreations.append(IKHandleConstraint)

    mmDictOfIKFKSwitchLists["ikIcon"] = mmIKCreations
    
    #point constrain the IK and FK arm roots to the control arm
    cmds.pointConstraint(originalChainName[0], newIKChain[0], mo = 1)
    cmds.pointConstraint(originalChainName[0], newFKChain[0], mo = 1)
    
    #---------------------------------------------------------------------------------------

    #Create FK Icons
    mmFKCreationList, fkIconNameList = mmCreateFKControls( newFKChain, mmNumberOfBonesInLegSystem, overallGroup )

    mmDictOfIKFKSwitchLists["fkIcon"] = mmFKCreationList

    #---------------------------------------------------------------------------------------
    
    #Need to create a polevector control in the proper place
    mmPoleVector = mmCreatePoleVector( newIKChain, overallArmIKHandleName, "PV" )[0]

    #Put pole vector pad into hierarchy
    cmds.parent(mmPoleVector, "root_Control")

    #Pass back in returns
    mmDictOfIKFKSwitchLists["poleVector"] = [mmPoleVector]

    #Orient the last bone in the IK chain to the IK handle - this shouldn't matter, but hopefully provides necessary information
    cmds.orientConstraint(ikIconName,newIKChain[len(newIKChain)-1])

    #---------------------------------------------------------------------------------------
    
    #Need to pass through all created items and grab various names to plug in to SDKs.
    mmIterate = 0
    ikfk_blendColor_Dict = {}

    while ( mmIterate < mmNumberOfBonesInLegSystem ):

        ikfk_blendColor_Dict[mmIterate] = mmCreateBlendSystem( originalChainName[mmIterate], newIKChain[mmIterate], newFKChain[mmIterate])

        mmIterate += 1

    #Do another pass for connecting all the various pieces together in SDKs
    mmIterate = 0

    while ( mmIterate < mmNumberOfBonesInLegSystem ):

        #mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
        #Example: mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-10, 10], [90, 0], 1 )
        mmCreateSDK( nurbsCurveAttr, ikfk_blendColor_Dict[mmIterate], ".blender", [0, 10], [0, 1], 1 )

        mmIterate += 1

    #Also need to hide the visibility attr of each control (because it has an sdk on it now and don't want the user breaking it).
    
    mmCreateSDK( nurbsCurveAttr, ikIconName, ".visibility", [0, 0.5, 9.5, 10], [1, 1, 1, 0], 1 )
    cmds.setAttr (ikIconName + ".visibility", k = 0 )

    mmCreateSDK( nurbsCurveAttr, mmPoleVector, ".visibility", [0, 0.5, 9.5, 10], [1, 1, 1, 0], 1 )
    cmds.setAttr (mmPoleVector + ".visibility", k = 0 )

    #set all of the fkIconNameList visibilities as well
    i = 0
    while (i <= len(fkIconNameList)-1):
        mmCreateSDK( nurbsCurveAttr, fkIconNameList[i], ".visibility", [0, 0.5, 9.5, 10], [0, 1, 1, 1], 1 )
        cmds.setAttr (fkIconNameList[i] + ".visibility", k = 0 )
        i += 1

    #---------------------------------------------------------------------------------------
    
    if(stretchyActivation):

        #change ik/fk system to be stretchy
        #regular stretch (no elbow stretch)

        #Create variables
        stretch_distanceShapeNodeName_dict = {}
        stretch_locator_dict = {}

        mmIterate = 0
        while ( mmIterate < mmNumberOfBonesInLegSystem ):
            #create a distance node to find the space between upper joints
            stretch_distanceShapeNodeName_dict[mmIterate] = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmOriginalJointChain[mmIterate] + "_distanceNode#")

            #create locators
            stretch_locator_dict[mmIterate] = cmds.spaceLocator( p = [0,0,0], n = mmOriginalJointChain[mmIterate] + "_Stretch_Locator#")[0]

            mmIterate += 1

        stretch_distanceShapeNodeName_overall = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmOriginalJointChain[mmNumberOfBonesInLegSystem - 1] + "_distanceNode#")
        
        #attach locators to distance node
        cmds.connectAttr(stretch_locator_dict[0] + ".translate", stretch_distanceShapeNodeName_dict[0] + ".point1")

        mmIterate = 1
        while ( mmIterate < mmNumberOfBonesInLegSystem ):
            cmds.connectAttr(stretch_locator_dict[mmIterate] + ".translate", stretch_distanceShapeNodeName_dict[mmIterate - 1] + ".point2")

            #If the next pass through the dictionary will work, then connect point 1 of the next distance node
            if ( mmIterate + 1 < mmNumberOfBonesInLegSystem ):
                cmds.connectAttr(stretch_locator_dict[mmIterate] + ".translate", stretch_distanceShapeNodeName_dict[mmIterate] + ".point1")

            mmIterate += 1

        #Hook up the overall distance node
        cmds.connectAttr(stretch_locator_dict[0] + ".translate", stretch_distanceShapeNodeName_overall + ".point1")
        cmds.connectAttr(stretch_locator_dict[mmNumberOfBonesInLegSystem - 1] + ".translate", stretch_distanceShapeNodeName_overall + ".point2")
        
        #move locators to selected joint and its first child
        mmIterate = 0
        while ( mmIterate < mmNumberOfBonesInLegSystem - 1 ):
            cmds.pointConstraint(newIKChain[mmIterate], stretch_locator_dict[mmIterate], mo = 0)
        
            mmIterate += 1

        mmStretchLocator = stretch_locator_dict[mmNumberOfBonesInLegSystem - 1]
        mmStretchLocatorPointConstraint = cmds.pointConstraint(ikIconName, stretch_locator_dict[mmNumberOfBonesInLegSystem - 1], mo = 0)

        #Create a list of strings/values which can be used to create a giant "if" statement for maya to use in its expression editor
        IKBone_Dist_Dict = {}
        stretch_IKBone_static_dict = {}
        stretch_IKBone1_Distance_ratio_static_dict = {}
        stretch_IKBoneDistance_static = 0
        newIKChain_name_dict = {}
        newFKChain_name_dict = {}
        originalChain_name_dict = {}

        mmIterate = 0
        while ( mmIterate < mmNumberOfBonesInLegSystem ):
            IKBone_Dist_Dict[mmIterate] = stretch_distanceShapeNodeName_dict[mmIterate] + ".distance"
            stretch_IKBone_static_dict[mmIterate] = cmds.getAttr( IKBone_Dist_Dict[mmIterate] )
            newIKChain_name_dict[mmIterate] = newIKChain[mmIterate]
            newFKChain_name_dict[mmIterate] = newFKChain[mmIterate]
            originalChain_name_dict[mmIterate] = originalChainName[mmIterate]

            #Add up how large the ik bones are together
            stretch_IKBoneDistance_static += stretch_IKBone_static_dict[mmIterate]

            mmIterate += 1

        #Need to compute something with total length, so have to split it out to a separate while loop.
        mmIterate = 0
        while ( mmIterate < mmNumberOfBonesInLegSystem ):
            stretch_IKBone1_Distance_ratio_static_dict = stretch_IKBone_static_dict[mmIterate] / stretch_IKBoneDistance_static

            mmIterate += 1

        #Computer overall outside the while loops.
        overall_Dist_Name = stretch_distanceShapeNodeName_overall + ".distance"
        stretch_overallDistance_static = cmds.getAttr(overall_Dist_Name)

        
        #Add attribute to the main control curve which will allow the arm to be stretched further than normally possible
        cmds.addAttr(nurbsCurveVal, ln = "manually_stretch_arm",  at = 'float', min = -50, max = 100, dv = 0, k = 1)
        nurbsCurveStretchAttr = nurbsCurveVal + ".manually_stretch_arm"

        expression_stretch_values = ""
        
        # print locals()
        expression_stretch_values = '''if ( {nurbsStretchAttr} && {overall_Dist_Name} >= {stretch_IKBoneDistance_static} ){{\r\n'''.format(**locals())

        #Run through loop of desired information, adding to the expression as we go.
        mmIterate = 0
        while ( mmIterate < mmNumberOfBonesInLegSystem - 1 ):
            mmReplacer = newIKChain_name_dict[mmIterate]
            expression_stretch_values += '''   {mmReplacer}.sy = 1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr}*{nurbsStretchAttr} /10 );\r\n'''.format(**locals())
            
            mmReplacer = newFKChain_name_dict[mmIterate]
            expression_stretch_values += '''   {mmReplacer}.sy = 1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr}*{nurbsStretchAttr} /10 );\r\n'''.format(**locals())
            
            mmReplacer = originalChain_name_dict[mmIterate]
            expression_stretch_values += '''   {mmReplacer}.sy = 1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr}*{nurbsStretchAttr} /10 );\r\n'''.format(**locals())

            mmIterate += 1

        expression_stretch_values += '}\r\nelse {\r\n'

        mmIterate = 0
        while ( mmIterate < mmNumberOfBonesInLegSystem - 1 ):
            mmReplacer = newIKChain_name_dict[mmIterate]
            expression_stretch_values += '''   {mmReplacer}.sy = 1 + {nurbsCurveStretchAttr}*{nurbsStretchAttr} /10;\r\n'''.format(**locals())
            
            mmReplacer = newFKChain_name_dict[mmIterate]
            expression_stretch_values += '''   {mmReplacer}.sy = 1 + {nurbsCurveStretchAttr}*{nurbsStretchAttr} /10;\r\n'''.format(**locals())
            
            mmReplacer = originalChain_name_dict[mmIterate]
            expression_stretch_values += '''   {mmReplacer}.sy = 1 + {nurbsCurveStretchAttr}*{nurbsStretchAttr} /10;\r\n'''.format(**locals())

            mmIterate += 1

        expression_stretch_values += '}'

        cmds.expression(s=expression_stretch_values, n=("stretchyArm_expression"), ae=0, uc=all )

        #Organizing
        mmIterate = 0
        while ( mmIterate < mmNumberOfBonesInLegSystem ):

            cmds.parent(stretch_locator_dict[mmIterate], overallGroup)

            mmIterate += 1

    #---------------------------------------------------------------------------------------

    #putting things into a group for cleaning purposes
    cmds.parent(originalChainName[0], overallGroup)
    cmds.parent(newIKChain[0], overallGroup)
    cmds.parent(newFKChain[0], overallGroup)

    cmds.select(ikIconName)

    mmDictOfIKFKSwitchLists["distanceSystem"] = [mmStretchLocator, mmStretchLocatorPointConstraint]
    mmDictOfIKFKSwitchLists["fkikSwitch"] = [nurbsCurveVal]
    mmDictOfIKFKSwitchLists["orgFolder"] = [overallGroup]

    return mmDictOfIKFKSwitchLists

'''
This function takes in stuff, and creates FK controls on however many bones requestted, then passes back information.
'''
def mmCreateFKControls( newFKChain = [], mmNumberOfBonesInLegSystem = 0, overallGroup = "", mmPossibleParentJoint = "", mmName = "FK", *args ):

    if (newFKChain == [] or mmNumberOfBonesInLegSystem == 0 or overallGroup == ""):
        print "mmRF.mmCreateFKControls provided invalid information."
        return None

    fkIconNameList = []
    mmLastFKIcon = ""
    mmCounter = 0
    mmFKCreationList = []

    if (mmPossibleParentJoint != ""):
        mmLastFKIcon = mmPossibleParentJoint

    #Create Icons for the FK arm and connect them to the FK arm
    while ( mmCounter < mmNumberOfBonesInLegSystem - 1 ):
        mmFKCreations = []
            
        # Create an 'FK' Text box so the control is easy to identify
        myCircleName = mmOF.createTextBox( mmName+str(mmCounter), None, [0,0,0], [1,1,1], [1,1,1], "circle" )
        cmds.rotate( 180, 0, 0 )
        cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)
        
        cmds.select(myCircleName, r = 1)
        cmds.select(newFKChain[mmCounter], add = 1)
        
        mmFKCreations = padAndAlign(3)
        fkIconPad2 = mmFKCreations[2]

        #Set the icon to follow the bone it is on.
        cmds.pointConstraint(newFKChain[mmCounter], fkIconPad2, mo = 0)

        #find new name of icon
        cmds.select(fkIconPad2, r = 1)
        cmds.pickWalk(d = "down")
        fkIconName = cmds.pickWalk(d = "down")[0]
        fkIconName = cmds.rename(fkIconName, newFKChain[mmCounter] + "_control")

        if( mmLastFKIcon != "" ):
            cmds.orientConstraint(mmLastFKIcon, mmFKCreations[1], mo = 1)

        #Put padded icon into the proper hierarchy
        if( mmCounter == 0):
            mmParentCheck = cmds.listRelatives(fkIconPad2, p = 1)
            if (mmParentCheck != overallGroup):
                cmds.parent(fkIconPad2, overallGroup)
        
        #Store FK information
        fkIconNameList.append(fkIconName)
        mmFKCreations[0] = fkIconName
        mmLastFKIcon = fkIconName
        mmFKCreationList.append(mmFKCreations)

        mmCounter += 1

    return mmFKCreationList, fkIconNameList

'''
This function takes in a bone chain, an IKHandle, and a name, then creates a polevector in the 'proper' place, returns a list of the icon and the pad it is under.
'''
def mmCreatePoleVector( mmBoneChain = None, mmIKHandleName = None, mmName = None, *args ):

    #Use first and last bone - may cause issues in legs with small bends (mostly strait)
    mmBoneChainLen = len(mmBoneChain) - 1

    #Grab vector information of first 3 joints of mmBoneChain
    mmPointStartLoc = cmds.joint(mmBoneChain[0], q = 1, p = 1, a = 1)
    mmPointMidLoc = cmds.joint(mmBoneChain[1], q = 1, p = 1, a = 1)
    mmPointEndLoc = cmds.joint(mmBoneChain[mmBoneChainLen], q = 1, p = 1, a = 1)

    mmPointStartVector = om.MVector(mmPointStartLoc[0],mmPointStartLoc[1],mmPointStartLoc[2])
    mmPointMidVector = om.MVector(mmPointMidLoc[0],mmPointMidLoc[1],mmPointMidLoc[2])
    mmPointEndVector = om.MVector(mmPointEndLoc[0],mmPointEndLoc[1],mmPointEndLoc[2])

    mmMidPointVector = mmPointEndVector + (mmPointStartVector - mmPointEndVector)*.5

    mmPoleVectorVector = mmPointMidVector + (mmPointMidVector - mmMidPointVector)

    #----------------------------------------------------------------------------------------
    
    #Create Icon & move to location
    mmPoleVectorControl = mmOF.createTextBox( mmName, None, [0,0,0], [1,1,1], [2,2,2], "text" )

    cmds.move(mmPoleVectorVector.x, mmPoleVectorVector.y, mmPoleVectorVector.z)

    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

    #Connect to IKHandle
    cmds.poleVectorConstraint( mmPoleVectorControl, mmIKHandleName )

    mmPoleVectorControl = cmds.rename(mmPoleVectorControl, str(mmBoneChain[0]) + "_pv")

    return [mmPoleVectorControl]

'''
This function takes in relevant information to the pole vector, and creates an autonomous system that helps keep the pole vector in place.
#Note: This function may report cycles in the script editor.  Think these are fine as there aren't cycles after the fact.
#   Can check if there are cycles with "print cmds.cycleCheck()"
#   Also beneficial (sometimes) to have cmds.refresh() before/after a script to ensure the dag is cleaned out and there isn't really a cycle.
#?  Should get rid of these cycles eventually.
'''

'''
new version:

def mmAutonomousPoleVectorSystem( mmBoneChain = None, mmIKHandleName = None, mmPoleVectorControl = None, mmStartControl = None, mmEndControl = None, *args ):

    """
    #Attempt 2:
    After the leg is created
    Create a bone at the start and at the parent object (like the thigh), then orient the bones
    Create a bone at the start and at the end(foot), then orient the bones
    *Should the bones be oriented? We want them to be zero'd for sure, but don't we want the angles to match up perfectly - i.e. oriented to world?  Test?
    Create a scIKHandle for both new bone pairs
    Parent constrain the ikhandles under the respective thing which should control the aimer.
    Parent constrain the pole vector group under the start bones of each of the new bone pairs.
    Create controls which allow the PV to swap which parent it is using - or jump to world.
    Organize all the new things created.
    """
    if None in [mmBoneChain, mmIKHandleName, mmPoleVectorControl, mmStartControl, mmEndControl]:
        print "mmRF.mmAutonomousPoleVectorSystem was givin invaled information."
        return None

    #Find position of bone chain
    mmPointStartLoc = cmds.joint(mmBoneChain[0], q = 1, p = 1, a = 1)

    #Find position of start control
    cmds.select(mmStartControl)
    mmPointStartChildLoc = cmds.xform( q = 1, pivots = 1, ws = 1)

    #Find position of end control
    cmds.select(mmEndControl)
    mmPointEndChildLoc = cmds.xform( q = 1, pivots = 1, ws = 1)

    #Create a space switcher for the PV
    mmPoleVectorControlAutoKneePad = mmOF.mmGroupInPlace(mmPoleVectorControl, "_AutoKnee_Pad")
    mmPoleVectorControlWorldPad = mmOF.mmGroupInPlace(mmPoleVectorControl, "_World_Pad")

    #----------------------------------------------------------------------------------------

    mmPV_StartAimer = cmds.joint( p = (mmPointStartLoc[0],mmPointStartLoc[1],mmPointStartLoc[2]), n = "poleVector_placeHolder_startAimer_#")
    mmPV_StartChild = cmds.joint( p = (mmPointStartChildLoc[0],mmPointStartChildLoc[1],mmPointStartChildLoc[2]), n = "poleVector_placeHolder_startChild_#")
    
    cmds.select(cl = 1)
    mmPV_EndAimer = cmds.joint( p = (mmPointStartLoc[0],mmPointStartLoc[1],mmPointStartLoc[2]), n = "poleVector_placeHolder_endAimer_#")
    mmPV_EndChild = cmds.joint( p = (mmPointEndChildLoc[0],mmPointEndChildLoc[1],mmPointEndChildLoc[2]), n = "poleVector_placeHolder_endChild_#")

    mmPV_StartAimerPad = mmOF.mmGroupInPlace(mmPV_StartAimer)
    mmPV_EndAimerPad = mmOF.mmGroupInPlace(mmPV_EndAimer)

    cmds.pointConstraint(mmBoneChain[0], mmPV_StartAimerPad, mo = 1)
    cmds.pointConstraint(mmBoneChain[0], mmPV_EndAimerPad, mo = 1)

    #Create scIKHandles
    mmPV_StartIKHandleName = mmCreateIKHandle( mmPV_StartAimer, mmPV_StartChild, "sc" )
    mmPV_EndIKHandleName = mmCreateIKHandle( mmPV_EndAimer, mmPV_EndChild, "sc" )

    #Have the follow ikHandles constrain to the start and end controllers
    cmds.pointConstraint(mmStartControl, mmPV_StartIKHandleName, mo = 1)
    cmds.pointConstraint(mmEndControl, mmPV_EndIKHandleName, mo = 1)

    #----------------------------------------------------------------------------------------
    
    #Create a space switcher for the PV
    mmCreatedAutoBendAttr = spaceSwitcherMulti( 3, mmEndControl, [mmPoleVectorControlAutoKneePad], [mmPV_StartAimer, mmPV_EndAimer], True, "ParentToFoot" )
    mmCreatedSpaceSwitchAttr = spaceSwitcherMulti( 3, mmEndControl, [mmPoleVectorControlWorldPad], [mmPoleVectorControlAutoKneePad, "root_Control"], True, "AutoKneeToRoot" )

    #Set autoknee to halfway between start and stop - generally should be good for legs.
    cmds.setAttr(mmCreatedAutoBendAttr, 5)

    #Organize
    mmPoleVectorOverallGroup = cmds.group(em = 1, n = "poleVector_Group_#")
    cmds.parent(mmPoleVectorControlAutoKneePad, mmPV_StartAimerPad, mmPV_EndAimerPad, mmPV_StartIKHandleName, mmPV_EndIKHandleName, mmPoleVectorOverallGroup)

    return [mmPV_StartAimer, mmPV_EndAimer, mmCreatedSpaceSwitchAttr, mmCreatedAutoBendAttr, mmPoleVectorControlWorldPad, mmPoleVectorOverallGroup]
'''

'''
old version:
#? Unsure why new version commented out, did we not finish something?  Was the new idea bad?  What was the new idea?
'''
def mmAutonomousPoleVectorSystem( mmBoneChain = None, mmIKHandleName = None, mmPoleVectorControl = None, mmStartControl = None, mmEndControl = None, *args ):
    
    if None in [mmBoneChain, mmIKHandleName, mmPoleVectorControl, mmStartControl, mmEndControl]:
        print "mmRF.mmAutonomousPoleVectorSystem was givin invaled information."
        return None

    mmPointStartLoc = cmds.joint(mmBoneChain[0], q = 1, p = 1, a = 1)

    #Create a space switcher for the PV
    mmPoleVectorControlPad = mmOF.mmGroupInPlace(mmPoleVectorControl)

    #----------------------------------------------------------------------------------------

    mmPV_StartAimer = cmds.spaceLocator(n = "poleVector_placeHolder_startAimer_#")[0]
    cmds.move(mmPointStartLoc[0],mmPointStartLoc[1],mmPointStartLoc[2])
    mmOF.changeColor(9)
    mmPV_EndAimer = cmds.spaceLocator(n = "poleVector_placeHolder_endAimer_#")[0]
    cmds.move(mmPointStartLoc[0],mmPointStartLoc[1],mmPointStartLoc[2])
    mmOF.changeColor(9)
    cmds.parent( mmPV_EndAimer, mmPV_StartAimer )

    mmPV_StartAimerPad = mmOF.mmGroupInPlace(mmPV_StartAimer)

    cmds.pointConstraint(mmBoneChain[0], mmPV_StartAimerPad, mo = 1)

    #Have the follow locators aim in the direction of the IK
    mmStartPointAimConstraint = cmds.aimConstraint( mmEndControl, mmPV_StartAimer, mo = 0, wuo = mmStartControl, aim = [0,-1,0], upVector = [1,0,0], worldUpVector = [1,0,0], worldUpType = "objectrotation" )
    #Have the follow locators aim in the direction of the IK
    mmEndPointAimConstraint = cmds.aimConstraint( mmEndControl, mmPV_EndAimer, mo = 0, wuo = mmEndControl, aim = [0,-1,0], upVector = [1,0,0], worldUpVector = [1,0,0], worldUpType = "objectrotation" )

    cmds.setKeyframe( mmPV_EndAimer + ".rx")
    cmds.setKeyframe( mmPV_EndAimer + ".ry")
    cmds.setKeyframe( mmPV_EndAimer + ".rz")
    mmBlendEndAimAttr = mmPV_EndAimer + ".blendAim1"

    cmds.setAttr(mmBlendEndAimAttr, 1)


    #----------------------------------------------------------------------------------------
    
    #Create a space switcher for the PV
    mmCreatedSpaceSwitchAttr = spaceSwitcherMulti( 3, mmEndControl, [mmPoleVectorControlPad], [mmPV_EndAimer, "root_Control"], True, "AutoKneeToRoot" )

    #Create an attribute for swapping between the start and end controls
    mmStartControlNameSplit = mmStartControl.split("_")
    mmEndControlNameSplit = mmEndControl.split("_")
    mmCreatedAutoBendAttrName = mmEndControlNameSplit[0] + "_To_" + mmStartControlNameSplit[0] 
    mmCreatedAutoBendAttr = mmEndControl + "."+ mmCreatedAutoBendAttrName

    #Create an Attr to control whether the knee follows the foot or the pelvis
    cmds.addAttr(mmEndControl, ln = mmCreatedAutoBendAttrName, at = "double", min = 0, max = 10, dv = 0, k = 1)

    #mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
    #Example: mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-10, 10], [90, 0], 1 )
    mmCreateSDK( mmCreatedAutoBendAttr, mmPV_EndAimer, ".blendAim1", [0, 10], [1, 0], 1 )

    #Set autoknee to halfway between start and stop - generally good for legs.
    #?  This autoknee's aimers are freaking out when the points being aimed at move around too much.  Not worth keeping?
    cmds.setAttr(mmCreatedAutoBendAttr, 5)

    #Organize
    mmPoleVectorOverallGroup = cmds.group(em = 1, n = "poleVector_Group_#")
    cmds.parent(mmPV_StartAimerPad, mmPoleVectorOverallGroup)

    return [mmPV_StartAimer, mmPV_EndAimer, mmCreatedSpaceSwitchAttr, mmCreatedAutoBendAttr, mmPoleVectorControlPad, mmPoleVectorOverallGroup]




'''
This function takes in 3 selected objects, creates blendColors shanding nodes, .
'''
def mmCreateBlendSystem( mmBindObject = None, mmBlendObjectOne = None, mmBlendObjectTwo = None, *args ):

    if ( mmBindObject == None or mmBlendObjectOne == None or mmBlendObjectTwo == None ):
        print "mmRF.mmCreateBlendSystem was provide invalid information."
        return None

    #Create blendColor nodes and apply rotational information to them, and pass them to bind arm
    mmSNBlendColor = cmds.shadingNode("blendColors", au = 1, n = mmBindObject + "_blendColors#")
    
    mmIKJointRotateName = mmBlendObjectOne + ".rotate"
    mmFKJointRotateName = mmBlendObjectTwo + ".rotate"

    cmds.connectAttr(mmIKJointRotateName, mmSNBlendColor + ".color2", f =1)
    cmds.connectAttr(mmFKJointRotateName, mmSNBlendColor + ".color1", f =1)
    
    mmBindJointRotateName = mmBindObject + ".rotate"

    cmds.connectAttr(mmSNBlendColor + ".output", mmBindJointRotateName, f =1)

    #Return the created shader node which is doing the blending.
    return mmSNBlendColor

'''
This function creates an IK handle of the passed type between the two passed bones, and returns the IK handle name.
'''
def mmCreateIKHandle( mmParentBone, mmChildBone, mmTypeOfIKHandle, *args ):
    
    #print "mmParentBone ", mmParentBone, " mmChildBone ", mmChildBone
    
    if ( mmTypeOfIKHandle == "sc" ):
        mmHandleType = "ikSCsolver"
    elif ( mmTypeOfIKHandle == "rp" ):
        mmHandleType = "ikRPsolver"
    else:
        print "Invalid Choice"
        return Null
        
    ikHandleBaseJoint = mmParentBone + ".rotatePivot"
    ikHandleEndJoint = mmChildBone + ".rotatePivot"
    
    cmds.select( ikHandleBaseJoint, r = 1)
    cmds.select( ikHandleEndJoint, add = 1)
    
    cmds.ikHandle(ap = 1, sol = mmHandleType, n = mmParentBone + "_ikHandle")
    mmTempIKHandleName = cmds.ls(sl = 1)
    overallIKHandleName = mmTempIKHandleName[0]
    
    return overallIKHandleName

"""
#? This is the AutoIKFK with the bendy section - I removed it from the above because who knows if it works anymore (i.e. definitely doesn't work).
#?  But like a hoarder, I can't just get rid of it.. so it sits here.
def autoIKFK( mmNumberOfBonesInLegSystem = None, *args ):
    
    #Get info if possible
    switchLabel = cmds.textFieldButtonGrp("ikfkSwitchLabel", q = 1, text = 1)
    if (switchLabel == "Switch Label"):
        switchLabel = "ik_fk_switch"
    mmSelectedInScene = cmds.ls(sl=1)
    nurbsCurveVal = mmSelectedInScene[0]
    jointSystemChain = cmds.ls(mmSelectedInScene[1], dag = 1)
    mmOriginalJointChain = jointSystemChain

    #Bring in the user input values
    numDivisions = cmds.intField("createIKSplineArmDivVal", q = 1, v = 1)
        
    if ( mmNumberOfBonesInLegSystem == None ):
        mmNumberOfBonesInLegSystem = cmds.intField("createIKSplineArmNumBonesVal", q = 1, v = 1)
            
    #break if nothing selected
    if(mmSelectedInScene == []):
        print "Nothing is selected"
        return None
    
    #Create a master group to put everything that isn't spline in, to clean up the outliner
    overallGroup = cmds.group(n = switchLabel + "_overall_group", em = 1)
    
    #Check if user wants Bendyness of arm, this replaces the bind arm 
    bendyActivation = cmds.checkBoxGrp("ikfkSwitchChkBoxes", q = 1, v1 = 1)

    #Create a master group to put all spline objects in, to clean up the outliner
    if (bendyActivation):
        splineGroup = cmds.group(n = switchLabel + "_spline_group", em = 1)
    
    #Check if user wants Stretchyness of arm
    stretchyActivation = cmds.checkBoxGrp("ikfkSwitchChkBoxes", q = 1, v2 = 1)
    
    #Creates a new attribute to switch on the curve selected between ik and fk arms
    cmds.addAttr (nurbsCurveVal, ln = switchLabel,  at = 'double', min = 0, max = 10, dv = 0)
    nurbsCurveAttr = nurbsCurveVal + "." + switchLabel
    cmds.setAttr (nurbsCurveAttr, e= 1, k = 1)
    
    #Creates a new attribute to toggle the stretchyness
    if (stretchyActivation):
        cmds.addAttr (nurbsCurveVal, ln = "stretch_toggle",  at = 'enum', en = "off:on:", dv = 1)
        nurbsStretchAttr = nurbsCurveVal + ".stretch_toggle"
        cmds.setAttr (nurbsStretchAttr, e= 1, k = 1)
    
    # #Set the 3rd bone rotation to 0,0,0
    # #?  Unsure why this was done (cleanliness?), but it breaks skeletons with more bones than the leg (like with a foot.)
    # cmds.setAttr( jointSystemChain[2]+ ".jointOrientX", 0)
    # cmds.setAttr( jointSystemChain[2]+ ".jointOrientY", 0)
    # cmds.setAttr( jointSystemChain[2]+ ".jointOrientZ", 0)
    
    #duplicate the joint chain twice
    ikSystemChain = cmds.duplicate(mmOriginalJointChain, rr = 1, rc = 1)
    
    fkSystemChain = cmds.duplicate(mmOriginalJointChain, rr = 1, rc = 1)

    #If there are additional bones created, delete all except how many we want in the leg system
    originalJointLen = len(mmOriginalJointChain)

    if ( originalJointLen > mmNumberOfBonesInLegSystem ):

        mmCounter = originalJointLen - 1
        while ( ( len(ikSystemChain) ) > mmNumberOfBonesInLegSystem ):
        
            cmds.select( ikSystemChain[mmCounter] )
            cmds.delete()
            del ikSystemChain[ mmCounter ]
            mmCounter -= 1

        mmCounter = originalJointLen - 1
        while ( ( len(fkSystemChain) ) > mmNumberOfBonesInLegSystem ):
            cmds.select( fkSystemChain[mmCounter] )
            cmds.delete()
            del fkSystemChain[ mmCounter ]
            mmCounter -= 1

    #If using bendy, need to make a new "bind" skeleton
    if(bendyActivation):
        splineSystemChain = cmds.duplicate(mmOriginalJointChain, rr = 1, rc = 1)

        #rename original joint chain to mark it as the control chain
        for jt in jointSystemChain:
            newName = "control_" + jt
            cmds.rename(jt,newName)
        originalChainName = cmds.ls(('control_'+ jointSystemChain[0]),dag=1)
            
    else:
        #rename original joint chain to mark it as the bind chain
        for jt in jointSystemChain:
            newName = "bind_" + jt
            cmds.rename(jt,newName)
        originalChainName = cmds.ls(('bind_'+ jointSystemChain[0]),dag=1)
    
    #rename 1st duplicate joint chain to mark it as the ik chain
    for jt in ikSystemChain:
        newName = "ik_" + jt
        cmds.rename(jt,newName)
    newIKChain = cmds.ls(('ik_'+ ikSystemChain[0]),dag=1)

    #rename 2nd duplicate joint chain to mark it as the fk chain
    for jt in fkSystemChain:
        newName = "fk_" + jt
        cmds.rename(jt,newName)
    newFKChain = cmds.ls(('fk_'+ fkSystemChain[0]),dag=1)
    
    if(bendyActivation):
        #rename 3rd duplicate joint chain to mark it as the spline chain
        for jt in splineSystemChain:
            newName = "spline_" + jt
            cmds.rename(jt,newName)
        newSplineChain = cmds.ls('spline_'+ splineSystemChain[0])
    
    
    #Create an IK Handle on the IK Arm
    ikHandleBaseJoint = newIKChain[0] + ".rotatePivot"
    ikHandleEndJoint = newIKChain[mmNumberOfBonesInLegSystem - 1] + ".rotatePivot"

    cmds.select( ikHandleBaseJoint, r = 1)
    cmds.select( ikHandleEndJoint, add = 1)
    cmds.ikHandle(ap = 1, sol = "ikRPsolver", n = mmOriginalJointChain[0] + "_ikHandle")
    overallArmIKHandleName = cmds.ls(sl = 1)[0]
    
    cmds.parent(overallArmIKHandleName, overallGroup)
    
    #create an icon for the IK arm and connect it to the ikHandle
    mmOF.createCube()
    cmds.select(overallArmIKHandleName, add = 1)
    
    ikIconPad2Name = padAndAlign(1)[2]
    
    cmds.parent(ikIconPad2Name, overallGroup)
    
    cmds.setAttr(overallArmIKHandleName + ".visibility", 0)
    
    #find the new name of the IK Handle Icon
    cmds.select(ikIconPad2Name, r = 1)
    cmds.pickWalk(d = "down")
    ikIconNameString = cmds.pickWalk(d = "down")
    ikIconName = ikIconNameString[0]
    ikIconName = cmds.rename(ikIconName, overallArmIKHandleName + "_icon#")
    
    #point constrain the IK and FK arm roots to the control arm
    cmds.pointConstraint(originalChainName[0], newIKChain[0], mo = 1)
    cmds.pointConstraint(originalChainName[0], newFKChain[0], mo = 1)
    
    #Create Icons for the FK arm and connect them to the FK arm
    fkIconNameList = [""]
    mmCounter = 0
    while ( mmCounter <= mmNumberOfBonesInLegSystem - 2 ):
            
        myCircleName = cmds.circle()[0]
        cmds.rotate( '90deg', 0, 0 )
        cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)
        
        cmds.select(myCircleName, r = 1)
        cmds.select(newFKChain[mmCounter], add = 1)
        
        fkIconPad2 = padAndAlign(3)[2]

        #Set the icon to follow the bone it is on.
        cmds.pointConstraint(newFKChain[mmCounter], fkIconPad2, mo = 0)

        if( mmCounter >= 1 ):
            cmds.parent( fkIconPad2, fkIconName)
            fkIconNameList.append(fkIconName)

        #find new name of icon
        cmds.select(fkIconPad2, r = 1)
        cmds.pickWalk(d = "down")
        fkIconName = cmds.pickWalk(d = "down")[0]
        fkIconName = cmds.rename(fkIconName, newFKChain[mmCounter] + "_control")

        #Put padded icon into the proper hierarchy
        if( mmCounter == 0):
            cmds.parent(fkIconPad2, overallGroup)
            fkIconNameList.append(fkIconName)

        mmCounter += 1
    
    #Create blendColor nodes and apply rotational information to them, and pass them to bind arm
    ikfk_root_blendColors = cmds.shadingNode("blendColors", au = 1, n = mmOriginalJointChain[0] + "_blendColors#")
    ikfk_mid_blendColors = cmds.shadingNode("blendColors", au = 1, n = mmOriginalJointChain[1] + "_blendColors#")
    ikfk_end_blendColors = cmds.shadingNode("blendColors", au = 1, n = mmOriginalJointChain[2] + "_blendColors#")
    
    ikJointRoot = newIKChain[0] + ".rotate"
    fkJointRoot = newFKChain[0] + ".rotate"
    ikJointMid = newIKChain[1] + ".rotate"
    fkJointMid = newFKChain[1] + ".rotate"
    ikJointEnd = newIKChain[2] + ".rotate"
    fkJointEnd = newFKChain[2] + ".rotate"
    cmds.connectAttr(ikJointRoot, ikfk_root_blendColors + ".color2", f =1)
    cmds.connectAttr(fkJointRoot, ikfk_root_blendColors + ".color1", f =1)
    cmds.connectAttr(ikJointMid, ikfk_mid_blendColors + ".color2", f =1)
    cmds.connectAttr(fkJointMid, ikfk_mid_blendColors + ".color1", f =1)
    cmds.connectAttr(ikJointEnd, ikfk_end_blendColors + ".color2", f =1)
    cmds.connectAttr(fkJointEnd, ikfk_end_blendColors + ".color1", f =1)
    
    ctrlJointRoot = originalChainName[0] + ".rotate"
    ctrlJointMid = originalChainName[1] + ".rotate"
    ctrlJointEnd = originalChainName[2] + ".rotate"
    cmds.connectAttr(ikfk_root_blendColors + ".output", ctrlJointRoot, f =1)
    cmds.connectAttr(ikfk_mid_blendColors + ".output", ctrlJointMid, f =1)
    cmds.connectAttr(ikfk_end_blendColors + ".output", ctrlJointEnd, f =1)


    #Replace SDKs
    #mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
    #Example: mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-10, 10], [90, 0], 1 )
    mmCreateSDK( nurbsCurveAttr, ikfk_root_blendColors, ".blender", [0, 10], [0, 1], 1 )
    mmCreateSDK( nurbsCurveAttr, ikfk_mid_blendColors, ".blender", [0, 10], [0, 1], 1 )
    mmCreateSDK( nurbsCurveAttr, ikfk_end_blendColors, ".blender", [0, 10], [0, 1], 1 )
    mmCreateSDK( nurbsCurveAttr, ikIconName, ".visibility", [0, 0.5, 9.5, 10], [1, 1, 1, 0], 1 )
    mmCreateSDK( nurbsCurveAttr, newIKChain[0], ".visibility", [0, 0.5, 9.5, 10], [1, 1, 1, 0], 1 )
    mmCreateSDK( nurbsCurveAttr, newFKChain[0], ".visibility", [0, 0.5, 9.5, 10], [0, 1, 1, 1], 1 )
    
    #set all of the fkIconNameList visibilities as well
    i = 1
    while (i <= len(fkIconNameList)-1):
        mmCreateSDK( nurbsCurveAttr, fkIconNameList[i], ".visibility", [0, 0.5, 9.5, 10], [0, 1, 1, 1], 1 )
        i += 1


    
    #change arm system to be stretchy
    #regular stretch (no elbow stretch)

    if(stretchyActivation):
        #create a distance node to find the space between upper joints
        stretch_distanceShapeNodeName_bone1 = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmOriginalJointChain[0] + "_distanceNode#")
        stretch_distanceShapeNodeName_bone2 = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmOriginalJointChain[1] + "_distanceNode#")
        stretch_distanceShapeNodeName_overall = cmds.shadingNode("distanceBetween", asUtility = 1, n = mmOriginalJointChain[1] + "_distanceNode#")
        
        #create locators
        stretch_firstLocator = cmds.spaceLocator( p = [0,0,0], n = mmOriginalJointChain[0] + "_startLocator#")
        stretch_secondLocator = cmds.spaceLocator( p = [0,0,0], n = mmOriginalJointChain[0] + "_endLocator#")
        stretch_thirdLocator = cmds.spaceLocator( p = [0,0,0], n = mmOriginalJointChain[0] + "_endLocator#")
        
        #attach locators to distance node
        cmds.connectAttr(stretch_firstLocator[0] + ".translate", stretch_distanceShapeNodeName_bone1 + ".point1")
        cmds.connectAttr(stretch_secondLocator[0] + ".translate", stretch_distanceShapeNodeName_bone1 + ".point2")
        cmds.connectAttr(stretch_secondLocator[0] + ".translate", stretch_distanceShapeNodeName_bone2 + ".point1")
        cmds.connectAttr(stretch_thirdLocator[0] + ".translate", stretch_distanceShapeNodeName_bone2 + ".point2")
        cmds.connectAttr(stretch_firstLocator[0] + ".translate", stretch_distanceShapeNodeName_overall + ".point1")
        cmds.connectAttr(stretch_thirdLocator[0] + ".translate", stretch_distanceShapeNodeName_overall + ".point2")
        
        #move locators to selected joint and its first child
        cmds.pointConstraint(newIKChain[0], stretch_firstLocator, mo = 0)
        cmds.pointConstraint(newIKChain[1], stretch_secondLocator, mo = 0)
        cmds.pointConstraint(ikIconName, stretch_thirdLocator, mo = 0)
        
        IKBone1_Dist_Name = stretch_distanceShapeNodeName_bone1 + ".distance"
        IKBone2_Dist_Name = stretch_distanceShapeNodeName_bone2 + ".distance"
        overall_Dist_Name = stretch_distanceShapeNodeName_overall + ".distance"
        stretch_IKBone1_static = cmds.getAttr(IKBone1_Dist_Name)
        stretch_IKBone2_static = cmds.getAttr(IKBone2_Dist_Name)
        stretch_IKBoneDistance_static =  cmds.getAttr(IKBone1_Dist_Name) + cmds.getAttr(IKBone2_Dist_Name)
        stretch_IKBone1_Distance_ratio_static = stretch_IKBone1_static / stretch_IKBoneDistance_static
        stretch_IKBone2_Distance_ratio_static = stretch_IKBone2_static / stretch_IKBoneDistance_static
        stretch_overallDistance_static = cmds.getAttr(overall_Dist_Name)
        # stretch_amount_difference = " + overall_Dist_Name + " - " + IKBone1_Dist_Name + " + " + IKBone2_Dist_Name + "

        
        #Add attribute to the main control curve which will allow the arm to be stretched further than normally possible
        cmds.addAttr(nurbsCurveVal, ln = "manually_stretch_arm",  at = 'float', min = -50, max = 100, dv = 0, k = 1)
        nurbsCurveStretchAttr = nurbsCurveVal + ".manually_stretch_arm"
        

        newIKChain0 = newIKChain[0]
        newIKChain1 = newIKChain[1]
        newFKChain0 = newFKChain[0]
        newFKChain1 = newFKChain[1]
        originalChainName0 = originalChainName[0]
        originalChainName1 = originalChainName[1]

        # print locals()
        expression_stretch_values = '''
            if ( {nurbsStretchAttr} && {overall_Dist_Name} >= {stretch_IKBoneDistance_static} ){{
                {newIKChain0}.sy =        1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr} /10 );
                {newIKChain1}.sy =        1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr} /10 );
                {newFKChain0}.sy =        1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr} /10 );
                {newFKChain1}.sy =        1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr} /10 );
                {originalChainName0}.sy = 1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr} /10 );
                {originalChainName1}.sy = 1 + ( ( {overall_Dist_Name} - {stretch_IKBoneDistance_static} ) / {stretch_IKBoneDistance_static} + {nurbsCurveStretchAttr} /10 );
            }}
            else {{
                {newIKChain0}.sy = 1+ {nurbsCurveStretchAttr} /10;
                {newIKChain1}.sy = 1+ {nurbsCurveStretchAttr} /10;
                {newFKChain0}.sy = 1+ {nurbsCurveStretchAttr} /10;
                {newFKChain1}.sy = 1+ {nurbsCurveStretchAttr} /10;
                {originalChainName0}.sy = 1+ {nurbsCurveStretchAttr} /10;
                {originalChainName1}.sy = 1+ {nurbsCurveStretchAttr} /10;
            }}
        '''.format(**locals())

        cmds.expression(s=expression_stretch_values, n=("stretchyArm_expression"), ae=0, uc=all )


        
        #Organizing
        cmds.parent(stretch_firstLocator, overallGroup)
        cmds.parent(stretch_secondLocator, overallGroup)
        cmds.parent(stretch_thirdLocator, overallGroup)
        
        cmds.setAttr(stretch_firstLocator[0] + ".visibility", 0)
        cmds.setAttr(stretch_secondLocator[0] + ".visibility", 0)
        cmds.setAttr(stretch_thirdLocator[0] + ".visibility", 0)

    #putting things into a group for cleaning purposes
    cmds.parent(originalChainName[0], overallGroup)
    cmds.parent(newIKChain[0], overallGroup)
    cmds.parent(newFKChain[0], overallGroup)
    
    if(bendyActivation):
    
        
        #creating the bendy aspect of the rig if required
        cmds.select(newSplineChain)
        
        counter = 0
        iterate = 1
        while (iterate == 1):
    
            numberOfSpans = 4
            
            mmSelectedInScene = cmds.ls(sl = 1)
                    
            selectedJointChain = ""
            iMax = len(mmSelectedInScene)-1
            
            i = 0
            while (i<=iMax):
                selectedJointChain = cmds.ls(mmSelectedInScene[i], dag = 1)
                i += 1
            
            #set parent and child for first chain
            parentJointNameOrig = selectedJointChain[0]
            childJointName = selectedJointChain[1]
    
            
            #was trying to run this multiple times on the same chain, but doesn't work
            storageVariableParent = None
            #store that it needs to be run again if the chain continues
            if(len(selectedJointChain) >= 3):
                storageVariableParent = childJointName
            
            #create an icon to be used later
            boxIconName = mmOF.createCube()
            
            #create a distance node to find the space between joints
            distanceShapeNodeName = cmds.shadingNode("distanceBetween", asUtility = 1, n = parentJointNameOrig + "_distanceNode#")
            
            #create locators
            firstLocator = cmds.spaceLocator( p = [0,0,0] )
            secondLocator = cmds.spaceLocator( p = [1,1,1] )
            
            #attach locators to distance node
            cmds.connectAttr(firstLocator[0] + ".translate", distanceShapeNodeName + ".point1")
            cmds.connectAttr(secondLocator[0] + ".translate", distanceShapeNodeName + ".point2")
            
            #move locators to selected joint and its first child
            cmds.parentConstraint(parentJointNameOrig, firstLocator, mo = 0)
            cmds.parentConstraint(childJointName, secondLocator, mo = 0)
            
            #find the distance needed between each new joint
            totalDistance = cmds.getAttr(distanceShapeNodeName + ".distance")
            addedJointDistance = totalDistance/numDivisions
                    
            distanceTransNodeName = cmds.listRelatives(distanceShapeNodeName, p = 1)
            
            #get rid of distance node and locators
            cmds.delete(distanceTransNodeName)
            cmds.delete(firstLocator)
            cmds.delete(secondLocator)
            
            #set up the naming convention for newly created joints
            parentJointName = parentJointNameOrig
            jointName = parentJointName + "_spline#"
            
            #need to find out if y is pos or neg down the chain
            #to find out if y is negative, just find the Y attr of the middle joint and determine if its greater or less than 0
            isYNegative = cmds.getAttr(childJointName + ".ty")
            
            if(isYNegative < 0):
                ifNeedsAFlipValue = -1
            else:
                ifNeedsAFlipValue = 1
            
            i = 0
            #insert all the joints needed at the distance found
            #name as the iterations go
            while (i<=numDivisions-2):
                addedJoint = cmds.insertJoint(parentJointName)
                newJointName = cmds.rename(addedJoint, jointName)
                
                if(i == 0):
                    storedJoint = newJointName
                
                
                if(storageVariableParent and i == (numDivisions-2)):
                    anotherStoredJoint = newJointName

                
                cmds.joint(newJointName, e = 1, co = 1, r = 1, zso = 1, p = (0, (addedJointDistance*ifNeedsAFlipValue), 0))
                
                #set new parent joint
                parentJointName = newJointName
                
                i += 1
                
            if(storageVariableParent):
                    
                    
                #create Spline piece
                splineSolverNameList = cmds.ikHandle( sol = "ikSplineSolver", pcv = 0, sj = parentJointNameOrig, ee = anotherStoredJoint, ns = (numberOfSpans - 2), n = newSplineChain[0] + "_ikHandle#")
        
            else:
                #create Spline piece
                splineSolverNameList = cmds.ikHandle( sol = "ikSplineSolver", pcv = 0, sj = parentJointNameOrig, ee = childJointName, ns = (numberOfSpans - 2), n = newSplineChain[0] + "_ikHandle#")
                
                    
            
            #find name of curve used by spline
            splineSolverName = splineSolverNameList[0]
            splineCurveName = splineSolverNameList[2]
    
            splineCurveName = cmds.rename(splineCurveName, parentJointNameOrig + "_ikSplineCurve#")
            
            cmds.parent(splineSolverName, splineGroup, r = 1)

            cmds.parent(splineCurveName, splineGroup, r = 1)
            
            #Need to find the default length of the curve
            defaultArcLength = cmds.arclen(splineCurveName)
            
            #Need to create a node to find the changing value of the curve
            infoOfCurve = cmds.shadingNode("curveInfo", asUtility = 1, n = parentJointNameOrig + "_curveInfo#")
            cmds.connectAttr(splineCurveName + ".worldSpace[0]", infoOfCurve + ".inputCurve", f = 1)
            
            changingArcLength = cmds.getAttr(infoOfCurve + ".arcLength")
            
            #Need to create a method of driving the joints into a stretchy rig
            stretchyCondition = cmds.shadingNode("condition", asUtility = 1, n = (splineCurveName + "_stretchyCond#"))
            
            #set values for 1 and 0
            cmds.setAttr( stretchyCondition + ".colorIfTrueR", 1 )
            cmds.setAttr( stretchyCondition + ".colorIfFalseR", 0 )
    
            cmds.setAttr( stretchyCondition + ".operation", 3 )
            cmds.connectAttr( (infoOfCurve + ".arcLength"), stretchyCondition + ".firstTerm", f = 1)
            cmds.setAttr( stretchyCondition + ".secondTerm", (defaultArcLength) )
            
            #cmds.connectAttr( stretchyCondition + ".nodeState", f = 1)
    
            #create a multDiv node to use
            multDivSplineNode = cmds.shadingNode("multiplyDivide", asUtility = 1, n = parentJointNameOrig + "_multDiv#")
    
            cmds.connectAttr( (infoOfCurve + ".arcLength"), multDivSplineNode + ".input1X", f = 1)
            cmds.setAttr( multDivSplineNode + ".input2X", (defaultArcLength) )
            cmds.setAttr( multDivSplineNode  + ".operation", 2)
            
            #create a multDiv node to use
            multDivOnOffNode = cmds.shadingNode("multiplyDivide", asUtility = 1, n = parentJointNameOrig + "_multDiv#")
    
            cmds.connectAttr( (multDivSplineNode + ".outputX"), multDivOnOffNode + ".input1X", f = 1)
            cmds.connectAttr( (stretchyCondition + ".outColorR"), multDivOnOffNode + ".input2X", f = 1)
            
            #use final value, need to plug in to scale Y
            #insert the final value into the scale of all the new joints
            i = 0
            jointToWorkOn = storedJoint
            
            while (i<=numDivisions-2):
                #still need to make a similar attachment to an on off icon
                if (i == 0):
                    selectedJointName = jointToWorkOn
                else:
                    selectedJointName = jointToWorkOn[0]
                
                if(stretchyActivation):
                            
                    expression_stretch_values = "if(" + multDivOnOffNode + ".outputX >= 1){ " + selectedJointName + ".scaleY = " + multDivOnOffNode + ".outputX;} else{ " + selectedJointName + ".scaleY = 1+ " + nurbsCurveStretchAttr + "/10;}"
                
                else:
                    expression_stretch_values = "if(" + multDivOnOffNode + ".outputX >= 1){ " + selectedJointName + ".scaleY = " + multDivOnOffNode + ".outputX;} else{ " + selectedJointName + ".scaleY = 1;}"

                    
                    #cmds.connectAttr((multDivOnOffNode + ".outputX"), (selectedJointName + ".scaleY"), f = 1)
                    cmds.expression(s=expression_stretch_values, n=(selectedJointName + "_expression"), ae=0, uc=all )
    
                    #pickwalk to the child and store the name as the next working name
                    cmds.select(selectedJointName)
                    nextJointToWorkOn = cmds.listRelatives(c = 1)
                    
                    #set new parent joint
                    jointToWorkOn = nextJointToWorkOn
                    
                    i += 1
    
            #create an empty group to put clusters into
            clusterGroupNode = cmds.group(em = 1, n = parentJointNameOrig + "_clusterNode_Group#")
            
            #create an empty group to put middle controls into
            controlGroupNode = cmds.group(em = 1, n = parentJointNameOrig + "_controlNode_Group#")
            
            #create cluster nodes and apply them to the newly created curve's control points
            i = 0
            while (i <= numberOfSpans):
                clusterIterName = splineCurveName + ".cv[" + str(i) + "]"
                cmds.select(clusterIterName, r = 1)
                cmds.CreateCluster()
                
                clusterIterName = cmds.rename((splineCurveName + "_cluster#"))
                

                #put the clusters under parent cluster group
                cmds.parent(clusterIterName,clusterGroupNode)
                
                #grab first control and store its name
                if (i == 0):

                    if (counter == 0):
                        #top joint constraint
                        cmds.pointConstraint(originalChainName[0], clusterIterName)
                
                    if (counter == 1):
                        #top joint constraint
                        cmds.pointConstraint(originalChainName[1], clusterIterName)
                        
                    topIconName = clusterIterName
                
                #grab last control and store its name
                if (i == numberOfSpans):
                            
                    if (counter == 0):
                        #top joint constraint
                        cmds.pointConstraint(originalChainName[1], clusterIterName)
                        
                    if (counter == 1):
                        #end joint
                        cmds.pointConstraint(originalChainName[2], clusterIterName)
                        
                    bottomIconName = clusterIterName

                #grab middle controls and group them together
                if (i > 0 and i < numberOfSpans):
                                    
                    #Create a new icon from the original
                    newBoxIconName = cmds.duplicate(boxIconName)
                    newBoxIconName = cmds.rename(newBoxIconName, parentJointNameOrig + "_spline_icon#")
                    
                    cmds.select(newBoxIconName, r = 1)
                    cmds.select(clusterIterName, add = 1)
                    
                    #Use pad and align function to place the icon, store name for parenting
                    outerPadName = padAndAlign(1)[2]
                    
                    
                    
                    cmds.parent(outerPadName,controlGroupNode)
                            
                if (i == abs(numberOfSpans/2)):
                                    
                    storedItemName = clusterIterName
                i += 1

            #group the pad and name it
            controlGroupNodePad = cmds.group(controlGroupNode, name = (controlGroupNode + "_pad#"))
            controlGroupNodePadTwo = cmds.group(controlGroupNodePad, name = (controlGroupNodePad + "_again#"))
            cmds.xform(cp=1)
            
            #take second group and parentConstraint("name", mo = 0)
            nameOfConstraint = cmds.parentConstraint(storedItemName, controlGroupNodePad, mo = 0)
            
            #delete the parent contstraint
            cmds.delete(nameOfConstraint)
    
            cmds.select(controlGroupNode, r = 1)
            cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)
    
            cmds.xform(cp=1)
            
            #Create a new icon
            newBoxIconName = mmOF.createMoveAll()
            
            cmds.select(newBoxIconName, r = 1)
            
                    
            
            cmds.scale(.25, .25, .25, r = 1, scaleXYZ = 1)
            cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)
            
            cmds.select(controlGroupNodePad, add = 1)
            
            finalBoxParentsPad = padAndAlign(4)[2]
            
            andANewBoxName = cmds.ls(sl = 1)
            
            andTheFinalBoxName = cmds.rename(andANewBoxName[0], parentJointNameOrig + "_spline_middle_icon")
            
            #need final box to follow the arm as it moves around with other controls
            #so, going to use an expression for the placement, and an aim constraint for the orientation
            firstBoxParent = cmds.listRelatives(p = 1)
            
            #control icon's pad translations = (top icon's translates + bottom icon's translates)/2
            
            expression_stretch_values = firstBoxParent[0] + ".tx = (" + topIconName + ".tx + " + bottomIconName + ".tx)/2; " + firstBoxParent[0] + ".ty = (" + topIconName + ".ty + " + bottomIconName + ".ty)/2; " + firstBoxParent[0] + ".tz = (" + topIconName + ".tz + " + bottomIconName + ".tz)/2;"
            
            cmds.expression(s=expression_stretch_values, n=(firstBoxParent[0] + "_spline_holder"), ae=0, uc=all )
            
            addedBoxParent = cmds.group( andTheFinalBoxName , n = parentJointNameOrig + "_spline_middle_icon_extraPad")
            cmds.xform( cp = 1 )
            
            #parent constraint pad toward the control arm joint up above it
            #cmds.select(firstBoxParent)
            
            #cmds.orientConstraint( originalChainName[counter], addedBoxParent,  mo = 1 )
            #secondBoxParent = cmds.listRelatives(p = 1)
            #cmds.parentConstraint( originalChainName[counter], secondBoxParent[0],  mo = 1 )
            cmds.orientConstraint( originalChainName[counter], addedBoxParent,  mo = 1 )
            
            cmds.addAttr(andTheFinalBoxName, ln = "hide_extra_icons", at ="enum", en = "on:off:", dv = 0, k=1)
            
            cmds.connectAttr((andTheFinalBoxName + ".hide_extra_icons"), controlGroupNodePad + ".visibility")
            
            cmds.addAttr(andTheFinalBoxName, ln = "roundness", at ="float", min = 0, max = 10, dv = 1, k=1)
    
            cmds.connectAttr((andTheFinalBoxName + ".roundness"), controlGroupNodePad + ".scaleX")
            cmds.connectAttr((andTheFinalBoxName + ".roundness"), controlGroupNodePad + ".scaleY")
            cmds.connectAttr((andTheFinalBoxName + ".roundness"), controlGroupNodePad + ".scaleZ")
            
            #Don't want this to apply if there is no stretchy arm
            if(stretchyActivation):
                
                #Scale the cluster control boxes so that the controls don't overlap when manually scaling down
                expression_stretch_values = "if ( " + stretch_distanceShapeNodeName_bone1 + ".distance >= " + str(abs(stretch_overallDistance_static)) + " && " + nurbsStretchAttr + ") { " + controlGroupNodePadTwo + ".scaleZ = ( " + stretch_distanceShapeNodeName_bone1 + ".distance / " + str(abs(stretch_overallDistance_static)) + " + " + nurbsCurveStretchAttr + "/10); " + controlGroupNodePadTwo + ".scaleZ = ( " + stretch_distanceShapeNodeName_bone1 + ".distance / " + str(abs(stretch_overallDistance_static)) + " + " + nurbsCurveStretchAttr + "/10);} else { " + controlGroupNodePadTwo + ".scaleZ = 1+ " + nurbsCurveStretchAttr + "/10; " + controlGroupNodePadTwo + ".scaleZ = 1+ " + nurbsCurveStretchAttr + "/10;}"
                cmds.expression(s=expression_stretch_values, n=("spline_strechyArmHolder_expressionZ#"), ae=0, uc=all )
                
                expression_stretch_values = "if ( " + stretch_distanceShapeNodeName_bone1 + ".distance >= " + str(abs(stretch_overallDistance_static)) + " && " + nurbsStretchAttr + ") { " + controlGroupNodePadTwo + ".scaleX = ( " + stretch_distanceShapeNodeName_bone1 + ".distance / " + str(abs(stretch_overallDistance_static)) + " + " + nurbsCurveStretchAttr + "/10); " + controlGroupNodePadTwo + ".scaleX = ( " + stretch_distanceShapeNodeName_bone1 + ".distance / " + str(abs(stretch_overallDistance_static)) + " + " + nurbsCurveStretchAttr + "/10);} else { " + controlGroupNodePadTwo + ".scaleX = 1+ " + nurbsCurveStretchAttr + "/10; " + controlGroupNodePadTwo + ".scaleX = 1+ " + nurbsCurveStretchAttr + "/10;}"
                cmds.expression(s=expression_stretch_values, n=("spline_strechyArmHolder_expressionX#"), ae=0, uc=all )

                expression_stretch_values = "if ( " + stretch_distanceShapeNodeName_bone1 + ".distance >= " + str(abs(stretch_overallDistance_static)) + " && " + nurbsStretchAttr + ") { " + controlGroupNodePadTwo + ".scaleY = ( " + stretch_distanceShapeNodeName_bone1 + ".distance / " + str(abs(stretch_overallDistance_static)) + " + " + nurbsCurveStretchAttr + "/10); " + controlGroupNodePadTwo + ".scaleY = ( " + stretch_distanceShapeNodeName_bone1 + ".distance / " + str(abs(stretch_overallDistance_static)) + " + " + nurbsCurveStretchAttr + "/10);} else { " + controlGroupNodePadTwo + ".scaleY = 1+ " + nurbsCurveStretchAttr + "/10; " + controlGroupNodePadTwo + ".scaleY = 1+ " + nurbsCurveStretchAttr + "/10;}"
                cmds.expression(s=expression_stretch_values, n=("spline_strechyArmHolder_expressionY#"), ae=0, uc=all )

            #hide cluster nodes
            cmds.setAttr(clusterGroupNode + ".visibility", 0)
            
            #delete the original box icon
            cmds.delete(boxIconName)
                    
            
            #put all spline groups into the overall spline group
            #cmds.parent(clusterGroupNode, splineGroup, r = 1)
            #cmds.parent(controlGroupNode, splineGroup, r = 1)
            cmds.parent(finalBoxParentsPad, splineGroup, r = 1)
            
            if (storageVariableParent):
                    
                    
                #need to delete this connection, must find them first
                '''
                spline_joint13_spline29.scale |ik_fk_switch_spline_group1|spline_joint14.inverseScale
                '''
                
                    
                cmds.select(storageVariableParent)
                iterate = 1
                counter += 1
            else:
                iterate = 0

        
        cmds.parent( parentJointNameOrig, w = 1 )
        #cmds.disconnectAttr( anotherStoredJoint + ".scale", storageVariableParent + ".inverseScale")
        
        cmds.parent( newSplineChain, splineGroup, r = 1 )
        cmds.parent( parentJointNameOrig, splineGroup)

        
        cmds.select(ikIconName, r = 1)

    cmds.select(ikIconName)

"""

'''
Function: Uses an icon to create a controller for an object and parents the object to the icon with 2 pad groups
'''
def padAndAlign(mmConstraintType = 4, mmShouldRenameIcon = True, *args):
    mmSelectedInScene = cmds.ls(sl=1)
    nurbsCurveVal = mmSelectedInScene[0]
    jointSystemChain = cmds.ls(mmSelectedInScene[1], dag = 1)

    if(mmConstraintType == False ):
            
        mmConstraintType = cmds.radioButtonGrp("mmPadAndAlignRadioBoxes", q = 1, sl = 1)

    if(mmSelectedInScene):
        iconName = jointSystemChain[0]
        iconName += "_Control"
        
        #?  Removed this duplication (and later delete of the original), but am sure some functions (like fingers/hands) rely on it.
        #?      Was a stupid thing to do - duplication should be done in the finger/hands function, not here.  Need to fix there.
        # #create duplicates of the original icon
        # nurbsCurveValDup = cmds.duplicate(nurbsCurveVal)
        
        # #rename icon
        # iconRenamed = cmds.rename(nurbsCurveValDup, iconName)
        
        #rename icon
        if (mmShouldRenameIcon):
            iconRenamed = cmds.rename(nurbsCurveVal, iconName)
        else:
            iconRenamed = nurbsCurveVal
        
        #group it and name it
        iconGroupOne = cmds.group(iconRenamed, name = (iconRenamed + "_pad#"))
        # cmds.xform( cp = 1 )

        #group the pad and name it
        iconGroupTwo = cmds.group(iconGroupOne, name = (iconRenamed + "_pad#"))
        # cmds.xform( cp = 1 )
        
        #If we are making a new icon, then move it into position
        if ( mmShouldRenameIcon ):
            mmTempParentConst = cmds.parentConstraint(jointSystemChain[0], iconGroupTwo, mo = 0)
            #delete the parent contstraint
            cmds.delete(mmTempParentConst)
                
            #freeze transforms on the icon
            cmds.select(iconRenamed, r = 1)
            cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)
            
        #'Point', 'Aim', 'Orient', 'Parent'
        #decide which kind of constraint to do
        
        if (mmConstraintType == 1):
            #take icon and point contstrain the joint to it
            cmds.pointConstraint(iconRenamed, jointSystemChain[0], mo = 1)
    
        if (mmConstraintType == 2):
            #take icon and aim contstrain the joint to it
            cmds.aimConstraint(iconRenamed, jointSystemChain[0], mo = 1)
    
        if (mmConstraintType == 3):
            #take icon and orient contstrain the joint to it
            cmds.orientConstraint(iconRenamed, jointSystemChain[0], mo = 1)
    
        if (mmConstraintType == 4):
            #take icon and parent contstrain the joint to it
            cmds.parentConstraint(iconRenamed, jointSystemChain[0], mo = 1)
    
        #delete the original icon
        #cmds.delete(nurbsCurveVal)
        cmds.select(iconRenamed)
        
        #?  why am i doing this line?
        # cmds.xform(cp=1)

    else:
        print "Invalid Selection"

    return [iconRenamed, iconGroupOne, iconGroupTwo]

'''
#Function: Creates Attributes for a Hand icon & connect them to the fingers
#?  This function may be broken because padAndAlign no longer duplicates the control passed into it.
'''
def handCreator( boolIconsCreated = False, boolCurl = False, boolSpread = False, boolTwist = False, mmRotOrderFinger = "ZXY", mmRotOrderThumb = "ZXY", *args):
    
    mmSelectedInScene = cmds.ls(sl=1)
    if (boolCurl == False and boolSpread == False and boolTwist == False):
        boolCurl = cmds.checkBoxGrp("handSystemChkBoxes", q = 1, v1 = 1)
        boolSpread = cmds.checkBoxGrp("handSystemChkBoxes", q = 1, v2 = 1)
        boolTwist = cmds.checkBoxGrp("handSystemChkBoxes", q = 1, v3 = 1)

    mmCurlRotValueFinger = mmRotOrderFinger[0]
    mmSpreadRotValueFinger = mmRotOrderFinger[1]
    mmTwistRotValueFinger = mmRotOrderFinger[2]
    
    mmCurlRotValueThumb = mmRotOrderThumb[0]
    mmSpreadRotValueThumb = mmRotOrderThumb[1]
    mmTwistRotValueThumb = mmRotOrderThumb[2]

    mmControlsMade = []
    
    
    if(mmSelectedInScene):
        
        #labeling and connecting the hand
        controlCurve = mmSelectedInScene[0]
        
        #Creates an empty list to store names into
        listOfJointChains = [""]
        
        counter = 1
        counterMax = len(mmSelectedInScene)
        
        #Stores names of different joint chains into the list which was just created
        while (counter <= (counterMax-1)):
            jointChainToOperateOn = mmSelectedInScene[counter]
            listOfJointChains.append(jointChainToOperateOn)
            counter += 1

        #print "listOfJointChains", listOfJointChains
                
        counterOut = 1
        counterOutMax = len(listOfJointChains)
        
        #create a vis toggle attr to hide finger ctrls
        cmds.addAttr(controlCurve, ln ="extra_detail_vis", at ="enum", en = "off:on:" ,dv=1, k=1)
        
        if(boolCurl):
            #Create Attributes for each finger selected
            cmds.addAttr(controlCurve, ln = "curl", at ="double", min= -360, max =360, dv=0, k=1)
            cmds.setAttr((controlCurve + ".curl"), l=1)
            
            
            i=1
            while (i<=(counterOutMax-1)):
                    
                cmds.addAttr(controlCurve, ln= (listOfJointChains[i] + "_curl"), at ="double", min= -360, max =360, dv=0, k=1)
                i+=1
                
            #Create Attributes for each finger selected
            cmds.addAttr(controlCurve, ln = "curl_multiplier", at ="double", min= -360, max =360, dv=0, k=1)
            cmds.setAttr((controlCurve + ".curl_multiplier"), l=1)
            
            i=1
            while (i<=(counterOutMax-1)):
                    
                cmds.addAttr(controlCurve, ln= (listOfJointChains[i] + "_curl_multiplier"), at ="double", min= -10, max =10, dv=0, k=1)
                i+=1

        if(boolSpread):      
            cmds.addAttr(controlCurve, ln ="spread"  ,at ="double"  ,min =-360 ,max =360 ,dv=0, k=1)
            cmds.setAttr((controlCurve + ".spread"), l=1)
            
            i=1
            while (i<=(counterOutMax-1)):
                cmds.addAttr(controlCurve, ln= (listOfJointChains[i] + "_spread"), at ="double", min= -360, max =360, dv=0, k=1)
                i+=1
                    
            cmds.addAttr(controlCurve, ln ="spread_multiplier"  ,at ="double"  ,min =-360 ,max =360 ,dv=0, k=1)
            cmds.setAttr((controlCurve + ".spread_multiplier"), l=1)
                    
            i=1
            while (i<=(counterOutMax-1)):
                cmds.addAttr(controlCurve, ln= (listOfJointChains[i] + "_spread_multiplier"), at ="double", min= -10, max =10, dv=0, k=1)
                i+=1

        if(boolTwist):
            cmds.addAttr(controlCurve, ln ="twist"  ,at ="double"  ,min =-360 ,max =360 ,dv=0, k=1)
            cmds.setAttr((controlCurve + ".twist"), l=1)
            
            i=1
            while (i<=(counterOutMax-1)):
                cmds.addAttr(controlCurve, ln= (listOfJointChains[i] + "_twist"), at ="double", min= -360, max =360, dv=0, k=1)
                i+=1
                    
            cmds.addAttr(controlCurve, ln ="twist_multiplier"  ,at ="double"  ,min =-360 ,max =360 ,dv=0, k=1)
            cmds.setAttr((controlCurve + ".twist_multiplier"), l=1)
                    
            
            i=1
            while (i<=(counterOutMax-1)):
                cmds.addAttr(controlCurve, ln= (listOfJointChains[i] + "_twist_multiplier"), at ="double", min= -10, max =10, dv=0, k=1)
                i+=1

        
        cmds.addAttr(controlCurve, ln ="other"  ,at ="double"  ,min= -10 ,max =10 ,dv=0, k=1)
        cmds.setAttr((controlCurve + ".other"), l=1)
        cmds.addAttr(controlCurve, ln= "fist"  ,at ="double"  ,min =0,max =10 ,dv=0, k=1)
        
        #create an empty group to put all pads and icons into
        overallSystemGroup = cmds.group(em = 1, name = "createdHandSystem_Group#")
        
        #creates an original icon
        originalIcon = mmOF.createPin()
        
        #print "originalIcon: ", originalIcon

        #labeling and connecting each finger
        #duplicates original icon and places it on each joint that is needed
        while ( counterOut <= (counterOutMax-1) ):
            #print "listOfJointChains", listOfJointChains
            counter = 0
            currentJointChain = cmds.ls(listOfJointChains[counterOut], dag = 1, type = "transform")

            #print "At Beginning listOfJointChains[counterOut]: ", listOfJointChains[counterOut]

            #print "At Beginning currentJointChain: ", currentJointChain

            #Need to find out if there is a constraint name here, and if there is, get rid of it.
            mmPreCounter = 0
            mmPreCounterMax = len(currentJointChain)
            
            while ( mmPreCounter < mmPreCounterMax ):

                #print "mmPreCounter: ", mmPreCounter
                #print "mmPreCounterMax: ", mmPreCounterMax
                #print "currentJointChain: ", currentJointChain

                
                mmTempRelativeSplit = currentJointChain[mmPreCounter].split("_")

                mmTempLen = len(mmTempRelativeSplit)

                if ( mmTempRelativeSplit[mmTempLen - 1] == "parentConstraint1" or mmTempRelativeSplit[mmTempLen - 1] == "orientConstraint1" or mmTempRelativeSplit[mmTempLen - 1] == "pointConstraint1" or mmTempRelativeSplit[mmTempLen - 1] == "aimConstraint1"):
                    #Then don't include it.
                    #print "REMOVING currentJointChain[mmPreCounter]: ", currentJointChain[mmPreCounter] 
                    currentJointChain.remove( currentJointChain[mmPreCounter] )
                    mmPreCounter -= 1
                    mmPreCounterMax -= 1

                mmPreCounter += 1

            #print "At End currentJointChain: ", currentJointChain

            counterMax = len(currentJointChain)
                    
            createdCube = mmOF.createCube()
            
            cmds.select(createdCube)
            
            masterControlIcon = cmds.rename((currentJointChain[0] + "_Master_Control"))
            cmds.select(currentJointChain[0], add = 1)
            
            #add new control to "mmControlsMade"
            mmControlsMade.append( masterControlIcon )

            #group it and name it
            MCiconGroupOne = cmds.group(masterControlIcon, name = (masterControlIcon + "_pad#"))
            
            #group the pad and name it
            MCiconGroupTwo = cmds.group(MCiconGroupOne, name = (masterControlIcon + "_pad#"))
            
            #take second group and parentConstraint("name", mo = 1)
            nameOfConstraint = cmds.pointConstraint(currentJointChain[0], MCiconGroupTwo, mo = 0)
            
            #delete the parent contstraint
            cmds.delete(nameOfConstraint)
                    
            cmds.parent(MCiconGroupTwo, overallSystemGroup)
            
            #Set up a Vis Toggle for fingers on master controls, and master switch on main icon
            cmds.addAttr(masterControlIcon, ln ="extra_detail_vis", at ="enum", en = "off:on:", dv=1, k=1)
            
            
            #Prep names for expressions later
            multiplierCurlName = controlCurve + "." + listOfJointChains[counterOut] + "_curl_multiplier"
            multiplierSpreadName = controlCurve + "." + listOfJointChains[counterOut] + "_spread_multiplier"
            multiplierTwistName = controlCurve + "." + listOfJointChains[counterOut] + "_twist_multiplier"
            
            multiplierCounterMultiplier = 2
            multiplierValSmall = 0
            multiplierValLarge = counterMax*multiplierCounterMultiplier

            mmThumbBool = False
            
            #labeling and connecting each joint
            while (counter <= (counterMax-1)):
                iconName = currentJointChain[counter] + "_icon"
                
                if ( currentJointChain[counter][0:10] == "rightThumb" or currentJointChain[counter][0:9] == "leftThumb" ):
                    mmThumbBool = True

                #Need to check if the controls are already created - it will be passed in that they are
                if ( boolIconsCreated == False ):

                    #create duplicates of the original icon
                    #print "originalIcon: ", originalIcon
                    nurbsCurveValDup = cmds.duplicate(originalIcon)

                    cmds.select( nurbsCurveValDup )

                    if ( mmThumbBool ):

                        if ( mmCurlRotValueThumb == "X"):
                            cmds.rotate(0,0,0)
                        elif ( mmCurlRotValueThumb == "Y"):
                            cmds.rotate(0,0,90)
                        elif ( mmCurlRotValueThumb == "Z"):
                            cmds.rotate(0,0,0)

                    else:

                        if ( mmCurlRotValueFinger == "X"):
                            cmds.rotate(0,0,0)
                        elif ( mmCurlRotValueFinger == "Y"):
                            cmds.rotate(0,0,90)
                        elif ( mmCurlRotValueFinger == "Z"):
                            cmds.rotate(0,0,0)

                    cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

                    #rename icon
                    iconRenamed = cmds.rename(nurbsCurveValDup, iconName)

                else:
                    #else, use what exists already - but how to find this appendage's control?
                    #print "currentJointChain[counter]", currentJointChain[counter]
                    
                    iconRenamed = currentJointChain[counter].split("_")[0] + "_Control"

                    cmds.select( iconRenamed )

                    #need to delete the parent constraint holding the mesh in place with this control
                    cmds.select( currentJointChain[counter] )
                    mmTempRelatives = cmds.listRelatives( type = "transform" )

                    #print "mmTempRelatives", mmTempRelatives
                    for mmTempRelative in mmTempRelatives:
                        mmChecker = mmTempRelative.split("_")

                        mmLenChecker = len(mmChecker)

                        if ( mmChecker[mmLenChecker-1][0:16] == "parentConstraint" ):
                            cmds.delete(mmTempRelative)

                    #re-grab the current controller
                    cmds.select( iconRenamed )


                    #Unparent so the control can be placed at the origin
                    cmds.parent( w = 1 )

                    #Set to world trans
                    mmGWT.main()

                    #Move control to the origin
                    cmds.xform( t = (0,0,0) )

                    #Force update of viewport, and then pause for .5 seconds
                    # cmds.refresh()
                    # time.sleep( 0.15 )
                
                #add new control to "mmControlsMade"
                mmControlsMade.append( iconRenamed )

                #group it and name it
                iconGroupOne = cmds.group(em = 1, name = (iconRenamed + "_pad"))

                cmds.parent( iconRenamed, iconGroupOne )
                
                #group the pad and name it
                iconGroupTwo = cmds.group(em = 1, name = (iconRenamed + "_pad1"))
                
                cmds.parent( iconGroupOne, iconGroupTwo )
                
                #group the pad and name it
                iconGroupThree = cmds.group(em = 1, name = (iconRenamed + "_pad2"))
                
                cmds.parent( iconGroupTwo, iconGroupThree )

                #Put the groups and icon in place with a parent constraint
                nameOfConstraint = cmds.pointConstraint(currentJointChain[counter], iconGroupThree, mo = 0)

                # print iconGroupOne, ".xform: ", cmds.xform(iconGroupOne, q = 1, t = 1, ws = 1 )
                # print iconGroupTwo, ".xform: ", cmds.xform(iconGroupTwo, q = 1, t = 1, ws = 1 )
                # print iconGroupThree, ".xform: ", cmds.xform(iconGroupThree, q = 1, t = 1, ws = 1 )
                
                #cmds.refresh()
                #time.sleep( 0.15 )

                #delete the parent contstraint
                cmds.delete(nameOfConstraint)
                
                cmds.select( iconGroupThree )
                
                cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)

                if (counter == 0):
                    cmds.parent(iconGroupThree, masterControlIcon)
                    visTogGroupName = iconGroupThree


                # print "mmTempRelatives", mmTempRelatives
                # print "mmTempRelative", mmTempRelative

                # print "iconRenamed", iconRenamed
                #print "currentJointChain[counter]", currentJointChain[counter]

                #take icon and orient constrain the joint to it
                cmds.parentConstraint(iconRenamed, currentJointChain[counter], mo = 1)

                #create needed multiply Divide nodes
                multDivNodeName = cmds.shadingNode("multiplyDivide", au = 1, n = (currentJointChain[counter] + "_multDivNode#"))
                multDivNodeNameTwo = cmds.shadingNode("multiplyDivide", au = 1, n = (currentJointChain[counter] + "_multDivNode#"))
                #multDivList.append(multDivNodeName)
                #multDivList.append(multDivNodeNameTwo)
                
                #Check to see if this is a thumb - because we have weird situations where we want to make them rotate differently
                #print "currentJointChain[counter][0:8]", currentJointChain[counter][0:8]
                if( mmThumbBool ):
                    if(boolCurl):
                        
                        #Connects the rotations of the master control to the input of the multiply divide node and output to a pad.
                        cmds.connectAttr((masterControlIcon + ".rotate" + mmCurlRotValueThumb), (multDivNodeName + ".input1" + mmCurlRotValueThumb ))
                        cmds.connectAttr((multDivNodeName + ".o" + mmCurlRotValueThumb.lower() ), (iconGroupOne + ".rotate" + mmCurlRotValueThumb )) 
                        
                        #Connects the rotations of the control icon's attribute to the input of another multiply divide node and output to a pad.
                        cmds.connectAttr((controlCurve + "." + currentJointChain[0] + "_curl"), (multDivNodeNameTwo + ".input1" + mmCurlRotValueThumb ))
                        cmds.connectAttr((multDivNodeNameTwo + ".o" + mmCurlRotValueThumb.lower() ), (iconGroupTwo + ".rotate" + mmCurlRotValueThumb ))
                        
                    if(boolSpread):
                        
                        #Connects the rotations of the master control to the input of the multiply divide node and output to a pad.
                        cmds.connectAttr((masterControlIcon + ".rotate" + mmSpreadRotValueThumb ), (multDivNodeName + ".input1" + mmSpreadRotValueThumb ))
                        cmds.connectAttr((multDivNodeName + ".o" + mmSpreadRotValueThumb.lower() ), (iconGroupOne + ".rotate" + mmSpreadRotValueThumb )) 
                                
                        #Connects the rotations of the control icon's attribute to the input of another multiply divide node and output to a pad.
                        cmds.connectAttr((controlCurve + "." + currentJointChain[0] + "_spread"), (multDivNodeNameTwo + ".input1" + mmSpreadRotValueThumb ))
                        cmds.connectAttr((multDivNodeNameTwo + ".o" + mmSpreadRotValueThumb.lower() ), (iconGroupTwo + ".rotate" + mmSpreadRotValueThumb ))
                                
                    if(boolTwist):
                        
                        #Connects the rotations of the master control to the input of the multiply divide node and output to a pad.
                        cmds.connectAttr((masterControlIcon + ".rotate" + mmTwistRotValueThumb ), (multDivNodeName + ".input1" + mmTwistRotValueThumb ))
                        cmds.connectAttr((multDivNodeName + ".o" + mmTwistRotValueThumb.lower() ), (iconGroupOne + ".rotate" + mmTwistRotValueThumb )) 
                        
                        #Connects the rotations of the control icon's attribute to the input of another multiply divide node and output to a pad.
                        cmds.connectAttr((controlCurve + "." + currentJointChain[0] + "_twist"), (multDivNodeNameTwo + ".input1" + mmTwistRotValueThumb ))
                        cmds.connectAttr((multDivNodeNameTwo + ".o" + mmTwistRotValueThumb.lower() ), (iconGroupTwo + ".rotate" + mmTwistRotValueThumb ))
                else:

                    if(boolCurl):
                        
                        #Connects the rotations of the master control to the input of the multiply divide node and output to a pad.
                        cmds.connectAttr((masterControlIcon + ".rotate" + mmCurlRotValueFinger), (multDivNodeName + ".input1" + mmCurlRotValueFinger ))
                        cmds.connectAttr((multDivNodeName + ".o" + mmCurlRotValueFinger.lower() ), (iconGroupOne + ".rotate" + mmCurlRotValueFinger )) 
                        
                        #Connects the rotations of the control icon's attribute to the input of another multiply divide node and output to a pad.
                        cmds.connectAttr((controlCurve + "." + currentJointChain[0] + "_curl"), (multDivNodeNameTwo + ".input1" + mmCurlRotValueFinger ))
                        cmds.connectAttr((multDivNodeNameTwo + ".o" + mmCurlRotValueFinger.lower() ), (iconGroupTwo + ".rotate" + mmCurlRotValueFinger ))
                        
                    if(boolSpread):
                        
                        #Connects the rotations of the master control to the input of the multiply divide node and output to a pad.
                        cmds.connectAttr((masterControlIcon + ".rotate" + mmSpreadRotValueFinger ), (multDivNodeName + ".input1" + mmSpreadRotValueFinger ))
                        cmds.connectAttr((multDivNodeName + ".o" + mmSpreadRotValueFinger.lower() ), (iconGroupOne + ".rotate" + mmSpreadRotValueFinger )) 
                                
                        #Connects the rotations of the control icon's attribute to the input of another multiply divide node and output to a pad.
                        cmds.connectAttr((controlCurve + "." + currentJointChain[0] + "_spread"), (multDivNodeNameTwo + ".input1" + mmSpreadRotValueFinger ))
                        cmds.connectAttr((multDivNodeNameTwo + ".o" + mmSpreadRotValueFinger.lower() ), (iconGroupTwo + ".rotate" + mmSpreadRotValueFinger ))
                                
                    if(boolTwist):
                        
                        #Connects the rotations of the master control to the input of the multiply divide node and output to a pad.
                        cmds.connectAttr((masterControlIcon + ".rotate" + mmTwistRotValueFinger ), (multDivNodeName + ".input1" + mmTwistRotValueFinger ))
                        cmds.connectAttr((multDivNodeName + ".o" + mmTwistRotValueFinger.lower() ), (iconGroupOne + ".rotate" + mmTwistRotValueFinger )) 
                        
                        #Connects the rotations of the control icon's attribute to the input of another multiply divide node and output to a pad.
                        cmds.connectAttr((controlCurve + "." + currentJointChain[0] + "_twist"), (multDivNodeNameTwo + ".input1" + mmTwistRotValueFinger ))
                        cmds.connectAttr((multDivNodeNameTwo + ".o" + mmTwistRotValueFinger.lower() ), (iconGroupTwo + ".rotate" + mmTwistRotValueFinger ))
                    
                if (counter >= 1):
                    cmds.parent(iconGroupThree, padParent)
                    
                padParent = iconRenamed
                
                #Need to apply the mult-Div Nodes to the multiplier attribute
                if( mmThumbBool):
                    
                    if(boolSpread):
                        expressionHappyFunTime = "if( " + multiplierSpreadName + " >= 0){ " + multDivNodeName + ".input2" + mmSpreadRotValueThumb + " = 1+( " + multiplierSpreadName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeName + ".input2" + mmSpreadRotValueThumb + " = 1-( " + multiplierSpreadName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_spread"), ae=0, uc=all )

                        expressionHappyFunTime = "if( " + multiplierSpreadName + " >= 0){ " + multDivNodeNameTwo + ".input2" + mmSpreadRotValueThumb + " = 1+( " + multiplierSpreadName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeNameTwo + ".input2" + mmSpreadRotValueThumb + " = 1-( " + multiplierSpreadName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_spread"), ae=0, uc=all )

                    if(boolCurl):
                        expressionHappyFunTime = "if( " + multiplierCurlName + " >= 0){ " + multDivNodeName + ".input2" + mmCurlRotValueThumb + " = 1+( " + multiplierCurlName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeName + ".input2" + mmCurlRotValueThumb + " = 1-( " + multiplierCurlName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_curl"), ae=0, uc=all )

                        expressionHappyFunTime = "if( " + multiplierCurlName + " >= 0){ " + multDivNodeNameTwo + ".input2" + mmCurlRotValueThumb + " = 1+( " + multiplierCurlName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeNameTwo + ".input2" + mmCurlRotValueThumb + " = 1-( " + multiplierCurlName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_curl"), ae=0, uc=all )

                    if(boolTwist):
                        expressionHappyFunTime = "if( " + multiplierTwistName + " >= 0){ " + multDivNodeName + ".input2" + mmTwistRotValueThumb + " = 1+( " + multiplierTwistName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeName + ".input2" + mmTwistRotValueThumb + " = 1-( " + multiplierTwistName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_twist"), ae=0, uc=all )
            
                        expressionHappyFunTime = "if( " + multiplierTwistName + " >= 0){ " + multDivNodeNameTwo + ".input2" + mmTwistRotValueThumb + " = 1+( " + multiplierTwistName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeNameTwo + ".input2" + mmTwistRotValueThumb + " = 1-( " + multiplierTwistName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_twist"), ae=0, uc=all )
            
                else: 
                    if(boolSpread):
                        expressionHappyFunTime = "if( " + multiplierSpreadName + " >= 0){ " + multDivNodeName + ".input2" + mmSpreadRotValueFinger + " = 1+( " + multiplierSpreadName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeName + ".input2" + mmSpreadRotValueFinger + " = 1-( " + multiplierSpreadName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_spread"), ae=0, uc=all )

                        expressionHappyFunTime = "if( " + multiplierSpreadName + " >= 0){ " + multDivNodeNameTwo + ".input2" + mmSpreadRotValueFinger + " = 1+( " + multiplierSpreadName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeNameTwo + ".input2" + mmSpreadRotValueFinger + " = 1-( " + multiplierSpreadName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_spread"), ae=0, uc=all )

                    if(boolCurl):
                        expressionHappyFunTime = "if( " + multiplierCurlName + " >= 0){ " + multDivNodeName + ".input2" + mmCurlRotValueFinger + " = 1+( " + multiplierCurlName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeName + ".input2" + mmCurlRotValueFinger + " = 1-( " + multiplierCurlName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_curl"), ae=0, uc=all )

                        expressionHappyFunTime = "if( " + multiplierCurlName + " >= 0){ " + multDivNodeNameTwo + ".input2" + mmCurlRotValueFinger + " = 1+( " + multiplierCurlName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeNameTwo + ".input2" + mmCurlRotValueFinger + " = 1-( " + multiplierCurlName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_curl"), ae=0, uc=all )

                    if(boolTwist):
                        expressionHappyFunTime = "if( " + multiplierTwistName + " >= 0){ " + multDivNodeName + ".input2" + mmTwistRotValueFinger + " = 1+( " + multiplierTwistName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeName + ".input2" + mmTwistRotValueFinger + " = 1-( " + multiplierTwistName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_twist"), ae=0, uc=all )
            
                        expressionHappyFunTime = "if( " + multiplierTwistName + " >= 0){ " + multDivNodeNameTwo + ".input2" + mmTwistRotValueFinger + " = 1+( " + multiplierTwistName + "/10) * " + str(multiplierValSmall) + "/ " + str(counter+1) + ";} else{ " + multDivNodeNameTwo + ".input2" + mmTwistRotValueFinger + " = 1-( " + multiplierTwistName + "/10) * " + str(multiplierValLarge) + "/ " + str(counter+1) + ";}"
                        cmds.expression(s=expressionHappyFunTime, n=("multiplier_exp_ " + currentJointChain[counter] + "_twist"), ae=0, uc=all )
            
                counter += 1
        
                multiplierValSmall += multiplierCounterMultiplier
                
                multiplierValLarge -= multiplierCounterMultiplier
                    
            counterOut += 1
            
            #connect vis controls from master control to group
            cmds.connectAttr((masterControlIcon + ".extra_detail_vis"), (visTogGroupName + ".visibility"))
            
            #connect seperate master control vis ctrls to main control
            cmds.connectAttr((controlCurve + ".extra_detail_vis"), (masterControlIcon + ".extra_detail_vis"))
            
            #lock and hide control
            cmds.setAttr((masterControlIcon + ".extra_detail_vis"), l = 1, k = 0, channelBox = 0)

        #delete the original icon
        cmds.delete(originalIcon)

        #deselect all
        cmds.select(cl = 1)

        #return the controls which were made
        return mmControlsMade

    else:
            print "No Selection"
            
def tentacleConnector(*args):
    
    mmSelectedInScene = cmds.ls(sl=1)
    
    tentController = mmSelectedInScene[0]
    tentMultiplier = mmSelectedInScene[1]
    tentPad1 = mmSelectedInScene[2]
    tentPad2 = mmSelectedInScene[3]
    tentPad3 = mmSelectedInScene[4]
    tentPad4 = mmSelectedInScene[5]
    tentPad5 = mmSelectedInScene[6]
    tentPad6 = mmSelectedInScene[7]
    
    #create mult-div nodes
    multDivNodeName1 = cmds.shadingNode("multiplyDivide", au = 1, n = (tentPad1 + "_multDivNode"))
    multDivNodeName2 = cmds.shadingNode("multiplyDivide", au = 1, n = (tentPad2 + "_multDivNode"))
    multDivNodeName3 = cmds.shadingNode("multiplyDivide", au = 1, n = (tentPad3 + "_multDivNode"))
    multDivNodeName4 = cmds.shadingNode("multiplyDivide", au = 1, n = (tentPad4 + "_multDivNode"))
    multDivNodeName5 = cmds.shadingNode("multiplyDivide", au = 1, n = (tentPad5 + "_multDivNode"))
    multDivNodeName6 = cmds.shadingNode("multiplyDivide", au = 1, n = (tentPad6 + "_multDivNode"))
    
    #connect control icon to input attributes of mult-div nodes
    cmds.connectAttr((tentController + ".rotate"),(multDivNodeName1 + ".input1"), f = 1)
    cmds.connectAttr((tentController + ".rotate"),(multDivNodeName2 + ".input1"), f = 1)
    cmds.connectAttr((tentController + ".rotate"),(multDivNodeName3 + ".input1"), f = 1)
    cmds.connectAttr((tentController + ".rotate"),(multDivNodeName4 + ".input1"), f = 1)
    cmds.connectAttr((tentController + ".rotate"),(multDivNodeName5 + ".input1"), f = 1)
    cmds.connectAttr((tentController + ".rotate"),(multDivNodeName6 + ".input1"), f = 1)
    
    #create expressions for each tentacle to rotate in space
    tentExpressionA1 = "if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName1 + ".input2X = 1+( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName1 + ".input2X = 1-6*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName2 + ".input2X = 1+2*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName2 + ".input2X = 1-5*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName3 + ".input2X = 1+3*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName3 + ".input2X = 1-4*( " + tentMultiplier + ".translateY)/.16;}if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName4 + ".input2X = 1+4*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName4 + ".input2X = 1-3*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName5 + ".input2X = 1+5*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName5 + ".input2X = 1-2*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName6 + ".input2X = 1+6*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName6 + ".input2X = 1-( " + tentMultiplier + ".translateY)/.16;}"

    tentExpressionB1 = "if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName1 + ".input2Y = 1+( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName1 + ".input2Y = 1-6*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName2 + ".input2Y = 1+2*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName2 + ".input2Y = 1-5*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName3 + ".input2Y = 1+3*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName3 + ".input2Y = 1-4*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName4 + ".input2Y = 1+4*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName4 + ".input2Y = 1-3*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName5 + ".input2Y = 1+5*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName5 + ".input2Y = 1-2*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName6 + ".input2Y = 1+6*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName6 + ".input2Y = 1-( " + tentMultiplier + ".translateY)/.16;}"

    tentExpressionC1 = "if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName1 + ".input2Z = 1+( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName1 + ".input2Z = 1-6*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName2 + ".input2Z = 1+2*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName2 + ".input2Z = 1-5*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName3 + ".input2Z = 1+3*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName3 + ".input2Z = 1-4*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName4 + ".input2Z = 1+4*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName4 + ".input2Z = 1-3*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName5 + ".input2Z = 1+5*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName5 + ".input2Z = 1-2*( " + tentMultiplier + ".translateY)/.16;} if(( " + tentMultiplier + ".translateY) >= 0){ " + multDivNodeName6 + ".input2Z = 1+6*( " + tentMultiplier + ".translateY)/.16;} else{ " + multDivNodeName6 + ".input2Z = 1-( " + tentMultiplier + ".translateY)/.16;}"
    
    #use expressions to drive tentacles
    cmds.expression(s=tentExpressionA1, n=("multDivFactor1_ " + tentMultiplier), ae=0, uc=all )
    
    cmds.expression(s=tentExpressionB1, n=("multDivFactor2_ " + tentMultiplier), ae=0, uc=all )
    
    cmds.expression(s=tentExpressionC1, n=("multDivFactor3_ " + tentMultiplier), ae=0, uc=all )
    
    #connect output attributes of mutl-div nodes
    cmds.connectAttr((multDivNodeName1 + ".output"),(tentPad1 + ".rotate"))
    cmds.connectAttr((multDivNodeName2 + ".output"),(tentPad2 + ".rotate"))
    cmds.connectAttr((multDivNodeName3 + ".output"),(tentPad3 + ".rotate"))
    cmds.connectAttr((multDivNodeName4 + ".output"),(tentPad4 + ".rotate"))
    cmds.connectAttr((multDivNodeName5 + ".output"),(tentPad5 + ".rotate"))
    cmds.connectAttr((multDivNodeName6 + ".output"),(tentPad6 + ".rotate"))

def clusterMaker(*args):
            
    selectedStuff = cmds.ls(sl = 1)
    fullCurveName = selectedStuff[0]
    #numberOfSpans = cmds.intField("clusterMakerVal", q = 1, v = 1)
    clusterGroupName = cmds.group(n = fullCurveName + "_cluster_group#", em = 1)
    iconGroupName = cmds.group(n = fullCurveName + "_icon_group#", em = 1)
    
    infoFromCurve = cmds.shadingNode("curveInfo", asUtility = 1, n = fullCurveName + "_curveInfo#")
    cmds.connectAttr(fullCurveName + ".worldSpace[0]", infoFromCurve + ".inputCurve", f = 1)
    
    numberOfKnots = cmds.getAttr(infoFromCurve + ".kn")
    numberOfSpans = len(numberOfKnots[0])
    
    i = 0
    while (i <= numberOfSpans - 3):
        clusterIterName = fullCurveName + ".cv[" + str(i) + "]"
        cmds.select(clusterIterName, r = 1)
        cmds.CreateCluster()
        
        clusterIterName = cmds.rename( fullCurveName + "_cluster#")
        cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)
        cmds.xform( cp = 1 )
        
        
        #put the clusters under parent cluster group
        cmds.parent(clusterIterName,clusterGroupName)

        #Create a new icon from the original
        newBoxIconName = cmds.circle()
        cmds.xform(scale = [.3, .3, .3])
        newBoxIconName = cmds.rename(newBoxIconName[0], fullCurveName + "_icon#")
        cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)
        cmds.xform(newBoxIconName, cp = 1 )
        
        #take second group and parentConstraint("name", mo = 1)
        nameOfConstraint = cmds.parentConstraint(clusterIterName, newBoxIconName, mo = 0)
        
        #group it and name it
        iconGroupOne = cmds.group(newBoxIconName, name = (clusterIterName + "_pad#"))
        cmds.xform( cp = 1 )
        
        #delete the parent contstraint
        cmds.delete(nameOfConstraint)
        cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)
        
        cmds.xform( t = [-.25,-.25,-.25] )
        
        cmds.parent(iconGroupOne, iconGroupName)
        
        cmds.parentConstraint(newBoxIconName, clusterIterName, mo = 1)

        cmds.xform( cp = 1 )
        
        cmds.setAttr(clusterGroupName + ".visibility", 0)
        
        i += 1

def makeSplineStretchy(*args):
    
    #select the curve you want to be stretchy
    selectedStuff = cmds.ls(sl = 1)
    splineCurveName = selectedStuff[0]
    jointToWorkOn = cmds.ls((selectedStuff[1]),dag=1)
    numDivisions = len(jointToWorkOn)
    
    numeroDownTheChain = cmds.radioButtonGrp("stretchySplineRadioBoxes", q = 1, sl = 1)
    
    if(numeroDownTheChain == 1):
        axisDownTheChain = "X"
    if(numeroDownTheChain == 2):
        axisDownTheChain = "Y"
    if(numeroDownTheChain == 3):
        axisDownTheChain = "Z"
    
    #Need to find the default length of the curve
    defaultArcLength = cmds.arclen(splineCurveName)
    
    #Need to create a node to find the changing value of the curve
    infoOfCurve = cmds.shadingNode("curveInfo", asUtility = 1, n = splineCurveName + "_curveInfo#")
    cmds.connectAttr(splineCurveName + ".worldSpace[0]", infoOfCurve + ".inputCurve", f = 1)
    
    changingArcLength = cmds.getAttr(infoOfCurve + ".arcLength")
    
    #Need to create a method of driving the joints into a stretchy rig
    stretchyCondition = cmds.shadingNode("condition", asUtility = 1, n = (splineCurveName + "_stretchyCond#"))
    
    #set values for 1 and 0
    cmds.setAttr( stretchyCondition + ".colorIfTrueR", 1 )
    cmds.setAttr( stretchyCondition + ".colorIfFalseR", 0 )
    
    cmds.setAttr( stretchyCondition + ".operation", 3 )
    cmds.connectAttr( (infoOfCurve + ".arcLength"), stretchyCondition + ".firstTerm", f = 1)
    cmds.setAttr( stretchyCondition + ".secondTerm", (defaultArcLength) )
    
    #cmds.connectAttr( stretchyCondition + ".nodeState", f = 1)
    
    #create a multDiv node to use
    multDivSplineNode = cmds.shadingNode("multiplyDivide", asUtility = 1, n = splineCurveName + "_multDiv#")
    
    cmds.connectAttr( (infoOfCurve + ".arcLength"), multDivSplineNode + ".input1X", f = 1)
    cmds.setAttr( multDivSplineNode + ".input2X", (defaultArcLength) )
    cmds.setAttr( multDivSplineNode  + ".operation", 2)
    
    #create a multDiv node to use
    multDivOnOffNode = cmds.shadingNode("multiplyDivide", asUtility = 1, n = splineCurveName + "_multDiv#")
    
    cmds.connectAttr( (multDivSplineNode + ".outputX"), multDivOnOffNode + ".input1X", f = 1)
    cmds.connectAttr( (stretchyCondition + ".outColorR"), multDivOnOffNode + ".input2X", f = 1)
    
    #use final value, need to plug in to its proper scale direction
    #insert the final value into the scale of all the new joints
    i = 0
    
    while (i<=numDivisions-3):
        #still need to make a similar attachment to an on off icon
        if (i == 0):
                selectedJointName = jointToWorkOn[0]
        else:
                selectedJointName = jointToWorkOn[0]
        
        expression_stretch_values = "if(" + multDivOnOffNode + ".outputX >= 1){ " + selectedJointName + ".scale " + str(axisDownTheChain) + " = " + multDivOnOffNode + ".outputX;} else{ " + selectedJointName + ".scale " + str(axisDownTheChain) + " = 1;}"

        
        #cmds.connectAttr((multDivOnOffNode + ".outputX"), (selectedJointName + ".scaleY"), f = 1)
        cmds.expression(s=expression_stretch_values, n=(splineCurveName + "_expression"), ae=0, uc=all )

        #pickwalk to the child and store the name as the next working name
        cmds.select(selectedJointName)
        nextJointToWorkOn = cmds.listRelatives(c = 1)
        
        #set new parent joint
        jointToWorkOn = nextJointToWorkOn
        
        i += 1

'''
####################################
Need a space switcher that takes multiple "children" and creates the exact same space switching set ups on the same controller so they swap in unison.
Select the icon which will control the switch, then the pad which the constraints will be on, then each item which will be constraining.
#   This function also can take only a single child.
#   This function also allows a control icon to be different than the thing being space switched.
####################################
'''
def spaceSwitcherMulti( mmConstraintType = False, mmControlIcon = False, mmInputList = [], mmParentList = [], mmCreateTheAttr = True, mmSingleAttrName = "",  *args ):

    #Constraint Numbers:
    #   1: pointConstraint
    #   2: orientConstraint
    #   3: parentConstraint
    #   4: scaleConstraint

    if ( mmConstraintType == False or mmControlIcon == False ):
        #Run with selected objects as a single space switcher
        mmConstraintType = cmds.radioButtonGrp("switcherSystemChkBoxes", q = 1, sl = 1)
        mmCreateTheAttr = cmds.checkBoxGrp("switcherSystemChkBoxes2", q = 1, v1 = 1)

        selectedStuff = cmds.ls(sl = 1)

        #grab the icon which all the switching info is going to be on
        mmControlIcon = selectedStuff[0]

        #grab the pad which all the constraints are going to
        nameOfPad = selectedStuff[1]

        mmInputList = [selectedStuff[1]]

    else:
        selectedStuff = ["",""]

        for mmParent in mmParentList:
            selectedStuff.append(mmParent)
    
    #create a list to put all the names into
    listOfObjectsToConstrainTo = [""]

    #find total number of objects to constrain to
    totalNumberOfConstraints = len(selectedStuff)-2

    #grab all items which are selected and create a constraint system for them
    i = 2
    while(i <= totalNumberOfConstraints+1):
        listOfObjectsToConstrainTo.append( selectedStuff[i] )
        
        i += 1
       
    mmCounterOuter = 0

    for mmInput in mmInputList:

        if ( mmCounterOuter > 0):
            mmCreateTheAttr = False

        #grab the pad which all the constraints are going to
        nameOfPad = mmInput

        #grab all the constraint names
        constraintNamesList = [""]


        i = 1
        while(i <= totalNumberOfConstraints):

            #?  for additional types of space constraints, nothing seems to work but parent
            if (mmConstraintType == 1):
                actualConstraintName = mmControlIcon + "_pointConstraint#"
                nameOfConstraint = cmds.pointConstraint(listOfObjectsToConstrainTo[i], nameOfPad, mo = 1, w = 1, n = actualConstraintName )[0]
                constraintNamesList.append(nameOfConstraint)
                #Does not keep offset despite the MO bool being fed True.. unsure why.
                    
            elif (mmConstraintType == 2):
                actualConstraintName = mmControlIcon + "_orientConstraint#"
                nameOfConstraint = cmds.orientConstraint(listOfObjectsToConstrainTo[i], nameOfPad, mo = 1, w = 1, n = actualConstraintName )[0]
                constraintNamesList.append(nameOfConstraint)
                #Does not keep offset despite the MO bool being fed True.. unsure why.

            elif (mmConstraintType == 3):
                actualConstraintName = mmControlIcon + "_parentConstraint#"
                nameOfConstraint = cmds.parentConstraint(listOfObjectsToConstrainTo[i], nameOfPad, mo = 1, w = 1, n = actualConstraintName )[0]
                constraintNamesList.append(nameOfConstraint)

            elif (mmConstraintType == 4):
                actualConstraintName = mmControlIcon + "_scaleConstraint#"
                nameOfConstraint = cmds.scaleConstraint(listOfObjectsToConstrainTo[i], nameOfPad, mo = 1, w = 1, n = actualConstraintName )[0]
                constraintNamesList.append(nameOfConstraint)

            else:
                print "Invalid Selection"
        
            i += 1

        if( mmCreateTheAttr ):
            if( mmSingleAttrName != "" and mmSingleAttrName != False ):

                mmAttrCheck = None
                try:
                    #create Attributes and connect them
                    cmds.addAttr(mmControlIcon, ln = "space_switching", at = "enum", en = "---------------:", k = 1)
                    cmds.setAttr(mmControlIcon + ".space_switching", e = 1, l = 1)
                except:
                    print "mmRF.spaceSwitcherMulti found a spaceswitcher attr already exists."
                    
                #Create single Attr
                cmds.addAttr(mmControlIcon, ln = mmSingleAttrName, at = "double", min = 0, max = 10, dv = 0, k = 1)

                mmCreatedAttr = mmControlIcon + "." + mmSingleAttrName
                
                i = 1
                while(i <= totalNumberOfConstraints):
                    currentConstraintName = listOfObjectsToConstrainTo[i]
                    #mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
                    #Example: mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-10, 10], [90, 0], 1 )

                    if( i == 1 ):
                        mmCreateSDK( mmCreatedAttr, nameOfConstraint, "." + currentConstraintName + "W" + str(i-1), [0,10/(totalNumberOfConstraints-1)*(i)], [1,0], 1 )

                    elif( i > 1 and i < totalNumberOfConstraints ):
                        mmCreateSDK( mmCreatedAttr, nameOfConstraint, "." + currentConstraintName + "W" + str(i-1), [10/(totalNumberOfConstraints-1)*(i-2), 10/(totalNumberOfConstraints-1)*(i-1), 10/(totalNumberOfConstraints-1)*(i)], [0,1,0], 1 )

                    elif( i == totalNumberOfConstraints ):
                        mmCreateSDK( mmCreatedAttr, nameOfConstraint, "." + currentConstraintName + "W" + str(i-1), [10/(totalNumberOfConstraints-1)*(i-2),10], [0,1], 1 )

                    i += 1

                cmds.setAttr( mmCreatedAttr, 0 )

            else:
                #create Attributes and connect them
                mmCreatedAttr = cmds.addAttr(mmControlIcon, ln = "space_switching", at = "enum", en = "---------------:", k = 1)
                cmds.setAttr(mmControlIcon + ".space_switching", e = 1, l = 1)
                
                i = 1
                while(i <= totalNumberOfConstraints):
                    # print "listOfObjectsToConstrainTo[i]", listOfObjectsToConstrainTo[i]
                    currentConstraintName = listOfObjectsToConstrainTo[i]
            
                    cmds.addAttr(mmControlIcon, ln = currentConstraintName, at = "double", min = 0, max = 10, dv = 0, k = 1)
                    setRangeNamed = cmds.shadingNode( "setRange", asUtility = 1, n = mmControlIcon + "_setRange#")
                    cmds.setAttr(setRangeNamed + ".maxX", 1)
                    cmds.setAttr(setRangeNamed + ".oldMaxX", 10)
                    
                    cmds.connectAttr(  mmControlIcon + "." + currentConstraintName, setRangeNamed + ".valueX", f = 1)
                    cmds.connectAttr(  setRangeNamed + ".outValueX", nameOfConstraint + "." + currentConstraintName + "W" + str(i-1), f = 1)

                    i += 1

                #Need to then set one of the values as default of 1
                cmds.setAttr( mmControlIcon + "." + listOfObjectsToConstrainTo[1], 10 )

        mmCounterOuter += 1

        cmds.select(cl = 1)

    return mmCreatedAttr

'''
####################################
Need a space switcher that takes multiple "children" and creates the exact same space switching set ups on the same controller so they swap in unison.
Select the icon which will control the switch, then the pad which the constraints will be on, then each item which will be constraining.
#   This function also can take only a single child.
#   This function also allows a control icon to be different than the thing being space switched.
####################################
'''
def spaceSwitcherMultiSimple( *args ):

    spaceSwitcherMulti( mmConstraintType = False, mmControlIcon = False, mmInputList = [], mmParentList = [], mmCreateTheAttr = True, mmSingleAttrName = "space_switcher" )


'''
Function #? Needs a description - what does this do and how does it work?
'''
def multiChainFKHelper(*args):
    mmSelectedInScene = cmds.ls(sl = 1)
    controlCurveName = mmSelectedInScene[0]
    #chain=cmds.ls(mmSelectedInScene[1],dag=1)
    
    #find total number of joints
    totalNumberOfJoints = (len(mmSelectedInScene)-1)
    
    #select first joint
    currentSelectedJoint = mmSelectedInScene[1]
    
    jointsToWorkOnTog = cmds.radioButtonGrp("multiChainFKHelperRadioButtons", q = 1, sl = 1)
    
    i = 1
    
    if(jointsToWorkOnTog == 1):
        while (currentSelectedJoint):
            #currentJointToWorkOn = mmSelectedInScene[i]
            
            #create a multiDiv node to apply various changes to overall rotations of icon to joints
            #Need to create a method of driving the joints into a stretchy rig
            multDivNodeName = cmds.shadingNode("multiplyDivide", asUtility = 1, n = (controlCurveName + "_multDivNode#"))
            cmds.setAttr( multDivNodeName  + ".operation", 2)
            
            #finalMultiple = (float(i)/totalNumberOfJoints)
            finalMultiple = i

            #connect control icon to input attributes of mult-div nodes
            cmds.connectAttr((controlCurveName + ".rotate"), (multDivNodeName + ".input1"), f = 1)
            cmds.setAttr((multDivNodeName + ".input2X"), finalMultiple)
            cmds.setAttr((multDivNodeName + ".input2Y"), finalMultiple)
            cmds.setAttr((multDivNodeName + ".input2Z"), finalMultiple)
            cmds.connectAttr((multDivNodeName + ".output"), (currentSelectedJoint + ".rotate"))
            
            cmds.select(currentSelectedJoint)
            
            currentSelectedJoint = cmds.listRelatives(c = 1)
            currentSelectedJoint=currentSelectedJoint[0]
            i += 1
                                                
    else: 

        while(i <= (totalNumberOfJoints)):
            #currentJointToWorkOn = mmSelectedInScene[i]
            
            #create a multiDiv node to apply various changes to overall rotations of icon to joints
            #Need to create a method of driving the joints into a stretchy rig
            multDivNodeName = cmds.shadingNode("multiplyDivide", asUtility = 1, n = (controlCurveName + "_multDivNode#"))
            cmds.setAttr( multDivNodeName  + ".operation", 2)
            
            #finalMultiple = (float(i)/totalNumberOfJoints)
            finalMultiple = i

            #connect control icon to input attributes of mult-div nodes
            cmds.connectAttr((controlCurveName + ".rotate"), (multDivNodeName + ".input1"), f = 1)
            cmds.setAttr((multDivNodeName + ".input2X"), finalMultiple)
            cmds.setAttr((multDivNodeName + ".input2Y"), finalMultiple)
            cmds.setAttr((multDivNodeName + ".input2Z"), finalMultiple)
            cmds.connectAttr((multDivNodeName + ".output"), (currentSelectedJoint + ".rotate"))
            
            cmds.select(currentSelectedJoint)
            
            currentSelectedJoint = cmds.listRelatives(c = 1)
            currentSelectedJoint=currentSelectedJoint[0]
            i += 1
    
'''
Function for creating any number of Set Driven Keys
'''
def mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper ):

    #mmCreateSDK( mmObjectController, mmObjectSlave, mmObjectSlaveManip, mmControllerValueList, mmSlaveValueList, mmAngleFlipper )
    #Example: mmCreateSDK( mmFootRollAttr, mmRevFTRigList[0], ".rotateX",  [-10, 10], [90, 0], 1 )

    mmObjectSlaveAndManip = mmObjectSlave + mmObjectSlaveManip

    #Find Default Value of Controller to set back to after SDK is completed
    mmObjectControllerDefValue = cmds.getAttr( mmObjectController )

    mmTempLength = len(mmControllerValueList)-1
    mmCounter = -1

    # print "mmObjectController", mmObjectController
    # print "mmObjectSlave", mmObjectSlave
    # print "mmObjectSlaveManip", mmObjectSlaveManip
    # print "mmControllerValueList", mmControllerValueList
    # print "mmSlaveValueList", mmSlaveValueList
    # print "mmAngleFlipper", mmAngleFlipper

    while mmCounter <= mmTempLength:
        if ( mmCounter == -1 ):
            #The first value should be the default value - where nothing is moved, just in case there is an issue
            cmds.setDrivenKeyframe( mmObjectSlaveAndManip, currentDriver = mmObjectController)

        else:

            #set attr to appropriate value
            cmds.setAttr( mmObjectController, mmControllerValueList[mmCounter] )
            cmds.setAttr( mmObjectSlaveAndManip, mmSlaveValueList[mmCounter] * mmAngleFlipper )

            cmds.setDrivenKeyframe( mmObjectSlaveAndManip, currentDriver = mmObjectController)

            cmds.setAttr( mmObjectController, mmControllerValueList[0] )


        mmCounter += 1


    #Set Controller back to default value
    cmds.setAttr( mmObjectController, mmObjectControllerDefValue )

    #Set animation curves to linear
    #cmds.selectKey( clear = True )
    mel.eval( "selectKey " + mmObjectSlave + " ;" )
    cmds.keyTangent( itt = "linear", ott = "linear" )

'''
Function for grabbing any number of meshes (in a list) and getting bounding box information from them
This function returns a list of lists that is ordered as Min, Mid, Max, Total - each of a list of X,Y,Z
'''
def mmGrabBoundingBoxInfo( mmListOfDesiredMeshes = [] ):

    #mmGrabBoundingBoxInfo returns mmDictOfBoundingBoxLists with this information:
    # {
    #     "min":       [X, Y, Z],
    #     "midPoint":  [X, Y, Z],
    #     "max":       [X, Y, Z],
    #     "total":     [X, Y, Z],
    #     "pivot":     [X, Y, Z]
    # }

    if ( mmListOfDesiredMeshes == []):
        mmListOfDesiredMeshes = cmds.ls(sl = 1)

    if ( type(mmListOfDesiredMeshes) != type([]) ):
        mmListOfDesiredMeshes = [mmListOfDesiredMeshes]

    if ( type(mmListOfDesiredMeshes[0]) == type([]) ):
        mmListOfDesiredMeshes = mmListOfDesiredMeshes[0]

    mmXOverallMin = 0
    mmYOverallMin = 0
    mmZOverallMin = 0
    mmXOverallMax = 0
    mmYOverallMax = 0
    mmZOverallMax = 0
    mmDictOfBoundingBoxLists = []
    mmBoundingBoxListPiv = []

    i = 0
    for mmMesh in mmListOfDesiredMeshes:

        cmds.select(mmMesh)

        mmBoundingBoxList = cmds.xform( q = 1, boundingBox = 1, ws = 1 )
        mmBoundingBoxListPiv = cmds.xform( q = 1, pivots = 1, ws = 1 )

        mmXMin = mmBoundingBoxList[0]
        mmYMin = mmBoundingBoxList[1]
        mmZMin = mmBoundingBoxList[2]
        mmXMax = mmBoundingBoxList[3]
        mmYMax = mmBoundingBoxList[4]
        mmZMax = mmBoundingBoxList[5]

        if ( i == 0 ):

            mmXOverallMin = mmXMin
            mmYOverallMin = mmYMin
            mmZOverallMin = mmZMin
            mmXOverallMax = mmXMax
            mmYOverallMax = mmYMax
            mmZOverallMax = mmZMax

            i = 1

        else:

            if ( mmXMin < mmXOverallMin ):
                mmXOverallMin = mmXMin

            if ( mmYMin < mmYOverallMin ):
                mmYOverallMin = mmYMin

            if ( mmZMin < mmZOverallMin ):
                mmZOverallMin = mmZMin

            if ( mmXMax > mmXOverallMax ):
                mmXOverallMax = mmXMax

            if ( mmYMax > mmYOverallMax ):
                mmYOverallMax = mmYMax

            if ( mmZMax > mmZOverallMax ):
                mmZOverallMax = mmZMax

    #Find halfway point (i.e. center of object) and how far to move controller to be in the right place
    mmXOverallTotal = abs(mmXOverallMax - mmXOverallMin)
    mmYOverallTotal = abs(mmYOverallMax - mmYOverallMin)
    mmZOverallTotal = abs(mmZOverallMax - mmZOverallMin)

    mmXOverallMidPoint = mmXOverallMax - mmXOverallTotal/2
    mmYOverallMidPoint = mmYOverallMax - mmYOverallTotal/2
    mmZOverallMidPoint = mmZOverallMax - mmZOverallTotal/2

    mmDictOfBoundingBoxLists = {
            "min":         [mmXOverallMin, mmYOverallMin, mmZOverallMin],
            "midPoint":    [mmXOverallMidPoint, mmYOverallMidPoint, mmZOverallMidPoint],
            "max":         [mmXOverallMax, mmYOverallMax, mmZOverallMax],
            "total":       [mmXOverallTotal, mmYOverallTotal, mmZOverallTotal],
            "pivot":       [mmBoundingBoxListPiv[0], mmBoundingBoxListPiv[1], mmBoundingBoxListPiv[2]]
        }

    return mmDictOfBoundingBoxLists

'''
Function for taking the children of an object, parenting them out under something else, then constraining it to the object it was under before.
'''
def mmParentRemovalAndConstrainOLD( mmObjectWithChildren = None, mmOuterStructureForParenting = "root_Control", mmConstraintType = 0, mmExceptions = [], *args ):
    #Must create a locator for each object to point constrain to, because maya doesn't work right :(
    mmListOfCreatedLocators = []

    if (mmObjectWithChildren == None):
        print "mmRF.mmParentRemovalAndPointConstrain cannot work without specific information passed in."
        return None

    #Need to rig all the current children of the child objects to constrain at the location they are from their current parent
    mmChildrenOfObject = []

    #Grab all children of mmObjectWithChildren
    mmChildrenOfObject = cmds.listRelatives(mmObjectWithChildren, c = 1)

    #If there are children
    if ( mmChildrenOfObject and len(mmChildrenOfObject) > 1 ):
        #Parent to "root_Control"
        for mmChild in mmChildrenOfObject:

            if ( cmds.objectType(mmChild) == "transform" ):

                if mmChild in mmExceptions:
                    print "mmRF.mmParentRemovalAndConstrain found exception:", mmChild

                else:
                    cmds.parent( mmChild, mmOuterStructureForParenting )

                    #GroupInPlace - so the controls stay clean
                    mmChildGroup = mmOF.mmGroupInPlace( mmChild )

                    #Create locator
                    mmLocatorHolder = cmds.spaceLocator(n = mmChild + "_PlaceHolder_Locator")[0]

                    #Move locator to where the mmChild currently is
                    mmOF.mmMoveObject( [ mmLocatorHolder, mmChild ] )

                    #Parent the locator to the original object
                    cmds.parentConstraint( mmObjectWithChildren, mmLocatorHolder )

                    #For adding additional types of constraints - not sure yet if we need it.
                        #for additional types of space constraints, nothing seems to work but parent
                    if (mmConstraintType == 1):
                        actualConstraintName = mmLocatorHolder + "_pointConstraint#"
                        nameOfConstraint = cmds.pointConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]
                        #?  Does not keep offset despite the MO bool being fed True?.. unsure why.  Verify that this is definitely happening in all circumstances.

                    elif (mmConstraintType == 2):
                        actualConstraintName = mmLocatorHolder + "_orientConstraint#"
                        nameOfConstraint = cmds.orientConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]

                    elif (mmConstraintType == 3):
                        actualConstraintName = mmLocatorHolder + "_parentConstraint#"
                        nameOfConstraint = cmds.parentConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]

                    elif (mmConstraintType == 4):
                        actualConstraintName = mmLocatorHolder + "_scaleConstraint#"
                        nameOfConstraint = cmds.scaleConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]

                    else:
                        print "Invalid Selection for mmRF.mmParentRemovalAndConstrain"

                    #Store locator name
                    mmListOfCreatedLocators.append(mmLocatorHolder)

    #Check position of headcontrol
    mmChecker = cmds.xform( "headExtra_Control", q = 1, t = 1, r = 1 )
    print "headExtra_Control '4'", mmChecker

    return mmListOfCreatedLocators


'''
Function for taking the children of an object, parenting them out under something else, then constraining it to the object it was under before.
'''
def mmParentRemovalAndConstrain( mmObjectWithChildren = None, mmOuterStructureForParenting = "root_Control", mmConstraintType = 0, mmExceptions = [], *args ):
    #Must create a locator for each object to point constrain to, because maya doesn't work right :(
    mmListOfCreatedLocators = []

    if (mmObjectWithChildren == None):
        print "mmRF.mmParentRemovalAndPointConstrain cannot work without specific information passed in."
        return None

    #Need to rig all the current children of the child objects to constrain at the location they are from their current parent
    mmChildrenOfObject = []

    #Grab all children of mmObjectWithChildren
    mmChildrenOfObject = cmds.listRelatives(mmObjectWithChildren, c = 1)

    #If there are children
    if ( mmChildrenOfObject and len(mmChildrenOfObject) > 1 ):
        #Parent to "root_Control"
        for mmChild in mmChildrenOfObject:

            if ( cmds.objectType(mmChild) == "transform" ):

                if mmChild in mmExceptions:
                    print "mmRF.mmParentRemovalAndConstrain found exception:", mmChild

                else:
                    # print "mmChild", mmChild
                    # print "parent of mmChild: ", cmds.listRelatives(mmChild, p= 1)

                    cmds.parent( mmChild, mmOuterStructureForParenting )

                    # #Need to clean the trans/rot/scale of this node, but must unparent the children to do so.
                    mmRecursiveUnparentAndCleanChildrensTransRotScale( mmChild )

                    #GroupInPlace - so the controls stay clean
                    mmChildGroup = mmOF.mmGroupInPlace( mmChild )

                    #Create locator
                    mmLocatorHolder = cmds.spaceLocator(n = mmChild + "_PlaceHolder_Locator")[0]

                    #Move locator to where the mmChild currently is
                    mmOF.mmMoveObject( [ mmLocatorHolder, mmChild ] )

                    #Parent the locator to the original object
                    cmds.parentConstraint( mmObjectWithChildren, mmLocatorHolder )

                    #For adding additional types of constraints - not sure yet if we need it.
                        #for additional types of space constraints, nothing seems to work but parent
                    if (mmConstraintType == 1):
                        actualConstraintName = mmLocatorHolder + "_pointConstraint#"
                        nameOfConstraint = cmds.pointConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]
                        #?  Does not keep offset despite the MO bool being fed True?.. unsure why.  Verify that this is definitely happening in all circumstances.

                    elif (mmConstraintType == 2):
                        actualConstraintName = mmLocatorHolder + "_orientConstraint#"
                        nameOfConstraint = cmds.orientConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]

                    elif (mmConstraintType == 3):
                        actualConstraintName = mmLocatorHolder + "_parentConstraint#"
                        nameOfConstraint = cmds.parentConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]

                    elif (mmConstraintType == 4):
                        actualConstraintName = mmLocatorHolder + "_scaleConstraint#"
                        nameOfConstraint = cmds.scaleConstraint(mmLocatorHolder, mmChildGroup, mo = 1, w = 1, n = actualConstraintName )[0]

                    else:
                        print "Invalid Selection for mmRF.mmParentRemovalAndConstrain"

                    #Store locator name
                    mmListOfCreatedLocators.append(mmLocatorHolder)


    # cmds.select(mmObjectWithChildren)
    # cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

    return mmListOfCreatedLocators


'''
Function for taking the an object, breaking out its children, freezing its transforms, reparenting its children underneath,
    and doing the same recursively until it runs out of children.
#?  This will likely fail when something can't have its values frozen - but we'll deal with tath when it happens.
'''
def mmRecursiveUnparentAndCleanChildrensTransRotScale( mmObjectWithChildren = None, mmExceptions = [], *args ):

    if ( mmObjectWithChildren != None ):
        #Grab all children of mmObjectWithChildren
        mmChildrenOfObject = cmds.listRelatives(mmObjectWithChildren, c = 1)
        # print "running clean tool on ", mmObjectWithChildren

        mmChildInfoList = []

        for mmChild in mmChildrenOfObject:

            if ( cmds.objectType(mmChild) == "transform" and mmChild not in mmExceptions ):

                mmChildsParent = mmObjectWithChildren
                cmds.parent(mmChild, world = 1)
                mmChildInfoList.append( [mmChild, mmChildsParent] )

        # print "mmChildrenOfObject", mmChildrenOfObject
        # print "mmChildInfoList", mmChildInfoList
        # print ""

        cmds.select(mmObjectWithChildren)
        # print "cleaning ", mmObjectWithChildren, "now"
        cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

        # print cmds.xform("headExtra_Control", q = 1, t = 1, r = 1)

        for mmChildStored in mmChildInfoList:

            #Reparent all the children we have taken apart - likely breaking their TransRotScale.
            cmds.parent(mmChildStored[0], mmChildStored[1])

            #Run function recursively to clean the children - or find where the problem child is.
            mmRecursiveUnparentAndCleanChildrensTransRotScale( mmChildStored[0], mmExceptions )
        
        # print "completed run for ", mmObjectWithChildren
        # print ""

    return None

