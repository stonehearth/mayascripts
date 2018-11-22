"""

Function: mmReturnFilepathOrFilename
Description: This function will return either the file path or file name of a list with a string of a complete filepath&name

"""
__authors__ = "Matt Malley"

######################################
############# IMPORTS ################
######################################
import maya.cmds as cmds

######################################
############# DEFINES ################
######################################



def main( mmFilepathAndFilename, mmDesiredReturn ):
   # print "mmFilepathAndFilename", mmFilepathAndFilename
   mmFilepathAndFilenameNameList = []
   mmFilepathAndFilenameList = []

   # print "type( mmFilepathAndFilename )", type( mmFilepathAndFilename )

   #Need to find out what type mmFilepathAndFilename is so we don't error out when its a list or a string
   if ( type( mmFilepathAndFilename ) != type( ["list"] ) ):

      #---------------------------
      #This is to make sure we don't have (a specific) weird unicode in our strings.
      mmFilepathAndFilenameSplit = mmFilepathAndFilename.split("'")

      if ( len(mmFilepathAndFilenameSplit) > 1 ):

         mmFilepathAndFilename = mmFilepathAndFilenameSplit[1]

      # print "mmFilepathAndFilename during mmRFOF", mmFilepathAndFilename
      # print "type( mmFilepathAndFilename )", type( mmFilepathAndFilename )

      #---------------------------

      mmFilepathAndFilenameNameList.append(mmFilepathAndFilename)
      
      #Copy the list into the proper name
      mmFilepathAndFilename = list(mmFilepathAndFilenameNameList)
      
   # print "mmFilepathAndFilename", mmFilepathAndFilename

   #0 returns File Path
   if ( mmDesiredReturn == 0 ):
               
      mmFilepathAndFilenameList = mmFilepathAndFilename[0].split('/')
      
      mmFilenameAndFiletype = mmFilepathAndFilenameList[len(mmFilepathAndFilenameList) - 1]
      
      mmFilepath = mmFilepathAndFilename[0].split(mmFilenameAndFiletype)
      
      mmReturnString = str(mmFilepath[0])
      # print "mmReturnString", mmReturnString
      # print "type( mmReturnString )", type( mmReturnString )
      
   #1 returns File Name
   else:
               
      mmFilepathAndFilenameList = mmFilepathAndFilename[0].split('/')
      
      mmFilenameAndFiletype = mmFilepathAndFilenameList[len(mmFilepathAndFilenameList) - 1]
      
      mmFilename = mmFilenameAndFiletype.split('.')
      
      mmReturnString = str(mmFilename[0])
      # print "mmReturnString", mmReturnString
      # print "type( mmReturnString )", type( mmReturnString )
   
      
   return mmReturnString;