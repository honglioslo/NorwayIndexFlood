# -*- coding: latin_1 -*-
# General.py
#-----------------------------------------------------------------------------------
# Opprettet: 26.09.2008, IOPE
# Revidert:
#-----------------------------------------------------------------------------------
# Beskrivelse:
# Module for forkjellige generelle funksjoner
#-----------------------------------------------------------------------------------
# Kontekst: Generelt
#-----------------------------------------------------------------------------------
# Argumenter:
# <argument 1>: ScriptName, the name of the script this module is called from
# <argument 2>: logtekst, the text to be printed in the logfile
#-----------------------------------------------------------------------------------
# Resultater: logfile with the name of the script it is called from
#-----------------------------------------------------------------------------------
# Import system modules
import sys, os, smtplib,arcpy, time, ConfigParser


#***********************************************************************************
def Log(LogFile, logtekst):

   try:
       #---Open the logfile
       if not arcpy.Exists(LogFile):
          OpenLogFile = open(LogFile, 'w')
       else:
          OpenLogFile = open(LogFile, 'a')

       #---Write tekst to the logfile
       Time = time.strftime("%Y-%m-%d,%I:%M:%S", time.localtime())
       OpenLogFile.write(Time+"   ")
       OpenLogFile.write(logtekst)
       OpenLogFile.write("\n")

       #---Close the logfile
       OpenLogFile.close()
   except:
       #If an error occured print the message to the screen
       print "an error has occurred in function " + "Log"
       sys.exit(1)
#***********************************************************************************
def Kill(GeoDatasetList):

   try:

       for GeoDataset in GeoDatasetList:
           if arcpy.Exists(GeoDataset):
              arcpy.Delete_management(GeoDataset)
              #print GeoDataset + " is pushing up the daisies"
           if arcpy.Exists(GeoDataset + ".shp"):
              arcpy.Delete_management(GeoDataset + ".shp")
              #print GeoDataset + ".shp is pushing up the daisies"
   except:
       #If an error occured print the message to the screen
       print "an error has occurred in function " + "Kill"
       print arcpy.GetMessages()
       sys.exit(2)
#*****************************************************************************
def sett_snapextent(lExtent, lRaster):
    try:
        dsc = arcpy.Describe(lRaster)
        iCell = dsc.MeanCellWidth

        xmin = round(float(lExtent.XMin) / iCell) * iCell
        ymin = round(float(lExtent.YMin) / iCell) * iCell
        xmax = round(float(lExtent.XMax) / iCell) * iCell
        ymax = round(float(lExtent.YMax) / iCell) * iCell
        extent = "%s %s %s %s" %(xmin,ymin,xmax,ymax)

        return extent
    except:
        #If an error occured print the message to the screen
        print "an error has occurred in function " + "sett_snapextent"
        print arcpy.GetMessages()
        sys.exit(3)
#***********************************************************************************
def FieldExist(Featureclass, FieldName):
    try:
        FieldList = arcpy.ListFields(Featureclass, FieldName)
        FieldCount = len(FieldList)
        if FieldCount == 1:
           return True
        else:
           return False
    except:
        #If an error occured print the message to the screen
        print "an error has occurred in function " + "FieldExist"
        print arcpy.GetMessages()
        return False
#***********************************************************************************
def NeededFieldWidth(InFeatureClass,FieldName,LogFile):
    try:

        MaxFieldWidth = 0
        cur = arcpy.SearchCursor(InFeatureClass,"","",FieldName)
        for row in cur:
            if row.getValue(FieldName):
                if len(row.getValue(FieldName)) > MaxFieldWidth:
                    MaxFieldWidth = len(row.getValue(FieldName))
        del cur
        print MaxFieldWidth
        return MaxFieldWidth

    except:
        ErrorHandling(LogFile)
        sys.exit(1)
#***********************************************************************************
def CheckWorkspaceForEmptyFeatureClasses(Workspace):
    try:
        # get the current workspace
        CurrentWorkspace = arcpy.env.workspace
        arcpy.env.workspace = Workspace

        EmptyFeatureClassList = []
        for FeatureClass in arcpy.ListFeatureClasses():
            if arcpy.GetCount_management(FeatureClass).getOutput(0) == 0:
                EmptyFeatureClassList.append(FeatureClass)
        if len(EmptyFeatureClassList) > 0:
            return True
        else:
           return False
    except:
        #If an error occured print the message to the screen
        print "an error has occurred in function " + "CheckWorkspaceForEmptyFeatureClasses"
        print arcpy.GetMessages()
        return False

#***********************************************************************************
def StringIsAap(String):
    try:
        if String == "Aap":
           return True
        else:
           return False
    except:
        #If an error occured print the message to the screen
        print "an error has occurred in function " + "StringIsAap"
        print arcpy.GetMessages()
        return False
#***********************************************************************************

##def ReadIni(IniFile,Var):
##   #-------------------------------------------------------------------#
##   # Module trenger Navn til Inifile og variable                       #
##   # Inifile må ser slikt ut:                                          #
##   #                                                                   #
##   # [Sectionname]                                                     #
##   # variable:verdie     eller    variable = verdie                    #
##   #                                                                   #
##   # Secions kan brukes f.e for å kategorisere i stier, filer, verdier #
##   #-------------------------------------------------------------------#
##   try:
##      if not gp.exists(IniFile):
##         print "%s does not exist" %(IniFile)
##         sys.exit(2)
##      else:
##         var = Var.lower()
##         ItemCheck = 0
##         config = ConfigParser.ConfigParser()
##         config.read(IniFile)
##         # loop through all sections
##         for section in config.sections():
##            # and listet variables to find the value of Var
##            for Item in config.items(section):
##               if Item[0] == var:
##                  Item = config.get(section,var)
##                  ItemCheck = 1
##                  return Item
##
##         if ItemCheck == 0:
##            print "Variable %s does not exist in %s" %(Var,IniFile)
##            sys.exit(2)
##
##   except:
##       #If an error occured print the message to the screen
##       print "an error has occurred in function " + "ReadIni"
##       print gp.GetMessages()
##       sys.exit(1)
#**********************************************************************************
def ReadIni(IniFile,Var):
   #-------------------------------------------------------------------#
   # Module trenger Navn til Inifile og variable                       #
   # Inifile må ser slikt ut:                                          #
   #                                                                   #
   # [Sectionname]                                                     #
   # variable:verdie     eller    variable = verdie                    #
   #                                                                   #
   # Secions kan brukes f.e for å kategorisere i stier, filer, verdier #
   #-------------------------------------------------------------------#
   try:
      if not arcpy.Exists(IniFile):
         print "%s does not exist" %(IniFile)
         sys.exit(2)
      else:
         var = Var.lower()
         ItemCheck = 0
         config = ConfigParser.ConfigParser()
         config.read(IniFile)
         # loop through all sections"
         for section in config.sections():
            # and listet variables to find the value of Var
            for Item in config.items(section):
               if Item[0] == var:
                  Item = config.get(section,var)
                  ItemCheck = 1
                  #print Item
                  return Item

         if ItemCheck == 0:
            Item = "Variable %s does not exist in %s" %(Var,IniFile)
            return Item


   except:
       #If an error occured print the message to the screen
       print "an error has occurred in function " + "ReadIni"
       print "OBS! sjekk om inifilen er en ren txt og ikke rft!!!!"
       print arcpy.GetMessages()
       sys.exit(1)
#***********************************************************************************
def Email(FromEmailAdress,ToEmailAdress,Subject,EmailText):

   try:
        TEXT = """
        %s""" %(EmailText)
        print TEXT
        #----------- Prepare actual message --------------
        msg = """\

        From: %s
        To: %s
        Subject: %s
        %s
        """ % (FromEmailAdress, ToEmailAdress, Subject, TEXT)

        # The actual mail send
        # server = smtplib.SMTP("exch-post.nve.no")
	server = smtplib.SMTP("smtput.nve.no")
	server.sendmail(FromEmailAdress, ToEmailAdress, msg)
	server.quit()

	# -------------------------------------------------
   except:
        #If an error occured print the message to the screen
        print "an error has occurred in function " + "Email"
        print "if i remember correctly so works this only from GISEN"
        sys.exit(1)

#***********************************************************************************

def ExtentSelected(lyrFeatures, LogFile):
    try:
        cur = arcpy.SearchCursor(lyrFeatures)
        lstExt = [0,0,0,0]
        for row in cur:
           FeatureExt = row.Shape.Extent
           if lstExt[0] > FeatureExt.XMin: lstExt[0] = FeatureExt.XMin
           if lstExt[1] > FeatureExt.YMin: lstExt[1] = FeatureExt.YMin
           if lstExt[2] < FeatureExt.XMax: lstExt[2] = FeatureExt.XMax
           if lstExt[3] < FeatureExt.YMax: lstExt[3] = FeatureExt.YMax
        del cur
        extent = "%s %s %s %s" % tuple(lstExt)
        return extent

    except:
        ErrorHandling(LogFile)
        sys.exit(1)

