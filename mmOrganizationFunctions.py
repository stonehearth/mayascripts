"""

Function: mmOrganizationFunctions
Description: This is a collection of functions which help out with Organizational stuff in general.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.mel as mel

#Local
import mmScaleDownFrom3DSMax as mmSDF3M
import mmReturnFilepathOrFilename as mmRFOF
import mmSelectAnimatingParts as mmSAP
import mmRiggingFunctions as mmRF
import mmGetWorldTrans as mmGWT
import mmCreateLocAndParent as mmCLAP


######################################
############# DEFINES ################
######################################


'''
Lock and Hide Function:
-First loads in the selected objects of the scene so that multiple objects can be effected.
-Checks to make sure that at least one object is selected.
-Starts Loops to check each of the types of attributes on each object, and if they exist,
   Lock and Hide them
'''
def lockNHide(*args):

   mmSelectedInScene = cmds.ls(sl=1)
   
   if(mmSelectedInScene):
   
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxTrans", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".tx"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
       if(cmds.checkBoxGrp("chkBoxTrans", query = True, v2 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".ty"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
       if(cmds.checkBoxGrp("chkBoxTrans", query = True, v3 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".tz"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
         
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxRot", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".rx"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
       if(cmds.checkBoxGrp("chkBoxRot", query = True, v2 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".ry"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
       if(cmds.checkBoxGrp("chkBoxRot", query = True, v3 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".rz"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
         
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxScale", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".sx"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
       if(cmds.checkBoxGrp("chkBoxScale", query = True, v2 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".sy"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
       if(cmds.checkBoxGrp("chkBoxScale", query = True, v3 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".sz"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
         
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxVis", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".v"
         cmds.setAttr(mmSelected, lock=True, keyable=False, channelBox=False);
   else:
     print "Nothing is selected.";
     
'''
Unlock and Unhide Function:
-First loads in the selected objects of the scene so that multiple objects can be effected.
-Checks to make sure that at least one object is selected.
-Starts Loops to check each of the types of attributes on each object, and if they exist,
   Unlock and Unhide them

** The "keyable" flag is seperate because it sometimes will not trigger if grouped with everything else.
'''      
def unlockUnhide(*args):
   mmSelectedInScene = cmds.ls(sl=1)
   
   if(mmSelectedInScene):
   
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxTrans", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".tx"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
       if(cmds.checkBoxGrp("chkBoxTrans", query = True, v2 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".ty"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
       if(cmds.checkBoxGrp("chkBoxTrans", query = True, v3 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".tz"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
         
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxRot", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".rx"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
       if(cmds.checkBoxGrp("chkBoxRot", query = True, v2 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".ry"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
       if(cmds.checkBoxGrp("chkBoxRot", query = True, v3 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".rz"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
         
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxScale", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".sx"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
       if(cmds.checkBoxGrp("chkBoxScale", query = True, v2 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".sy"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
       if(cmds.checkBoxGrp("chkBoxScale", query = True, v3 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".sz"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);
         
     for i, sel in enumerate(mmSelectedInScene):
       if(cmds.checkBoxGrp("chkBoxVis", query = True, v1 = True) == 1):
         mmSelected = mmSelectedInScene[i] + ".v"
         cmds.setAttr(mmSelected, lock=False, channelBox=True)
         cmds.setAttr(mmSelected, keyable=True);

'''Function: Toggles all checkboxes either on or off, calls secondary function'''
def selectAllToggle(*args):
   boolValTest = checkChkBoxGrps()
   if(boolValTest==0):
     cmds.checkBoxGrp("chkBoxTrans", e = True, v1=0)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v2=0)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v3=0)
     
     cmds.checkBoxGrp("chkBoxRot", e = True, v1=0)
     cmds.checkBoxGrp("chkBoxRot", e = True, v2=0)
     cmds.checkBoxGrp("chkBoxRot", e = True, v3=0)
     
     cmds.checkBoxGrp("chkBoxScale", e = True, v1=0)
     cmds.checkBoxGrp("chkBoxScale", e = True, v2=0)
     cmds.checkBoxGrp("chkBoxScale", e = True, v3=0)
     
     cmds.checkBoxGrp("chkBoxVis", e = True, v1=0);
   else:
     cmds.checkBoxGrp("chkBoxTrans", e = True, v1=1)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v2=1)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v3=1)
     
     cmds.checkBoxGrp("chkBoxRot", e = True, v1=1)
     cmds.checkBoxGrp("chkBoxRot", e = True, v2=1)
     cmds.checkBoxGrp("chkBoxRot", e = True, v3=1)
     
     cmds.checkBoxGrp("chkBoxScale", e = True, v1=1)
     cmds.checkBoxGrp("chkBoxScale", e = True, v2=1)
     cmds.checkBoxGrp("chkBoxScale", e = True, v3=1)
     
     cmds.checkBoxGrp("chkBoxVis", e = True, v1=1);
     
'''Function: Checks if any check boxes are currently selected, returns a boolean'''
def checkChkBoxGrps(*args):
   checkBool = 1
   if(cmds.checkBoxGrp("chkBoxTrans", q = True, v1=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxTrans", q = True, v2=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxTrans", q = True, v3=1)):
     checkBool = 0;
     
   if(cmds.checkBoxGrp("chkBoxRot", q = True, v1=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxRot", q = True, v2=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxRot", q = True, v3=1)):
     checkBool = 0;
     
   if(cmds.checkBoxGrp("chkBoxScale", q = True, v1=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxScale", q = True, v2=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxScale", q = True, v3=1)):
     checkBool = 0;
     
   if(cmds.checkBoxGrp("chkBoxVis", q = True, v1=1)):
     checkBool = 0;
   
   return checkBool;

'''Function: Selects or Deselects all Translate check boxes'''
def selectAllTransToggle(*args):
   boolValTest = checkTransChkBoxGrps()
   if(boolValTest==0):
     cmds.checkBoxGrp("chkBoxTrans", e = True, v1=0)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v2=0)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v3=0)
   
   else:
     cmds.checkBoxGrp("chkBoxTrans", e = True, v1=1)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v2=1)
     cmds.checkBoxGrp("chkBoxTrans", e = True, v3=1);
     
'''Function: Selects or Deselects all Rotation check boxes'''
def selectAllRotToggle(*args):
   boolValTest = checkRotChkBoxGrps()
   if(boolValTest==0):
     cmds.checkBoxGrp("chkBoxRot", e = True, v1=0)
     cmds.checkBoxGrp("chkBoxRot", e = True, v2=0)
     cmds.checkBoxGrp("chkBoxRot", e = True, v3=0)
   
   else:
     cmds.checkBoxGrp("chkBoxRot", e = True, v1=1)
     cmds.checkBoxGrp("chkBoxRot", e = True, v2=1)
     cmds.checkBoxGrp("chkBoxRot", e = True, v3=1);
     
'''Function: Selects or Deselects all Scale check boxes'''
def selectAllScaleToggle(*args):
   boolValTest = checkScaleChkBoxGrps()
   if(boolValTest==0):
     cmds.checkBoxGrp("chkBoxScale", e = True, v1=0)
     cmds.checkBoxGrp("chkBoxScale", e = True, v2=0)
     cmds.checkBoxGrp("chkBoxScale", e = True, v3=0)
   
   else:
     cmds.checkBoxGrp("chkBoxScale", e = True, v1=1)
     cmds.checkBoxGrp("chkBoxScale", e = True, v2=1)
     cmds.checkBoxGrp("chkBoxScale", e = True, v3=1);
   
'''Function: Checks if any Translate check boxes are currently selected, returns a boolean'''
def checkTransChkBoxGrps(*args):
   checkBool = 1
   if(cmds.checkBoxGrp("chkBoxTrans", q = True, v1=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxTrans", q = True, v2=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxTrans", q = True, v3=1)):
     checkBool = 0;
     
   return checkBool;
   
'''Function: Checks if any Rotation check boxes are currently selected, returns a boolean'''
def checkRotChkBoxGrps(*args):
   checkBool = 1
   if(cmds.checkBoxGrp("chkBoxRot", q = True, v1=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxRot", q = True, v2=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxRot", q = True, v3=1)):
     checkBool = 0;
     
   return checkBool;
   
'''Function: Checks if any Scale check boxes are currently selected, returns a boolean'''
def checkScaleChkBoxGrps(*args):
   checkBool = 1
   if(cmds.checkBoxGrp("chkBoxScale", q = True, v1=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxScale", q = True, v2=1)):
     checkBool = 0;
   if(cmds.checkBoxGrp("chkBoxScale", q = True, v3=1)):
     checkBool = 0;
     
   return checkBool;

'''Function: Changes any selected object's Display Type to Reference and turns on Override'''
def refDisplayType(*args):
   mmSelectedInScene = cmds.ls (sl=1)
   #print mmSelectedInScene
   if(mmSelectedInScene):

     for i, sel in enumerate(mmSelectedInScene):
       mmSelected = mmSelectedInScene[i] + ".overrideEnabled"
       cmds.setAttr(mmSelected, 1)
       mmSelected = mmSelectedInScene[i] + ".overrideDisplayType"
       cmds.setAttr(mmSelected, 2);
       #WARNING ** -> if shape nodes have ".overrideEnabled" active, then they will still
       #                  be selectable in display windows
     
   else:
     print "Nothing Selected";

'''Function: Changes any selected object's Display Type to Normal   and turns off Override  '''
def normDisplayType(*args):
   mmSelectedInScene = cmds.ls (sl=1)
   #print mmSelectedInScene
   if(mmSelectedInScene):

     for i, sel in enumerate(mmSelectedInScene):
       mmSelected = mmSelectedInScene[i] + ".overrideDisplayType"
       cmds.setAttr(mmSelected, 0)
       mmSelected = mmSelectedInScene[i] + ".overrideEnabled"
       cmds.setAttr(mmSelected, 0);
       #WARNING ** -> if shape nodes have ".overrideEnabled" active, then they will still
       #                  be selectable in display windows      
   else:
     print "Nothing Selected";

'''Function: Changes any selected object's Color to a chosen Color'''
def changeColor( mmColorDesired = False, *args):
   mmSelectedInScene = cmds.ls (sl=1)
   if(mmSelectedInScene):
      if( mmColorDesired ):
         if( mmColorDesired < 0):
            print "negative number passed in for MMOF.changeColor, using zero instead."
            mmColorDesired = 0
         for i, sel in enumerate(mmSelectedInScene):
            mmSelected = mmSelectedInScene[i] + ".overrideEnabled"
            cmds.setAttr(mmSelected, 1)
            mmSelected = mmSelectedInScene[i] + ".overrideColor"
            cmds.setAttr(mmSelected, mmColorDesired);
            #WARNING ** -> if shape nodes have ".overrideEnabled" active, then they will still
            #                 have their selected color


      else:
         selectedColorVal = cmds.colorIndexSliderGrp("colorField", q = 1, v = 1) -1
         if( selectedColorVal < 0):
            print "negative number passed in for MMOF.changeColor, using zero instead."
            selectedColorVal = 0
         for i, sel in enumerate(mmSelectedInScene):
            mmSelected = mmSelectedInScene[i] + ".overrideEnabled"
            cmds.setAttr(mmSelected, 1)
            mmSelected = mmSelectedInScene[i] + ".overrideColor"
            cmds.setAttr(mmSelected, selectedColorVal);
            #WARNING ** -> if shape nodes have ".overrideEnabled" active, then they will still
            #                 have their selected color

   else:
     print "Nothing Selected"
      
'''Function: Returns the numerical value (in terms of Maya's color scheme) of the color of the first object selected'''
def mmGetColor( mmObjectWeWantColorFrom = None, *args ):
   if ( mmObjectWeWantColorFrom == None ):
      mmObjectWeWantColorFrom = cmds.ls (sl=1)
      if ( mmObjectWeWantColorFrom != [] ):
         mmObjectWeWantColorFrom = mmObjectWeWantColorFrom[0]

   if ( mmObjectWeWantColorFrom != [] and mmObjectWeWantColorFrom != None ):
      mmSelected = mmObjectWeWantColorFrom + ".overrideColor"
      mmColorLookingFor = cmds.getAttr(mmSelected);
      return mmColorLookingFor
   else:
      print "Nothing selected for mmOF.mmGetColor to pull from"
      return None

'''Function: Adds as a prefix any typed text onto the name of all selected objects'''
def mmNameAddPrefix(*args):
   mmSelectedInScene = cmds.ls (sl=1)
   #print mmSelectedInScene
   mmTextAddVal = cmds.textFieldButtonGrp("massRenameField_Prefix", q = 1, tx = 1)
     
   if(mmSelectedInScene):

     for i, sel in enumerate(mmSelectedInScene):
       mmSelected = mmTextAddVal + sel
       cmds.rename(sel, mmSelected);  
   else:
     print "Nothing Selected";
   
'''Function: Adds as a suffix any typed text onto the name of all selected objects'''
def mmNameAddSuffix(*args):
   mmSelectedInScene = cmds.ls (sl=1)
   #print mmSelectedInScene
   mmTextAddVal = cmds.textFieldButtonGrp("massRenameField_Suffix", q = 1, tx = 1)
     
   if(mmSelectedInScene):

     for i, sel in enumerate(mmSelectedInScene):
       mmSelected = sel + mmTextAddVal
       cmds.rename(sel, mmSelected);  
   else:
     print "Nothing Selected";
   
'''Functions: Icon Creations'''
def createCube(*args):
   cmds.curve( d= 1, p=[(-0.5, 0.5, 12.5), (-0.5, 0.5, 11.5), (0.5, 0.5, 11.5),
     (0.5, 0.5, 12.5), (0.5, -0.5, 12.5), (-0.5, -0.5, 12.5), (-0.5, 0.5, 12.5),
     (0.5, 0.5, 12.5), (0.5, -0.5, 12.5), (0.5, -0.5, 11.5), (0.5, 0.5, 11.5), (-0.5, 0.5, 11.5),
     (-0.5, -0.5, 11.5), (0.5, -0.5, 11.5), (0.5, -0.5, 12.5), (-0.5, -0.5, 12.5), (-0.5, -0.5, 11.5)],
     k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16))
   cmds.CenterPivot()   
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   renamedIcon = cmds.rename("box_icon")
   
   return(renamedIcon)

def createFoot(*args):

   mel.eval("curve -d 3 -p -0.408749 0 -0.293952 -p -0.35022 0.248755 -0.293952 -p -0.158199 0.473507 -0.293952 -p 0.10583 0.53024 -0.293952 -p 0.40259 0.528058 -0.293952 -p 0.614249 0.375314 -0.293952 -p 0.679711 0.209478 -0.293952 -p 0.656928 0 -0.306107 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 5 -k 5 ;")
   footPieceA = cmds.rename("foot_pieceA")
   mel.eval("curve -d 3 -p 0.621611 0 -0.455631 -p 0.589066 0 -0.533739 -p 0.62812 0 -0.631375 -p 0.725755 0 -0.670429 -p 0.797354 0 -0.618356 -p 0.777827 0 -0.507703 -p 0.712737 0 -0.436104 -p 0.621611 0 -0.455631 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 5 -k 5 ;")
   footPieceB = cmds.rename("foot_pieceB")
   mel.eval("curve -d 3 -p 0.406813 0 -0.618356 -p 0.354741 0 -0.735519 -p 0.419831 0 -0.852681 -p 0.556521 0 -0.833154 -p 0.615102 0 -0.709483 -p 0.523976 0 -0.59232 -p 0.406813 0 -0.618356 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 4 -k 4 ;")
   footPieceC = cmds.rename("foot_pieceC")
   mel.eval("curve -d 3 -p 0.185507 0 -0.676938 -p 0.10089 0 -0.735519 -p 0.0878717 0 -0.878717 -p 0.152962 0 -0.976352 -p 0.270124 0 -0.963334 -p 0.335214 0 -0.85919 -p 0.315687 0 -0.72901 -p 0.185507 0 -0.676938 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 5 -k 5 ;")
   footPieceD = cmds.rename("foot_pieceD")
   mel.eval("curve -d 3 -p -0.0488176 0 -0.689956 -p -0.152962 0 -0.689956 -p -0.211543 0 -0.7941 -p -0.185507 0 -0.92428 -p -0.10089 0 -0.956825 -p 0.0227816 0 -0.885226 -p 0.0292906 0 -0.781082 -p -0.0488176 0 -0.689956 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 5 -k 5 ;")
   footPieceE = cmds.rename("foot_pieceE")
   mel.eval("curve -d 3 -p -0.387286 0 -0.540248 -p -0.517467 0 -0.488176 -p -0.673683 0 -0.52723 -p -0.777827 0 -0.644393 -p -0.797354 0 -0.846172 -p -0.69321 0 -0.976352 -p -0.510958 0 -0.995879 -p -0.36125 0 -0.885226 -p -0.309178 0 -0.748537 -p -0.315687 0 -0.618356 -p -0.387286 0 -0.540248 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 8 -k 8 ;")
   footPieceF = cmds.rename("foot_pieceF")
   mel.eval("curve -d 3 -p -0.257106 0 0.0520721 -p -0.380777 0 -0.019527 -p -0.426341 0 -0.169234 -p -0.406813 0 -0.364505 -p -0.289651 0 -0.540248 -p -0.0813627 0 -0.624865 -p 0.159471 0 -0.637884 -p 0.419831 0 -0.566284 -p 0.62812 0 -0.403559 -p 0.712737 0 -0.169234 -p 0.732264 0 0.149707 -p 0.673683 0 0.507703 -p 0.465395 0 0.92428 -p 0.23107 0 1.034933 -p 0.0162725 0 1.002388 -p -0.0943807 0 0.891735 -p -0.0748537 0 0.748537 -p 0.0423086 0 0.579302 -p 0.133435 0 0.39705 -p 0.126926 0 0.240834 -p 0.00976352 0 0.123671 -p -0.120417 0 0.0650902 -p -0.257106 0 0.0520721 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 20 -k 20 ;")
   footPieceG = cmds.rename("foot_pieceG")
   footGroup = cmds.group(em=1)
   
   cmds.select( (footPieceA+"Shape"), r=True )
   cmds.select( (footPieceB+"Shape"), add=True )
   cmds.select( (footPieceC+"Shape"), add=True )
   cmds.select( (footPieceD+"Shape"), add=True )
   cmds.select( (footPieceE+"Shape"), add=True )
   cmds.select( (footPieceF+"Shape"), add=True )
   cmds.select( (footPieceG+"Shape"), add=True )
   cmds.select( footGroup, add=True )
   
   cmds.parent( r = 1, s = 1)
   renamedIcon = cmds.rename(footGroup, "foot_icon#")
   cmds.select(cl = 1)
   cmds.select(renamedIcon)
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   cmds.select( (footPieceA), r=True )
   cmds.select( (footPieceB), add=True )
   cmds.select( (footPieceC), add=True )
   cmds.select( (footPieceD), add=True )
   cmds.select( (footPieceE), add=True )
   cmds.select( (footPieceF), add=True )
   cmds.select( (footPieceG), add=True )
   cmds.delete()
   
   cmds.rename((footPieceA+"Shape"), renamedIcon+"_piece#")
   cmds.rename((footPieceB+"Shape"), renamedIcon+"_piece#")
   cmds.rename((footPieceC+"Shape"), renamedIcon+"_piece#")
   cmds.rename((footPieceD+"Shape"), renamedIcon+"_piece#")
   cmds.rename((footPieceE+"Shape"), renamedIcon+"_piece#")
   cmds.rename((footPieceF+"Shape"), renamedIcon+"_piece#")
   cmds.rename((footPieceG+"Shape"), renamedIcon+"_piece#")
   
   cmds.select( renamedIcon, r=True )
   
   cmds.setAttr( renamedIcon+".rotateY", 180)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   
   return(renamedIcon)

def createMoveAll(*args):
   cmds.curve( d= 1, p=[(0, 0, 0), (2, 0, 2), (1, 0, 2), (1, 0, 5), (4, 0, 5), (4, 0, 4), (6, 0, 6), (4, 0, 8),
     (4, 0, 7), (1, 0, 7), (1, 0, 10), (2, 0, 10), (0, 0, 12), (-2, 0, 10), (-1, 0, 10), (-1, 0, 7),
     (-4, 0, 7), (-4, 0, 8), (-6, 0, 6), (-4, 0, 4), (-4, 0, 5), (-1, 0, 5), (-1, 0, 2), (-2, 0, 2), (0, 0, 0)],
     k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24))

   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   newName = cmds.rename("moveAll_icon")

   '''
   cmds.select( cl = 1)
   cmds.select( newName + ".cv[6]", r = True )
   cmds.select( newName + ".cv[0]", newName + ".cv[24]", add = True)
   cmds.select( newName + ".cv[18]", add = True )
   cmds.select( newName + ".cv[12]", add = True )
   cmds.move( 0, 3.445143, 0, r = True)

   cmds.select( cl = 1)
   cmds.select( newName )
   '''

   return newName

def createCog(*args):
   cmds.curve( d= 1, p=[(0, 0, -5), (0.58013, 0, -4.964784), (0.559121, 0, -3.959155), (1.443657, 0, -3.72549),
     (1.933934, 0, -4.604603), (2.798358, 0, -4.139846), (2.350073, 0, -3.234546), (3.017073, 0, -2.62556),
     (3.876209, 0, -3.156503), (4.406032, 0, -2.35295), (3.63105, 0, -1.667133), (3.893341, 0, -0.9039),
     (4.944482, 0, -0.728879), (4.991915, 0, 0.277361), (3.982235, 0, 0.368277), (3.78127, 0, 1.291166),
     (4.699759, 0, 1.690093), (4.267555, 0, 2.597503), (3.29759, 0, 2.259881), (2.736533, 0, 2.91728),
     (3.100468, 0, 3.920808), (2.388726, 0, 4.386872), (1.612193, 0, 3.655715), (0.675088, 0, 3.940504),
     (0.622824, 0, 4.959428), (-0.531772, 0, 4.970395), (-0.642305, 0, 3.946132), (-1.618398, 0, 3.652977),
     (-2.159791, 0, 4.503331), (-2.95049, 0, 4.033868), (-2.523477, 0, 3.10236), (-3.049579, 0, 2.587483),
     (-3.956667, 0, 3.05417), (-4.400291, 0, 2.36374), (-3.631789, 0, 1.665517), (-3.898477, 0, 0.881911),
     (-4.959428, 0, 0.622824), (-4.981753, 0, -0.417165), (-3.931264, 0, -0.725687), (-3.717599, 0, -1.463823),
     (-4.57972, 0, -1.992198), (-4.114544, 0, -2.835786), (-3.24243, 0, -2.339079), (-2.578331, 0, -3.057267),
     (-3.122714, 0, -3.903262), (-2.168001, 0, -4.499401), (-1.731254, 0, -3.601029), (-0.783961, 0, -3.919789),
     (-0.742662, 0, -4.942367), (0, 0, -5)], k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
     18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
     44, 45, 46, 47, 48, 49))
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   renamedIcon = cmds.rename("cog_icon")
   
   return(renamedIcon)

def createHand(*args):  
   cmds.curve( d= 1, p=[(0.518946, 0, 0.674713), (-0.108459, 0, 0.709895), (-0.389911, 0, 0.498806),
     (-0.601, 0, 0.334625), (-0.853135, 0, 0.217353), (-0.794499, 0, 0.105945), (-0.554091, 0, 0.188035),
     (-0.343002, 0, 0.299444), (-0.167094, 0, 0.141127), ( -0.190549, 0, -0.0758261),
     (-0.413365, 0, -0.732548), (-0.296093, 0, -0.78532), (-0.0498227, 0, -0.16378),
     (0.0498584, 0, -0.181371), (-0.0380955, 0, -0.879138), (0.102631, 0, -0.902592),
     (0.184721, 0, -0.198961), (0.266811, 0, -0.210689), (0.401674, 0, -0.832229), (0.513082, 0, -0.76773),
     (0.413401, 0, -0.146189), (0.46031, 0, -0.0992804), (0.741762, 0, -0.53905), (0.829716, 0, -0.480414),
     (0.601036, 0, 0.000400601), (0.601036, 0, 0.416715), (0.601036, 0, 0.416715), (0.518946, 0, 0.674713)],
     k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27))
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.rotate(0,180,0)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   renamedIcon = cmds.rename("hand_icon")
   
   return(renamedIcon)

def createL(*args):     
   cmds.curve( d= 1, p=[(-0.598724, 0, -0.218159), (-0.594003, 0, -0.174886), (-0.546795, 0, -0.174886),
     (-0.537354, 0, 0.239752), (-0.591643, 0, 0.244473), (-0.591643, 0, 0.28932), (-0.174644, 0, 0.273584),
     (-0.182512, 0, 0.144551), (-0.2368, 0, 0.144551), (-0.228932, 0, 0.209854), (-0.459462, 0, 0.231098),
     (-0.468866, 0, -0.168579), (-0.424056, 0, -0.170165), (-0.422483, 0, -0.211078), (-0.598724, 0, -0.218159)],
     k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.rotate(0,180,0)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   renamedIcon = cmds.rename("lf_icon")
   
   return(renamedIcon)

def createR(*args):  
   cmds.curve( d= 1, p=[(0.453676, 0, -0.267727), (0.45761, 0, -0.211078), (0.563827, 0, -0.224454),
     (0.616542, 0, 0.233458), (0.561467, 0, 0.226377), (0.550452, 0, 0.281452), (0.762885, 0, 0.298762),
     (0.758164, 0, 0.246834), (0.71253, 0, 0.235819), (0.691287, 0, 0.0674454), (0.766032, 0, 0.0674454),
     (0.869101, 0, 0.253915), (0.825041, 0, 0.261783), (0.845498, 0, 0.323939), (1.011972, 0, 0.283484),
     (1.005216, 0, 0.216149), (0.946954, 0, 0.237269), (0.83999, 0, 0.0564304), (0.937495, 0, -0.0103932),
     (0.966927, 0, -0.0574617), (0.96973, 0, -0.15368), (0.931196, 0, -0.226386), (0.847008, 0, -0.273203),
     (0.732289, 0, -0.29346), (0.453676, 0, -0.267727), (0.732289, 0, -0.29346), (0.745019, 0, -0.233863),
     (0.652734, 0, -0.226814), (0.684206, 0, 0.00607583), (0.780159, 0, 0), (0.880385, 0, -0.0366403),
     (0.906101, 0, -0.0855511), (0.906532, 0, -0.151029), (0.873302, 0, -0.196365), (0.827088, 0, -0.221542),
     (0.741902, 0, -0.233807)], k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
     21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35))
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.rotate(0,180,0)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   renamedIcon = cmds.rename("rt_icon")
   
   return(renamedIcon)
   
def createBelt(*args):
   cmds.curve( d= 3, p=[(0.5, 0.5, 1.198716), (1.024819, 0.5, 1.014741), (1.452612, 0.5, 0.702568),
     (1.733495, 0.5, 0.203858), (1.706282, 0.5, -0.296401), (1.289212, 0.5, -0.849613),
     (0.610753, 0.5, -1.170487), (-0.091476, 0.5, -1.248073), (-0.879592, 0.5, -1.080841),
     (-1.35013, 0.5, -0.800062), (-1.671924, 0.5, -0.381854), (-1.743553, 0.5, 0.156244),
     (-1.527344, 0.5, 0.616448), (-1.13066, 0.5, 0.956748), (-0.626579, 0.5, 1.166239), (-0.5, 0.5, 1.198716),
     (-0.490754, 0.5, 1.198716), (0.482888, 0.5, 1.198716), (0.5, 0.5, 1.198716), (0.5, 0.497621, 1.198716),
     (0.5, 0.492111, 1.198716), (0.5, -0.48945, 1.198716), (0.5, -0.499202, 1.198716), (0.5, -0.5, 1.198716),
     (0.572163, -0.5, 1.180349), (0.996121, -0.5, 1.028949), (1.413168, -0.5, 0.742489),
     (1.740084, -0.5, 0.174141), (1.60933, -0.5, -0.499341), (0.943364, -0.5, -1.05355),
     (0.211519, -0.5, -1.240387), (-0.600027, -0.5, -1.173299), (-1.227527, -0.5, -0.894663),
     (-1.707694, -0.5, -0.292333), (-1.644823, -0.5, 0.437031), (-1.143393, -0.5, 0.94912),
     (-0.649274, -0.5, 1.159934), (-0.502014, -0.5, 1.196505), (-0.5, -0.5, 1.198716),
     (-0.5, -0.499509, 1.198716), (-0.5, -0.497879, 1.198716), (-0.5, 0.494062, 1.198716),
     (-0.5, 0.5, 1.198716), (-0.498386, 0.5, 1.198716), (-0.495647, 0.5, 1.198716),
     (-0.360866, 0.360866, 1.198716), (-0.360866, 0.360498, 1.198716), (-0.360866, 0.360057, 1.198716),
     (-0.360866, -0.35549, 1.198716), (-0.360866, -0.35549, 1.198716), (-0.360866, -0.357694, 1.198716),
     (-0.360866, -0.360866, 1.198716), (-0.359666, -0.360866, 1.198716), (-0.356983, -0.360866, 1.198716),
     (0.348641, -0.360866, 1.198716), (0.358462, -0.360866, 1.198716), (0.360866, -0.360866, 1.198716),
     (0.360866, -0.359699, 1.198716), (0.360866, -0.356584, 1.198716), (0.360866, 0.346595, 1.198716),
     (0.360866, 0.356102, 1.198716), (0.360866, 0.360866, 1.198716), (0.360095, 0.360866, 1.198716),
     (0.354955, 0.360866, 1.198716), (-0.338403, 0.360866, 1.198716), (-0.358942, 0.360866, 1.198716),
     (-0.360866, 0.360866, 1.198716), (-0.5, 0.5, 1.198716), (-0.50018, 0.5, 1.1968), (-0.49877, 0.5, 1.198716),
     (0.495585, 0.499737, 1.198716), (0.498225, 0.5, 1.198716), (0.5, 0.499723, 1.198716),
     (0.5, 0.498133, 1.198716), (0.5, 0.496776, 1.198716), (0.5, -0.493508, 1.198716), (0.5, -0.495123, 1.198716),
     (0.5, -0.496923, 1.198716), (0.5, -0.5, 1.198716), (0.499454, -0.5, 1.198716), (0.498349, -0.5, 1.198716),
     (-0.5, -0.5, 1.198716)], k = (0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
     21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
     48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
     75, 76, 77, 78, 79, 79, 79))
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   renamedIcon = cmds.rename("waist_icon")
   
   return(renamedIcon)
   
'''Function: Creates multiple pin icons which can be used to move fingers'''
def createPin(*args):
   mel.eval("curve -d 1 -p -0.5 0 0 -p -0.412917 0 0.0860787 -p -0.326679 0 0 -p -0.413158 0 -0.0864794 -p -0.5 0 0 -p -0.413521 -0.0864794 0 -p -0.326679 0 0 -p -0.413517 0.0858017 -0.000579073 -p -0.5 0 0 -p 0.5 0 0 -p 0.413902 0.0859236 0 -p 0.328244 0 0 -p 0.414931 -0.0874093 0 -p 0.5 0 0 -p 0.413081 0 0.0860258 -p 0.328237 0 0 -p 0.413987 0 -0.0855441 -p 0.5 0 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 ;")
   pinPiece1 = cmds.rename("pin_pieceA")
   mel.eval("curve -d 1 -p 0.414931 -0.0874093 0 -p 0.413081 0 0.0860258 -p 0.413902 0.0859236 0 -p 0.414603 0 -0.0849315 -p 0.414931 -0.0874093 0 -k 0 -k 1 -k 2 -k 3 -k 4 ;")
   pinPiece2 = cmds.rename("pin_pieceB")
   mel.eval("curve -d 1 -p -0.413521 -0.0864794 0 -p -0.412917 0 0.0860787 -p -0.413517 0.0858017 -0.000579073 -p -0.413158 0 -0.0864794 -p -0.413521 -0.0864794 0 -k 0 -k 1 -k 2 -k 3 -k 4 ;")
   pinPiece3 = cmds.rename("pin_pieceC")
   pinGroup = cmds.group(em=1)
   cmds.select( (pinPiece1+"Shape"), r=True )
   cmds.select( (pinPiece2+"Shape"), add=True )
   cmds.select( (pinPiece3+"Shape"), add=True )
   cmds.select( pinGroup, add=True )
   cmds.parent( r = 1, s = 1)
   renamedIcon = cmds.rename(pinGroup, "pin_icon#")
   cmds.select(cl = 1)
   cmds.select(renamedIcon)
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.rotate(0,0,90)
   cmds.scale(5,5,5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)
   cmds.select( pinPiece1, r=True )
   cmds.select( pinPiece2, add=True )
   cmds.select( pinPiece3, add=True )
   cmds.delete()
   cmds.select( renamedIcon, r=True )
   cmds.rename((pinPiece1+"Shape"), "pin_piece#")
   cmds.rename((pinPiece2+"Shape"), "pin_piece#")
   cmds.rename((pinPiece3+"Shape"), "pin_piece#")
   
   return(renamedIcon)

'''Function: Creates multiple pin icons which can be used to move fingers'''
def createOrb(*args):

   cmds.circle(  )
   mmCircle1 = cmds.rename("orb_pieceA")
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   cmds.select( cl = 1 )

   cmds.circle(  )
   cmds.rotate(90,0,0)
   mmCircle2 = cmds.rename("orb_pieceB")
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   cmds.select( cl = 1 )

   cmds.circle(  )
   cmds.rotate(0,90,0)
   mmCircle3 = cmds.rename("orb_pieceC")
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   orbGroup = cmds.group(em=1)

   cmds.select( cl = 1 )

   #Grab various pieces and parent them into a group
   cmds.select( (mmCircle1+"Shape"), r=True )
   cmds.select( (mmCircle2+"Shape"), add=True )
   cmds.select( (mmCircle3+"Shape"), add=True )

   cmds.select( orbGroup, add=True )

   cmds.parent( r = 1, s = 1)


   renamedIcon = cmds.rename(orbGroup, "orb_icon#")
   cmds.select(cl = 1)
   cmds.select(renamedIcon)
   cmds.CenterPivot()
   cmds.move(0,0,0, xyz = 1, rpr = 1)
   cmds.scale(2.5,2.5,2.5)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   cmds.select( cl = 1 )

   cmds.select( mmCircle1, r=True )
   cmds.select( mmCircle2, add=True )
   cmds.select( mmCircle3, add=True )
   cmds.delete()
   cmds.select( renamedIcon, r=True )
   cmds.rename((mmCircle1+"Shape"), "orb_piece#")
   cmds.rename((mmCircle2+"Shape"), "orb_piece#")
   cmds.rename((mmCircle3+"Shape"), "orb_piece#")
   
   return(renamedIcon)

'''Function: Icon Creation - creates an icon around the passed in or selected object'''
def createFitAll( mmMeshObject = False, mmPercentOfSize = 1.1, *args ):

   if ( mmMeshObject == False ):
      mmMeshObject = cmds.ls(sl = 1)
      mmMeshObjectLen = len(mmMeshObject)
      if (mmMeshObjectLen == 0):
         print "Nothing selected for createFitAll function to work."
         return None

      mmMeshObject = mmMeshObject[0]

   cmds.select( mmMeshObject )

   #find the pivot location of the mesh object
   mmMeshObjectPivot = cmds.xform( q = 1, pivots = 1, ws = 1)

   mmPivX = mmMeshObjectPivot[0]
   mmPivY = mmMeshObjectPivot[1]
   mmPivZ = mmMeshObjectPivot[2]

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

   #Find halfway point (i.e. center of object)
   mmXMidPoint = mmXMax - mmXTotal/2
   mmYMidPoint = mmYMax - mmYTotal/2
   mmZMidPoint = mmZMax - mmZTotal/2

   #Find size user wants
   mmNewXTotal = mmXTotal*mmPercentOfSize
   mmNewYTotal = mmYTotal*mmPercentOfSize
   mmNewZTotal = mmZTotal*mmPercentOfSize

   #Create new min and max
   mmXMin = mmXMidPoint - mmNewXTotal/2
   mmXMax = mmXMidPoint + mmNewXTotal/2
   mmYMin = mmYMidPoint - mmNewYTotal/2
   mmYMax = mmYMidPoint + mmNewYTotal/2
   mmZMin = mmZMidPoint - mmNewZTotal/2
   mmZMax = mmZMidPoint + mmNewZTotal/2

   #Create Curve
   mmCreatedCurve = cmds.curve( d= 1, p=[(mmXMin, mmYMin, mmZMin), (mmXMax, mmYMin, mmZMin), (mmXMax, mmYMax, mmZMin), (mmXMin, mmYMax, mmZMin), (mmXMin, mmYMin, mmZMin), 
      (mmXMin, mmYMin, mmZMax), (mmXMax, mmYMin, mmZMax), (mmXMax, mmYMax, mmZMax), (mmXMin, mmYMax, mmZMax), (mmXMin, mmYMin, mmZMax),
      (mmXMax, mmYMin, mmZMax), (mmXMax, mmYMin, mmZMin), (mmXMax, mmYMax, mmZMin), (mmXMax, mmYMax, mmZMax), (mmXMin, mmYMax, mmZMax), (mmXMin, mmYMax, mmZMin) ],
      k = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ))

   mmCreatedCurve = cmds.rename("fitall_icon")

   #Move the newly created nurbs curve to the meshobject
   mmShapeNode = cmds.listRelatives()[0]

   #Try pulling out the shape nodes first, then putting them back later
   #Create a new node, move into place, freeze transforms, swap in the shape, move & freeze the other node, swap back.
   mmTrashGroup = cmds.group(em = 1)
   cmds.select( mmTrashGroup )
   cmds.move( mmPivX, mmPivY, mmPivZ, xyz = 1, rpr = 1)

   cmds.select(mmTrashGroup)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   cmds.select( (mmShapeNode) )
   cmds.select( mmTrashGroup, add = 1 )
   cmds.parent( r = 1, s = 1 )

   #Move the control transform
   cmds.select(mmCreatedCurve)
   cmds.move( mmPivX, mmPivY, mmPivZ, xyz = 1, rpr = 1)

   cmds.select(mmCreatedCurve)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   #Reparent shape node
   cmds.select( (mmShapeNode) )
   cmds.select( mmCreatedCurve, add = 1 )
   cmds.parent( r = 1, s = 1 )

   cmds.delete( mmTrashGroup )

   cmds.select(cl = 1)

   return(mmCreatedCurve)

'''Function: Icon Creation - creates an icon around the passed in or selected object'''
def createText( mmTextToCreate = "bob", mmTextScaleValue = [1,1,1], *args ):

   mmCurveList = []

   #Create text of name passed in
   mmTextGroupNode = mel.eval('textCurves -ch 0 -f "Tahoma|w400|h-11" -t "' + mmTextToCreate + '";')

   # cmds.scale( 1.0*mmTextScaleValue[0], mmTextScaleValue[1], mmTextScaleValue[2] )
   cmds.scale( 1.0*mmTextScaleValue[2]/10, 1.0*mmTextScaleValue[1]/10, 1.0*mmTextScaleValue[0]/10 )

   mmGroupNodes = cmds.listRelatives(c = 1)

   for mmGroup in mmGroupNodes:
      cmds.select(mmGroup)

      mmCurve = cmds.listRelatives(c = 1)

      mmCurveList.append(mmCurve)

      cmds.parent( mmCurve, w = 1 )

   cmds.delete( mmTextGroupNode )

   for mmCurve in mmCurveList:
      cmds.select(mmCurve, add = 1 )

   mmTextIcon = combineNurbCurves()

   #set to world
   mmGWT.main()
   cmds.move(0,0,0)

   cmds.select(mmTextIcon)

   return mmTextIcon

'''Function: Icon Creation - This creates a squatish box icon with the passed in text on two sides.'''
def createTextBox( mmTextToCreate = "bob", mmObjectToScaleTo = None, mmRotationalOffset = [0,0,0], mmScaleValue = [1,1,1], mmTextScaleValue = [1,1,1], mmShapeName = "text", *args ):

   if ( mmTextToCreate == "bob" ):

      mmTextToCreate = cmds.textFieldButtonGrp( "createTextBox_TextField", q = 1, text = True ) 

   '''
   #Demo for creation:
   #createTextBox( mmTextToCreate = "bob", mmObjectToScaleTo = None, mmRotationalOffset = [0,0,0], mmScaleValue = [1,1,1], mmTextScaleValue = [1,1,1], mmShapeName = "box" )
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
      # text
   '''

   mmTextIcon = createText(mmTextToCreate, mmTextScaleValue)

   if (mmShapeName != "text"):

      cmds.move(0,0,0.5)

      cmds.duplicate()

      cmds.rotate(0, 180, 0)

      cmds.move(0,0,-0.5)

      cmds.select(mmTextIcon, add = 1)

      mmInterimTextIcon = combineNurbCurves()

      #Create any shape desired
      mmNewBoxIcon = mmCreateDesiredNurbsIcon( mmShapeName )

      if (mmShapeName == "circle"):
         cmds.scale(0.5,0.5,0.5)

      cmds.select( mmInterimTextIcon, add = 1 )

      mmFinalIcon = combineNurbCurves()

   else:
      mmFinalIcon = mmTextIcon

   cmds.rotate( 0, 90, 0 )

   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   cmds.rotate( mmRotationalOffset[0], mmRotationalOffset[1], mmRotationalOffset[2] )
   
   cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)
   
   cmds.scale( mmScaleValue[0], mmScaleValue[1], mmScaleValue[2] )

   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   #If an object is passed in for scale, then get info from it and apply changes.
   if ( mmObjectToScaleTo != None ):
      mmObjectBoundingInfo = mmRF.mmGrabBoundingBoxInfo( [mmObjectToScaleTo] )

    #mmGrabBoundingBoxInfo returns mmDictOfBoundingBoxLists with this information:
    # [
    #     "overallMin":       [X, Y, Z],
    #     "overallMidPoint":  [X, Y, Z],
    #     "overallMax":       [X, Y, Z],
    #     "overallTotal":     [X, Y, Z],
    #     "overallPiv":       [X, Y, Z]
    # ]

      #Fix up scale to match the object passed in, adjust rotations if desired.
      #? This doesn't quite work right.. not sure why.  Prolly order of operations.
      #?     Its because of the pivots being unknown.  Don't care enough to fix atm, we can just manually adjust if it bothers us.
      cmds.select( mmFinalIcon )

      cmds.scale( mmObjectBoundingInfo["total"][0], mmObjectBoundingInfo["total"][1], mmObjectBoundingInfo["total"][2] )

      cmds.makeIdentity( apply = 1, t = 1, r = 1, s = 1, n = 0)

      mmMoveObject( [mmFinalIcon, mmObjectToScaleTo] )

   cmds.select(mmFinalIcon)

   mmFinalIcon = cmds.rename(mmFinalIcon, "UniqueName_#")

   return mmFinalIcon

'''
This Function takes an input word, creates a nurbs icon based on that word, and then returns the pointer of the newly created icon.
If the word does not have a corresponding icon type, an error is printed out and 'none' is returned.
'''
def mmCreateDesiredNurbsIcon( mmShapeName ):
   #Determine which shape the user wants

   '''
   Possible Shapes:
   box
   belt
   hand
   foot
   moveall
   cog
   left
   right
   pin
   orb
   circle
   fitall
   '''

   if ( mmShapeName == "box" ):
      mmCreatedController = createCube()
   elif ( mmShapeName == "belt" ):
      mmCreatedController = createBelt()
   elif ( mmShapeName == "hand" ):
      mmCreatedController = createHand()
   elif ( mmShapeName == "foot" ):
      mmCreatedController = createFoot()
   elif ( mmShapeName == "moveall" ):
      mmCreatedController = createMoveAll()
   elif ( mmShapeName == "cog" ):
      mmCreatedController = createCog()
   elif ( mmShapeName == "left" ):
      mmCreatedController = createL()
   elif ( mmShapeName == "right" ):
      mmCreatedController = createR()
   elif ( mmShapeName == "pin" ):
      mmCreatedController = createPin()
   elif ( mmShapeName == "orb" ):
      mmCreatedController = createOrb()
   elif ( mmShapeName == "circle" ):
      mmCreatedController = cmds.circle()[0]
      cmds.rotate( '90deg', 0, 0 )
   elif ( mmShapeName == "fitall" ):
      mmCreatedController = createFitAll()
   elif ( mmShapeName == "text" ):
      mmCreatedController = createText()
   else:
      print "Not a supported shape type."
      return None

   return mmCreatedController

"""
This function will combine selected nurb curves into a single new transform with multiple shape nodes inside it.
"""
def combineNurbCurves(*args):
    #Grab label from UI.
    finalLabel = cmds.textFieldButtonGrp("combineNurbsLabel", q = 1, text = 1)
    tempLabel = "bob"
    selectedObjectList = []
    selectedShapesList = []
    newNameShapesList = []
    
    #Grab selected items.
    mmSelectedInScene = cmds.ls(sl=1)
    
    i = 0
    #For every selected object
    while (i<=(len(mmSelectedInScene)-1)):

        #If there is a parent
        if(cmds.listRelatives(mmSelectedInScene[i], p = 1)):
            #then Parent the selected thing to the world (unparent it)
            cmds.parent(mmSelectedInScene[i], w = 1)

        #Freeze transforms
        cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)

        #Grab each thing's name and store it in a list
        transformNodeName = cmds.ls(mmSelectedInScene[i])[0]
        selectedObjectList.append(transformNodeName)

        cmds.select(mmSelectedInScene[i])

        mmListOfChildren = cmds.listRelatives( c = 1 )

        for child in mmListOfChildren:
            selectedShapesList.append(child)

        i+=1

    #Select all shape nodes we found
    cmds.select(cl = 1)

    for shape in selectedShapesList:
        cmds.select( shape, add = 1 )

    #Freeze trans of shape nodes
    #?  Prolly shouldn't need to do this, but just in case I guess.
    cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)
    
    #rename shape nodes
    i = 0
    while (i<=(len(selectedShapesList)-1)):
        shapeNodeName = cmds.rename(selectedShapesList[i], (finalLabel + "_piece#"), ignoreShape = 0)
        
        #Store new names we just created
        if (shapeNodeName):
            newNameShapesList.append(shapeNodeName)
        i+=1
    
    #Create an emptry group/transform node which will be our newly created icon
    workingName = cmds.group(em = 1, n = tempLabel)
    
    #Parent all the shape nodes into the new empty group.
    i = 0
    while (i<=len(newNameShapesList)-1):
        shapeNodeName = cmds.ls(newNameShapesList[i])

        cmds.parent(shapeNodeName, workingName, r = 1, s = 1)
        i+=1
    
    #Delete all the old (now empty) transform nodes.
    i = 0
    while (i<=len(selectedObjectList)-1):
        cmds.delete(selectedObjectList[i])
        i+=1

    workingName = cmds.rename(workingName, finalLabel)

    cmds.select(workingName)

    #Center Pivot
    mel.eval("CenterPivot")

    #Freeze Transforms
    cmds.makeIdentity( apply=1, t = 1, r = 1, s = 1, n = 0)

    return workingName

'''Function: Object Matching to Selection - This function takes your first selection and moves it to your second, then freezes transforms.'''
def mmCallMoveObject( *args ):

   mmMoveObject()

   return None

'''Function: Object Matching to Selection - This function takes your first selection and moves it to your second, then freezes transforms.'''
def mmMoveObject( mmPassedObjectList = None, *args ):

   if mmPassedObjectList is None:
      mmPassedObjectList = cmds.ls(sl = 1)

      if (type(mmPassedObjectList) != type([])):
         print "Invalid selection or passed information to mmOF.mmMoveObject"
         return None

   mmTempParentConst = cmds.parentConstraint(mmPassedObjectList[1], mmPassedObjectList[0], mo = 0)
   cmds.delete(mmTempParentConst)

   cmds.select(mmPassedObjectList[0])
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   return None

'''
This function calls the Group in Place functionality from the UI with default values
'''
def mmCallGroupInPlace( *args ):

    #Grab selected Items
    mmSelectedInScene = cmds.ls( sl = 1 )

    for mmItem in mmSelectedInScene:
        mmCreatedGroup = mmGroupInPlace( mmItem )

    cmds.select( mmCreatedGroup )

'''
This function takes an object passed in, then creates a group on top of it, and passes back the name of that group.
'''
def mmGroupInPlace( mmObjectToGroup = None, mmNameOfPad = "_pad#" ):

   if (mmObjectToGroup == None):
      mmObjectToGroup = cmds.ls(sl = 1)[0]
   cmds.select(cl = 1)

   #Need to add a pad group to the passed object or selection

   #First need to verify that we aren't padding a pad - if we are, just increment (as long as user doesn't want something special)
   mmListChecker = mmObjectToGroup.split("_")

   if ( len(mmListChecker) >= 1 and len(mmListChecker[len(mmListChecker)-1]) > 3 and mmListChecker[len(mmListChecker)-1][0:3] == "pad" and mmNameOfPad == "_pad#" ):
      mmPadName = ""

      i = 0
      while ( i < len(mmListChecker) - 1 ):

         mmPadName += mmListChecker[i] + "_"
         i += 1

      mmPadName += "pad#"

   else:
      mmPadName = mmObjectToGroup + mmNameOfPad

   mmCounter = 1
   while ( cmds.objExists(mmPadName) ):
      mmPadName = mmObjectToGroup + mmNameOfPad + str(mmCounter)
      mmCounter += 1

   mmCreatedPad = cmds.group( em = True )
   mmCreatedPad = cmds.rename( mmCreatedPad, mmPadName )

   # print "mmObjectToGroup", mmObjectToGroup
   # print "mmCreatedPad", mmCreatedPad

   #Parent Constrain in the group (to get the location), then delete the constraint, then parent in the original object
   mmTrashPointConstraint = cmds.pointConstraint( mmObjectToGroup, mmCreatedPad, mo = 0 )
   cmds.delete(mmTrashPointConstraint)

   #Find the current parent
   mmObjectsParent = cmds.listRelatives( mmObjectToGroup, p = 1 )

   if ( mmObjectsParent != None ):
      cmds.parent( mmCreatedPad, mmObjectsParent[0] )

   cmds.select(mmCreatedPad)
   cmds.makeIdentity( apply = True, t = 1 , r = 1 , s = 1 , n = 0, pn = 1)

   cmds.parent( mmObjectToGroup, mmCreatedPad )

   #Set selection to mmCreatedPad - hopefully this doesn't break anything, but it seems more logical.
   cmds.select( mmCreatedPad, r = 1 )

   return mmCreatedPad
