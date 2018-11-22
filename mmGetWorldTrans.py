"""

Function: mmGetWorldTrans
Description: Function will freeze translations on the current object, snap it to the world's origin, store the x,y,z values,
freeze translations again, then move the object back to where it was in the world before - keeping the world translations.

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

######################################
############# DEFINES ################
######################################




def main(*args):
   curXTrans = 0
   curYTrans = 0
   curZTrans = 0
   i = 0
   
   mmSelectedInScene = cmds.ls(sl=1)
   
   if(mmSelectedInScene):
      mmSelectedInScene = cmds.ls(sl = 1)

      numberOfSpans = len(mmSelectedInScene)
      numberOfSpans -= 1

      #
      #Start the loop here
      #
      while (i <= numberOfSpans):   
      #for i, sel in enumerate(mmSelectedInScene):

         cmds.select(mmSelectedInScene[i])

         cmds.makeIdentity( a = 1, t = 1, r = 0, s = 0 )

         cmds.move(0,0,0, xyz = 1, rpr = 1)

         curXTrans = cmds.getAttr(mmSelectedInScene[i] + ".tx")
         curYTrans = cmds.getAttr(mmSelectedInScene[i] + ".ty")
         curZTrans = cmds.getAttr(mmSelectedInScene[i] + ".tz")

         curXTrans = curXTrans*-1
         curYTrans = curYTrans*-1
         curZTrans = curZTrans*-1

         cmds.makeIdentity( a = 1, t = 1, r = 0, s = 0 )

         cmds.move( curXTrans, curYTrans, curZTrans, rpr = 1)
         i += 1

   else:
      print "Nothing is selected.";



def option(*args):
   curXTrans = 0
   curYTrans = 0
   curZTrans = 0
   i = 0
   
   mmSelectedInScene = cmds.ls(sl=1)
   
   if(mmSelectedInScene):

      for mmSpan in mmSelectedInScene:

         cmds.select( cl = 1 )
         cmds.select(mmSpan)
         
         mmWhoIsParent = cmds.listRelatives( p = 1 )
         #print "mmWhoIsParent", mmWhoIsParent
         
         cmds.parent(mmSpan, w = 1)

         cmds.makeIdentity( a = 1, t = 1, r = 0, s = 0 )
         
         cmds.move(0,0,0, xyz = 1, rpr = 1)

         curXTrans = cmds.getAttr(mmSelectedInScene[i] + ".tx")
         curYTrans = cmds.getAttr(mmSelectedInScene[i] + ".ty")
         curZTrans = cmds.getAttr(mmSelectedInScene[i] + ".tz")

         curXTrans = curXTrans*-1
         curYTrans = curYTrans*-1
         curZTrans = curZTrans*-1
         #print "curXTrans", curXTrans, "curYTrans", curYTrans, "curZTrans", curZTrans

         cmds.makeIdentity( a = 1, t = 1, r = 0, s = 0 )

         cmds.move( curXTrans, curYTrans, curZTrans, rpr = 1)
         
         cmds.parent( mmSpan, mmWhoIsParent )
         
         i += 1

   else:
      print "Nothing is selected.";
