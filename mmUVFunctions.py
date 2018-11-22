"""

Function: mmUVFunctions
Description: This is a collection of functions which help out when UVing in general.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

#Local
import mmOrganizationFunctions
import mmModelingFunctions
import mmRiggingFunctions

######################################
############# DEFINES ################
######################################


  

#Function: Assists in selecting UVs shell
def selectUV(*args):
   cmds.ConvertSelectionToUVs() #converts any selection to UVs
   cmds.SelectUVShell() #selects shell of selected object

#Function: Takes user input of directions they want UV Shell to be moved in and moves them,
#unless they are already in corresponding coordinates
def moveUVCords(*args):
   testList = cmds.polyEditUV(query = 1, v = 1)
   
   if(cmds.radioButtonGrp("uCheckBox", query = 1, sl = 1) == 1):
     if(testList[0] < 0):
       
       cmds.polyEditUVShell(u=1);

     else:
       print "Shell is already in +U";
       
   elif(cmds.radioButtonGrp("uCheckBox", query = 1, sl = 1) == 2):
     if(testList[0] > 0):
       cmds.polyEditUVShell(u=-1);
         
     else:
       print "Shell is already in -U";
   else:
     print "Invalid Values";
       
       
   if(cmds.radioButtonGrp("vCheckBox", query = 1, sl = 1) == 1):
     if(testList[1] < 0):
       cmds.polyEditUVShell(v=1);
     else:
       print "Shell is already in +V";
     
   elif(cmds.radioButtonGrp("vCheckBox", query = 1, sl = 1) == 2):
     if(testList[1] > 0):
     
       cmds.polyEditUVShell(v=-1);
         
     else:
       print "Shell is already in -V";
   
   else:
     print "Invalid Values";
     
#Function: Opens the UV Editor
def uvWindow(*args):
   cmds.TextureViewWindow()
   
#Function: Unfolds UV information according to selected settings
def uvUnfold(*args):
   
   weightSolver_Val = cmds.floatSliderGrp("weightSolver", q = 1, value= 1)
   optimizeToOriginal_Val = cmds.floatSliderGrp("optimizeToOriginal", q = 1, value= 1)
   maxIterations_Val = cmds.intSliderGrp("unfoldMaxIterations", q = 1, value = 1)
   stopThresh_Val = cmds.floatSliderGrp("stopThresh", q = 1, value = 1)
   
   if(cmds.radioButtonGrp("unfoldCheckBox", q = True, sl=1) == 1):
     pinBordBool = 1
     pinUVBool = 0;
   if(cmds.radioButtonGrp("unfoldCheckBox", q = True, sl=1) == 2):
     pinUVBool = 1
     pinBordBool = 0;
   if(cmds.radioButtonGrp("unfoldCheckBox", q = True, sl=1) == 3):
     pinUVBool = 0
     pinBordBool = 0;
   
   cmds.unfold(oa = 0, gb = weightSolver_Val, gmb = optimizeToOriginal_Val,
     i = maxIterations_Val, ss = stopThresh_Val,
     pub = pinBordBool, ps = pinUVBool, us = 0)
   
#Function: Relaxes UV information according to selected settings
def uvRelax(*args):
   maxIterations_Val = cmds.intSliderGrp("relaxMaxIterations", q = 1, value = 1)
   
   if(cmds.radioButtonGrp("relaxCheckBox", q = True, sl=1) == 1):
     pinBordBool = 1
     pinUVBool = 0;
   if(cmds.radioButtonGrp("relaxCheckBox", q = True, sl=1) == 2):
     pinUVBool = 1
     pinBordBool = 0;
   if(cmds.radioButtonGrp("relaxCheckBox", q = True, sl=1) == 3):
     pinUVBool = 0
     pinBordBool = 0;

   cmds.untangleUV(r = "harmonic", pb = pinBordBool, ps = pinUVBool, mri = maxIterations_Val)
   
#Function: Assists in selecting UVs border
def selectUVBorder(*args):
   cmds.ConvertSelectionToUVs() #converts any selection to UVs
   cmds.SelectUVBorder() #selects border of selected object
   
#Function: Runs through a chosen number of iterations of Unfold and Relax according to user defined settings
def adjUV(*args):
   i = 0
   testVal = cmds.intField("uvAdjustVal", q = 1, v = 1)
   
   while (i <= testVal):
   
     weightSolver_Val = cmds.floatSliderGrp("weightSolver", q = 1, value= 1)
     optimizeToOriginal_Val = cmds.floatSliderGrp("optimizeToOriginal", q = 1, value= 1)
     maxIterations_Val = cmds.intSliderGrp("unfoldMaxIterations", q = 1, value = 1)
     stopThresh_Val = cmds.floatSliderGrp("stopThresh", q = 1, value = 1)
     
     if(cmds.radioButtonGrp("unfoldCheckBox", q = True, sl=1) == 1):
       pinBordBool = 1
       pinUVBool = 0;
     if(cmds.radioButtonGrp("unfoldCheckBox", q = True, sl=1) == 2):
       pinUVBool = 1
       pinBordBool = 0;
     if(cmds.radioButtonGrp("unfoldCheckBox", q = True, sl=1) == 3):
       pinUVBool = 0
       pinBordBool = 0;
     
     cmds.unfold(oa = 0, gb = weightSolver_Val, gmb = optimizeToOriginal_Val,
       i = maxIterations_Val, ss = stopThresh_Val,
       pub = pinBordBool, ps = pinUVBool, us = 0)
     
     maxIterations_Val = cmds.intSliderGrp("relaxMaxIterations", q = 1, value = 1)
     
     if(cmds.radioButtonGrp("relaxCheckBox", q = True, sl=1) == 1):
       pinBordBool = 1
       pinUVBool = 0;
     if(cmds.radioButtonGrp("relaxCheckBox", q = True, sl=1) == 2):
       pinUVBool = 1
       pinBordBool = 0;
     if(cmds.radioButtonGrp("relaxCheckBox", q = True, sl=1) == 3):
       pinUVBool = 0
       pinBordBool = 0;
   
     cmds.untangleUV(r = "harmonic", pb = pinBordBool, ps = pinUVBool, mri = maxIterations_Val)
     
     i = i +1;
   
   
