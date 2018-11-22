"""

Function: mmExportAnimationAsJson
Description: This function will export the animations into the file format we are expecting for Stonehearth
#Stonehearth Animation Export Script 
#Need to create a print out of all trans/rot/scale values of a bone for each frame

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds
import maya.OpenMaya as om
import pymel.core as pm
import os

######################################
############# DEFINES ################
######################################





def main( mmConfirmBool = True, *args ):

   #Create some basic variables for use later

   #Define what a 'Tab" spacing should be.
   mmTab = "   "

   #Create a large string file to save out the animation as a .json
   mmJsonList = []


   #Set up the save for the export file

   #Ask the user where to save the export file
   #cmds.confirmDialog( title = 'Still to do', message = 'Make it so a dialogue requesting the filepath is not needed.', button = ['OK'], defaultButton = 'OK' )
   #List out what is in the document (Print it in Maya)
   #print open(fileName[0], 'r').read()
   #Canceling this dialogue should cancel the script with no repercussions
   #fileName = cmds.fileDialog2(fileFilter='*.json', caption='Where would you like to export your animation?')


   #Choose where to save the animation as a .json
   mmNewFilePath = ""
   mmNewFileName = ""

   mmOriginalFileName = cmds.file( query=True, sn=True )
   mmOriginalFileNameList = mmOriginalFileName.split('/')


   mmLengthOfFilenameList = len(mmOriginalFileNameList)


   #take one off the length because of computers
   mmLengthOfFilenameList -= 1

   mmCounter = 0

   for mmWord in mmOriginalFileNameList:
       
       if (mmCounter == mmLengthOfFilenameList):
           break
           
       if (mmCounter != 0): 
           mmNewFilePath += '/'
           
       mmNewFilePath += mmOriginalFileNameList[mmCounter]
       mmCounter += 1
       
   mmNewFileName = mmOriginalFileNameList[mmCounter].split('.')

   mmNewCompleteFilePath = mmNewFilePath + "/export/" + mmNewFileName[0] + ".json"

   #-----------------------------

   ############
   #Need to make sure that the  export folder exists, and if not, create it.
   ############

   #   Find out if there is an export folder, if not, make one.
   for item in os.listdir( mmNewFilePath ):
      if ( item != "/export" ):
         cmds.sysFile( mmNewFilePath + "/export/", makeDir=True )

   #-----------------------------

   #Start saving out the .json file
   fileWrite = open(mmNewCompleteFilePath, 'w')



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

   #-----------------------------

   #Clear Selection
   cmds.select( clear=True )
   #Select All
   cmds.select( all = 1, adn = 1 )
   mmSelectedItemsInScene = cmds.ls( sl = 1 )

   #Sort list for easier reading later
   mmSelectedItemsInScene.sort()

   #Create a list of items we want selected
   mmItemsWanted = []

   #Search all items to find ":" - because that means it is referenced
   #     We can assume that all meshes to be exported have this because we are requiring referencing.
   #     We can also assume that there is only one referenced rig in a scene at a time (because we say so).
   for mmSelectedObject in mmSelectedItemsInScene:
       
      #Split each name apart at ":"
      mmCheckName = mmSelectedObject.split(":")

      #Check if there was a ":" (if there is, a list with two entries will be created)
      if ( len(mmCheckName) == 2 ):

         #Split the name by "_" because we named things without "_" before (qubicle hates them)  - But this is still ASSUMING
         # and added "_loc" to all our locators
         mmRigName = mmCheckName[0]
         mmCheckName = mmCheckName[1].split("_")

         #Check to see if a list with two entries is returned, and if it is, if that second entry is 'loc'
         if ( len(mmCheckName) == 2 and mmCheckName[1] == 'loc' ):
            
            #If this is true, store the name into a list
            mmNameIThinkIReallyWant = mmRigName + ":" + mmCheckName[0]

            mmItemsWanted.append( mmNameIThinkIReallyWant )

            #mmItemsWanted.append( mmSelectedItemsInScene[mmCounter] )


   #Clear Selection
   cmds.select( clear=True )

   #Select the items we stored earlier
   cmds.select( mmItemsWanted )

   #mmItemsWanted is a list of _loc items
   mmSelectedNames = list(mmItemsWanted)

   #Create a new list to store the new names
   mmProperNames = []
   mmPadNames = []
   mmUsedBoneNames = []

   #Create a counter
   mmCounter = 0

   #Store the names without the prefix of the referenced rig name
   #'ReferencedAnimRig_Male:'
   for mmSelectedObject in mmSelectedNames:
      mmBoneNameList = mmSelectedObject.split(":")
      mmBoneName = mmBoneNameList[1]
      mmBoneName = mmBoneName.split("_")[0]
      mmUsedBoneName = mmBoneNameList[0] + ":" + mmBoneName
      mmPadName = mmBoneNameList[0] + ":" + mmBoneName + "_pad"
      
      mmProperNames.append(mmBoneName)
      mmUsedBoneNames.append(mmUsedBoneName)
      mmPadNames.append(mmPadName)

      mmCounter += 1

   mmCounter -= 1

   print "mmProperNames", mmProperNames
   print "mmUsedBoneNames", mmUsedBoneNames
   print "mmPadNames", mmPadNames
   print ""

   if (mmProperNames == []):
      print "Error in mmExportAnimationAsJson: is your rig referenced?"

   mmLastBone = mmProperNames[mmCounter]

   #Start printing the document which will store all of the animation data

   #Reset counter
   mmCounter = 0

   #open overall .json
   mmNewString = '{'

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)


   mmNewString =  mmTab + '"type": "animation",'

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)


   mmNewString =  mmTab + '"total_frames": "' + str(mmTotalFrames) + '",'

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)

   #Add this to code later - need to gather the info for this somewhere.
   #  Not sure where this info will come from, might have to manually create a separate property which we scan for.
   # mmNewString =  mmTab + '"reposition": [' + str(mmXValueOffset) + ',' + str(mmYValueOffset) + ',' + str(mmZValueOffset) + '],'

   # #Write the new string to the file, then separate the line down
   # fileWrite.write(mmNewString)
   # fileWrite.write(os.linesep)


   mmNewString =  mmTab + '"frames": ['

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)


   #Need to create a loop to go through all frames
   while ( mmCurrentTime <= mmLastFrame ):

      #Set Current Frame
      cmds.currentTime( mmCurrentTime, update=True )


      #Open first frame
      mmNewString =  mmTab + mmTab + '{'
           
      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)

       
      #Reset counter
      mmCounter = 0
       
      #Need to create a loop to go through all bones
      for mmUniqueBone in mmProperNames:
           
         #Actual Bone Names: mmSelectedNames
         #Bone Names we want to print: mmProperNames
         #print mmCounter
         mmCurrentSelectedBone = mmSelectedNames[mmCounter]
         mmCurrentProperBone = mmProperNames[mmCounter]
         mmCurrentUsedBone = mmUsedBoneNames[mmCounter]
         mmCurrentProperPad = mmPadNames[mmCounter]
         
         #print mmCurrentBone
        
         #Reach into Bone and grab needed values
         mmNodeTrans = cmds.xform(mmCurrentProperPad, q=True, ws=True, t=True)
         mmUsedBoneTrans = cmds.xform(mmCurrentUsedBone, q=True, os=True, t=True)

         #mmNodeTrans = node.getTranslation()
         #print "mmNodeTrans", mmNodeTrans

         mmCurrentBoneTransX = mmNodeTrans[0] + mmUsedBoneTrans[0]
         mmCurrentBoneTransY = -mmNodeTrans[2] + -mmUsedBoneTrans[2]
         mmCurrentBoneTransZ = mmNodeTrans[1] + mmUsedBoneTrans[1]

         #Round values to a max of 6 decimals
         mmCurrentBoneTransX = round( mmCurrentBoneTransX, 6 )
         mmCurrentBoneTransY = round( mmCurrentBoneTransY, 6 )
         mmCurrentBoneTransZ = round( mmCurrentBoneTransZ, 6 )
         
         #To add the mesh's rotation information to its pad, all we do is grab the rotation of the mesh.
         # We get it free because its just worldspace orientation.  Might apply to scale as well, need to test.

         node = pm.PyNode(mmCurrentUsedBone)
         mmQuatRotation = node.getRotation(quaternion=True, ws = 1)

         mmCurrentBoneRotX = mmQuatRotation.x
         mmCurrentBoneRotY = -mmQuatRotation.z
         mmCurrentBoneRotZ = mmQuatRotation.y
         mmCurrentBoneRotW = mmQuatRotation.w

         # #Round values to a max of 6 decimals
         mmCurrentBoneRotW = round( mmCurrentBoneRotW, 6 )
         mmCurrentBoneRotX = round( mmCurrentBoneRotX, 6 )
         mmCurrentBoneRotY = round( mmCurrentBoneRotY, 6 )
         mmCurrentBoneRotZ = round( mmCurrentBoneRotZ, 6 )

         #Delete TempLoc

         #-----------------------------

         #Grab Scale Values
         # mmCurrentBoneScaleX = cmds.getAttr( mmCurrentProperPad + '.scaleX')
         # mmCurrentBoneScaleY = cmds.getAttr( mmCurrentProperPad + '.scaleY')
         # mmCurrentBoneScaleZ = cmds.getAttr( mmCurrentProperPad + '.scaleZ')

         # # This didn't grab the World Space info from the bone and so info didn't transfer
         # mmNodeScale = cmds.xform(mmCurrentProperPad, q=True, ws=True, s=True)
         # mmUsedBoneScale = cmds.xform(mmCurrentUsedBone, q=True, os=True, s=True)
         # mmCurrentBoneScaleX = mmNodeScale[0] * mmUsedBoneScale[0]
         # mmCurrentBoneScaleY = mmNodeScale[2] * mmUsedBoneScale[2]
         # mmCurrentBoneScaleZ = mmNodeScale[1] * mmUsedBoneScale[1]

         # This one seems to work.
         mmUsedBoneScale = cmds.xform(mmCurrentUsedBone, q=True, ws=True, s=True)
         mmCurrentBoneScaleX = mmUsedBoneScale[0]
         mmCurrentBoneScaleY = mmUsedBoneScale[2]
         mmCurrentBoneScaleZ = mmUsedBoneScale[1]

         # #Round values to a max of 6 decimals
         mmCurrentBoneScaleX = round( mmCurrentBoneScaleX, 6 )
         mmCurrentBoneScaleY = round( mmCurrentBoneScaleY, 6 )
         mmCurrentBoneScaleZ = round( mmCurrentBoneScaleZ, 6 )

         #Open the bone
         mmNewString =  mmTab + mmTab + mmTab + '"' + mmCurrentProperBone + '": {'
                
         #Write the new string to the file, then separate the line down
         fileWrite.write(mmNewString)
         fileWrite.write(os.linesep)

         #Print Translation of Bone
         mmNewString =  mmTab + mmTab + mmTab + mmTab + '"pos": [' + str(mmCurrentBoneTransX) + ',' + str(mmCurrentBoneTransY) + ',' + str(mmCurrentBoneTransZ) + '],'
                
         #Write the new string to the file, then separate the line down
         fileWrite.write(mmNewString)
         fileWrite.write(os.linesep)

         #Print Quaternion Rotation of Bone
         mmNewString =  mmTab + mmTab + mmTab + mmTab + '"rot": [' + str(mmCurrentBoneRotW) + ',' + str(mmCurrentBoneRotX) + ',' + str(mmCurrentBoneRotY) + ',' + str(mmCurrentBoneRotZ) + '],'
                
         #Write the new string to the file, then separate the line down
         fileWrite.write(mmNewString)
         fileWrite.write(os.linesep)

         #Print Scale of Bone
         #This section should be commented out for now
         #***Don't forget to fix commas when adding this back in***
         mmNewString =  mmTab + mmTab + mmTab + mmTab + '"sca": [' + str(mmCurrentBoneScaleX) + ',' + str(mmCurrentBoneScaleY) + ',' + str(mmCurrentBoneScaleZ) + ']'
                
         #Write the new string to the file, then separate the line down
         fileWrite.write(mmNewString)
         fileWrite.write(os.linesep)

         #Increment Counter
         mmCounter += 1


         #Close the bone
         if ( mmCurrentProperBone != mmLastBone ):

            mmNewString =  mmTab + mmTab + mmTab + '},'
                        
            #Write the new string to the file, then separate the line down
            fileWrite.write(mmNewString)
            fileWrite.write(os.linesep)

         else:

            mmNewString =  mmTab + mmTab + mmTab + '}'
                        
            #Write the new string to the file, then separate the line down
            fileWrite.write(mmNewString)
            fileWrite.write(os.linesep)

           
      if ( mmCurrentTime < mmLastFrame ):

         mmNewString =  mmTab + mmTab + '},'
                  
         #Write the new string to the file, then separate the line down
         fileWrite.write(mmNewString)
         fileWrite.write(os.linesep)

      else:

         mmNewString =  mmTab + mmTab + '}'
                   
         #Write the new string to the file, then separate the line down
         fileWrite.write(mmNewString)
         fileWrite.write(os.linesep)

           
      #Increment Counter
      mmCurrentTime += 1
       
   mmNewString =  mmTab + ']'

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)


   mmNewString =  '}'

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)

   cmds.select( cl = 1 )

   #Reset time to first frame
   cmds.currentTime( mmOriginalTime )


   #Join list into a giant string
   #mmWritableString = ''.join(mmJsonList)

   #This needs to have the entier printed value saved out instead of "hello"
   #fileWrite.write(mmWritableString)

   fileWrite.close()

   if (mmConfirmBool):
      #Send a confirmation to the user saying the export is complete.
      cmds.confirmDialog( title = 'Export Complete', message = 'File Exported', button = ['OK'], defaultButton = 'OK' )
      #List out what is in the document (Print it in Maya)
      #print open(fileName[0], 'r').read()



'''
Need a secondary function to call the main because a negative value is being passed in somehow.
'''
def mainCall( *args ):
   main(True)