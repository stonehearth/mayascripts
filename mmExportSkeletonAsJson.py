"""

Function: mmExportSkeletonAsJson
Description: This function will export the skeletal animation into the file format we are expecting for Stonehearth

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
      #print "mmWord " + str(mmCounter), mmWord
       
      if ( mmCounter == mmLengthOfFilenameList):
         break
           
      if ( mmCounter != 0): 
         mmNewFilePath += '/'

      if ( mmCounter == mmLengthOfFilenameList-1 ):
         mmTempFolderName = mmWord


           
      mmNewFilePath += mmOriginalFileNameList[mmCounter]
      mmCounter += 1
   
   #Filename for the rig - should be the same as the folder name (line below is old)
   #mmNewFileName = mmOriginalFileNameList[mmCounter].split('.')

   #Add 'export' folder to file path so its being dropped in a private place
   mmNewCompleteFilePath = mmNewFilePath + "/export/" + mmTempFolderName + ".json"


   # print "mmNewCompleteFilePath",mmNewCompleteFilePath
   # print "mmNewFilePath",mmNewFilePath

   #-----------------------------

   ############
   #Need to make sure that the  atom_exports folder exists, and if not, create it.
   ############
   mmFolderChecker = True

   #   Find out how many files are in the max_animconversions folder.
   for item in os.listdir( mmNewFilePath ):
      # print "item", item
      if ( item == "export" ):
         mmFolderChecker = False
         break

   if ( mmFolderChecker ):
      cmds.sysFile( mmNewFilePath + "/export/", makeDir=True )

   #-----------------------------

   #Start saving out the .json file
   fileWrite = open(mmNewCompleteFilePath, 'w')



   #Store the original time before running the script
   mmOriginalTime = cmds.currentTime( query=True )


   #Clear Selection
   cmds.select( clear=True )
   #Select only Locators
   mmLocatorShapesInScene = cmds.ls( type = ("locator") )

   #Find the parent (which should always be the transforms)
   mmLocatorsInScene = cmds.listRelatives(mmLocatorShapesInScene, parent=True, fullPath=0)

   #Sort list for easier reading later
   mmLocatorsInScene.sort()

   #Create a list of items we want selected
   mmItemsWanted = []
   mmCounter = 0

   #Search all items to find the 'loc' locators
   #This works because nothing is referenced - will not be able to do the same in Export Anim
   for mmSelectedObject in mmLocatorsInScene:
   
      #Split the name by "_" because we named things without "_" before (qubicle hates them)
      # and added "_loc" to all our locators
      mmCheckName = mmSelectedObject.split("_")
      #print mmCheckName

      #Check to see if a list with two entries is returned, and if it is, if that second entry is 'loc'
      if ( len(mmCheckName) == 2 and mmCheckName[1] == 'loc' ):

         #If this is true, store the name into a list
         mmItemsWanted.append( mmLocatorsInScene[mmCounter] )

      mmCounter += 1

   #Clear Selection
   cmds.select( clear=True )

   #Select the items we stored earlier
   cmds.select( mmItemsWanted )



   mmSelectedNames = mmItemsWanted
   #print mmSelectedNames

   #Create a new list to store the new names
   mmProperNames = []
   #mmPadNames = []

   #Create a counter
   mmCounter = 0

   mmTempRootBone = ""

   #Store the names without the prefix of the referenced rig name
   #'ReferencedAnimRig_Male:'
   for mmSelectedObject in mmSelectedNames:
      mmBoneName = mmSelectedObject.split("_")[0]
      #mmPadName = mmBoneName + "_pad"
      
      mmProperNames.append(mmBoneName)
      #mmPadNames.append(mmPadName)
      

      if (mmBoneName == "root" ):
         #mmTempRootPad = ?Needed?
         mmTempRootBone = mmSelectedObject

      mmCounter += 1

   mmCounter -= 1
   
   #print mmProperNames

   #Store Last Bone name
   mmLastBone = mmProperNames[mmCounter]

   #Start printing the document which will store all of the animation data

   #Reset counter
   mmCounter = 0

   #open overall .json
   mmNewString = '{'

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)


   mmNewString =  mmTab + '"type" : "rig",'

   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)
   

   mmNewString =  mmTab + '"skeleton": {'

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
      #mmCurrentProperPad = mmPadNames[mmCounter]
      #print mmCurrentBone
      
      '''
         #Reach into Bone and grab needed values
         nodeTrans = cmds.xform(mmCurrentSelectedBone, q=True, ws=True, t=True)
         #nodeTrans = node.getTranslation()
         print nodeTrans
         mmCurrentBoneTransX = nodeTrans[0]
         mmCurrentBoneTransY = -nodeTrans[2]
         mmCurrentBoneTransZ = nodeTrans[1]
      '''

      nodeTrans = cmds.xform(mmCurrentSelectedBone, q=True, ws=True, t=True)
      mmCurrentBoneTransX = nodeTrans[0]
      mmCurrentBoneTransY = -nodeTrans[2]
      mmCurrentBoneTransZ = nodeTrans[1]

      '''
      #Old Method - only in local space
      #Reach into Bone and grab translation values
      mmCurrentBoneTransX = cmds.getAttr( mmCurrentSelectedBone + '.translateX')
      mmCurrentBoneTransY = cmds.getAttr( mmCurrentSelectedBone + '.translateY')
      mmCurrentBoneTransZ = cmds.getAttr( mmCurrentSelectedBone + '.translateZ')
      '''

      # #Round values to a max of 6 decimals
      # mmCurrentBoneTransX = round( mmCurrentBoneTransX, 6 )
      # mmCurrentBoneTransY = round( mmCurrentBoneTransY, 6 )
      # mmCurrentBoneTransZ = round( mmCurrentBoneTransZ, 6 )

      #if this is the last bone, close the skeletal section
      if ( mmCurrentProperBone != mmLastBone ):

         #Open the bone and print its skeletal information on the same line
         mmNewString =  mmTab + mmTab + '"' + mmCurrentProperBone + '": [' + str(mmCurrentBoneTransX) + ',' + str(mmCurrentBoneTransY) + ',' + str(mmCurrentBoneTransZ) + '],'

      else:

         #Open the bone and print its skeletal information on the same line
         mmNewString =  mmTab + mmTab + '"' + mmCurrentProperBone + '": [' + str(mmCurrentBoneTransX) + ',' + str(mmCurrentBoneTransY) + ',' + str(mmCurrentBoneTransZ) + ']'


      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)

      #Increment Counter
      mmCounter += 1

   mmNewString = mmTab + '},'
            
   #Write the new string to the file, then separate the line down
   fileWrite.write(mmNewString)
   fileWrite.write(os.linesep)

   if ( mmTempFolderName == "male" or mmTempFolderName == "female" or mmTempFolderName == "goblin"):

      #Old stuff - good for human male.. and nothing else.
      mmNewString = mmTab + '"animation_root" : "file(../animations/' + mmTempFolderName + ')",'
               
      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + '"effects_root" : "file(../effects)",'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + '"postures" : "file(../postures.json)",'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + '"moods" : "file(../moods.json)",'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + '"weighted_effects" : "file(../weighted_effects.json)",'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + '"conversation_effects" : "file(../conversation_effects.json)",'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + '"collision_shape" : {'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + mmTab + '"type" : "cylinder_collision_shape",'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + mmTab + '"radius" : 5,'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + mmTab + '"height" : 35'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)


      mmNewString =  mmTab + '}'

      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)
      
   else:

      #New Stuff
      mmNewString = mmTab + '"animation_root" : "file(animations)",'
               
      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)

      mmNewString = mmTab + '"effects_root": "file(effects)"'
               
      #Write the new string to the file, then separate the line down
      fileWrite.write(mmNewString)
      fileWrite.write(os.linesep)
      
   #Close out file
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

   if ( mmConfirmBool ):
      #Send a confirmation to the user saying the export is complete.
      cmds.confirmDialog( title = 'Export Complete', message = 'File Exported', button = ['OK'], defaultButton = 'OK' )
      #List out what is in the document (Print it in Maya)
      #print open(fileName[0], 'r').read()


'''
Need a secondary function to call the main because a negative value is being passed in somehow.
'''
def mainCall( *args ):
   main(True)