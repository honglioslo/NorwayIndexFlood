# -*- coding: latin_1 -*-
#***********************************************************************************
#-----------------------------------------------------------------------------------
# Filnavn: Avrenningrivernet.py
#-----------------------------------------------------------------------------------
# Opprettet: 1. des. 2010, JSV
# Revidert:
#-----------------------------------------------------------------------------------
# Beskrivelse:
#
#-----------------------------------------------------------------------------------
# Kontekst:
#
#-----------------------------------------------------------------------------------
# Argumenter: ingen
#-----------------------------------------------------------------------------------
# Forutsetninger:
# Fil feltinformasjon_alle.dbf med felt VOMR (vassdragsomr�de) og SNR (stasjonsnummer)
# Denne filen definerer hvilke m�lestasjoner analysen skal kj�res for
#-----------------------------------------------------------------------------------
# Resultater:
#
#-----------------------------------------------------------------------------------
#***********************************************************************************
# Import av systemmoduler
import sys, string, os, arcpy, traceback
import numpy
import arcpy
from arcpy import env
from arcpy.sa import *

# Import av NVE-rutiner
sys.path.append("V:\\Rutiner\\Python\\NVE")
from General10 import Log
from General10 import sett_snapextent

# Tillat overskriving av resultater
env.overwriteOutput = True
env.scratchWorkspace = r"C:\Temp\scratch.gdb"

#***********************************************************************************
def ErrorHandling(LogFile):
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    PyMsg = "PYTHON ERROR:\n" + tbinfo + "\n" + str(sys.exc_type) + ":" + str(sys.exc_value)+ "\n"
    GpMsg = "ARCPY ERROR:\n" + arcpy.GetMessages(2)+ "\n"
    print(PyMsg)
    print(GpMsg)
    arcpy.AddError(PyMsg)
    arcpy.AddError(GpMsg)
    Log(LogFile,PyMsg)
    Log(LogFile,GpMsg)
    arcpy.AddMessage(arcpy.GetMessages(1))
    #print arcpy.GetMessages(1)
    Log(LogFile,arcpy.GetMessages())
#***********************************************************************************
# Funksjonsdefinisjoner
#***********************************************************************************
def Resultat_Eksisterer(utfil):
    if arcpy.Exists(utfil):
        return True
    else:
        return False

#***********************************************************************************
def AreaDistributionRivernet(workspace,fc_msta_River,catchment,grd_hydflowdir,grd_hydflowacc,test,LogFile, utfil):

    try:

        LogTekst = " AreaDistributionRivernet "
        print(LogTekst)
        #Log(LogFile,LogTekst)

        class LicenseError(Exception):
             pass

        # Check out any necessary licenses
        print("The Spatial license is " + arcpy.CheckExtension("Spatial"))
        if arcpy.CheckExtension("Spatial") == "Available":
           arcpy.CheckOutExtension("Spatial")
        else:
           raise LicenseError

        # arcpy.env.workspace = workspace
        # dsc_catchment = arcpy.Describe(catchment)
        # extent_felt = dsc_catchment.extent
        # env.extent = sett_snapextent(extent_felt, grd_hydflowdir)
        # cellSize = arcpy.Describe(grd_hydflowdir).MeanCellHeight
        # print("Satt snapextent")
        # # Convert rivernet to raster
        # arcpy.FeatureToRaster_conversion(fc_msta_River, "LTEMA", "HRiver", cellSize)
        # # give all cells in the network tha river code
        # River_grd = Con("HRiver", 3201)
        # River_grd.save(os.path.join(workspace,"grd_msta_River"))
        # grd_msta_River = os.path.join(workspace,"grd_msta_River")		
        # arcpy.BuildRasterAttributeTable_management(grd_msta_River)
        # print("rivernet convertet to raster")
########################################################################
        grd_msta_River = os.path.join(workspace,"grd_msta_River")
########################################################################
		# extract flow acc by mask, glomma Wrong at extract
        # CatFlowAcc = ExtractByMask(grd_hydflowacc, catchment)
        # CatFlowAcc.save(os.path.join(workspace,"CatFlowAcc"))
        # arcpy.BuildRasterAttributeTable_management(CatFlowAcc)
        # print(" extract flow acc by catchment mask")
        # CatFlowAcc = os.path.join(workspace,"CatFlowAcc")
        # Rows = arcpy.SearchCursor(grd_msta_River)
        # for row in Rows:
           # countRiverHong = int(row.getValue("Count"))
           # print("the number of river cells")
           # print(countRiverHong)
        # arr = arcpy.RasterToNumPyArray(CatFlowAcc)
        # brr = numpy.sort(arr, axis=None, kind = "mergesort")
        # brr[:] = brr[::-1]
        # thValue = brr[countRiverHong-1]
        # print(thValue)
        # ConAcc = "Value < %s" % (thValue)
        # outCon = SetNull(CatFlowAcc, 1, ConAcc)
        # outCon.save(os.path.join(workspace,"outCon"))
        # print("get river cells according to the flow acc")
#############################################################
        # # extract flow dir to the river cells
        # outCon = os.path.join(workspace,"outCon");
        # CatFlowDir = Con(outCon, grd_hydflowdir)			
        # CatFlowDir.save(os.path.join(workspace,"CatFlowDir"))
        # print(CatFlowDir)
#############################################################	
        flowlen_diff = Int(FlowLength(os.path.join(workspace,"CatFlowDir"), "DOWNSTREAM", ""))
        arcpy.BuildRasterAttributeTable_management(flowlen_diff)
        flowlen_diff.save("%s\\flowlen_diff" % (workspace))		
        flowlen_diff = os.path.join(workspace, "flowlen_diff")
# MINIMUM —Smallest value of all cells in the input raster.
# MAXIMUM —Largest value of all cells in the input raster.
# MEAN —Average of all cells in the input raster.
# STD —Standard deviation of all cells in the input raster. 
        ReStat = arcpy.GetRasterProperties_management(flowlen_diff, "MINIMUM")
        MinValue = ReStat.getOutput(0)
        if (MinValue < 1):
            Log(LogFile, "min value is not 0, wrong; it is %s" %(MinValue))
            print(MinValue)
            return None
        else:
            resultatfil = open(utfil, 'a')
            resultatfil.write("Statistics for River\n")
            resultatfil.write('\n')
            ReStat = arcpy.GetRasterProperties_management(flowlen_diff, "MAXIMUM")
            MaxValue = ReStat.getOutput(0)                
            resultatfil.write('Max River, %s\n' %(MaxValue))
            ReStat = arcpy.GetRasterProperties_management(flowlen_diff, "MEAN")
            MeanValue = ReStat.getOutput(0)                
            resultatfil.write('Mean River, %s\n' %(MeanValue))
            ReStat = arcpy.GetRasterProperties_management(flowlen_diff, "STD")
            STDValue = ReStat.getOutput(0)                
            resultatfil.write('STD River, %s\n' %(STDValue))
            resultatfil.write('\n')
            resultatfil.close()     
    except:
        ErrorHandling(LogFile)
        sys.exit(9)
#***********************************************************************************

def Tilrettelegg_Data(stasjonsnr,DDDParameterList,DDD_Output_List,arbeidsomr,fc_mstaFelt,fc_rivernet,grd_hydflowdir,grd_hydflowacc,landuse,dtem25,resMal,test,LogFile):
    try:

        loggtekst = "\nMalestasjon: %s\n" % (stasjonsnr)
        print("Malestasjon: %s" % (stasjonsnr))

        resultatkatalog = os.path.join(arbeidsomr,"resultat")
        if not os.path.exists(resultatkatalog):
            os.makedirs(resultatkatalog)
        ok_stnr = stasjonsnr.replace(".", "_")
        resultatGdb = os.path.join(arbeidsomr, "%s_0.gdb" % (ok_stnr))
        # Creates geodatabase per station
        utfil = os.path.join(resultatkatalog, "%s_Stat.txt" %(ok_stnr))
        # check resultfiles
        resOk = Resultat_Eksisterer(utfil)
        print("%s made? %s" %(utfil,resOk))

        #--- if resultfile and result gbg exist.
        if resOk:
            print("%s already calculated" % (stasjonsnr))
            loggtekst += "%s already calculated\n" % (stasjonsnr)
        else:
            # # # env.extent = "MAXOF"

            # # Get the catchment for the station
            # # # msta_query = "\"STASJON_NR\" = '%s'" % (stasjonsnr)
            # # # catchment = "%s\\msta_felt" % (resultatGdb)
            # # # if arcpy.Exists("lyr"):
                # # # arcpy.Delete_management("lyr")
            # # # arcpy.MakeFeatureLayer_management(fc_mstaFelt, "lyr")
            # # # arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", msta_query)
            # # # if int(arcpy.GetCount_management("lyr").getOutput(0)) > 0:
                # # # arcpy.CopyFeatures_management("lyr", catchment)
                # # # print "Copied catchment polygon for %s" % (stasjonsnr)

                    # # --- get the river net inside the catchment
            # # # fc_msta_River = os.path.join(resultatGdb,"msta_River")
            # # # arcpy.Clip_analysis(fc_rivernet, catchment, fc_msta_River)
		
            fc_msta_River = os.path.join(resultatGdb,"msta_River")
            catchment = os.path.join(resultatGdb,"msta_felt")
            para = "river"			
            if Resultat_Eksisterer(fc_msta_River):           
                AreaDistributionRivernet(resultatGdb,fc_msta_River,catchment,grd_hydflowdir,grd_hydflowacc,test,LogFile, utfil)
            else:
			    Log(LogFile, "no results %s" % 	(resultatGdb))
    except:
        ErrorHandling(LogFile)
        sys.exit(9)
# Hovedskript
#***********************************************************************************
def main():

    #--- INPUT ARGUMENTER
    #msta = sys.argv[1]
    #msta = 101.1
    #datotag = "20161115"                        # dette er bare en tag
    arbeidsomr = "C:\\Temp\\FlowLength"  # katalogen m� finnes
    #check if stasjonsnr er format xx.x.0
    #if msta.count(".") == 1:
    #    msta = "%s.0" %msta

    #mstaliste = []
    StaFile = open("%s\\%s" % (arbeidsomr,"miss_sta"))
	
    #mstaliste.append(msta)
    #--- DDDParameterList = ["River","SoilBogGlacier","Hypso_HBV", "DDDD"]
    DDDParameterList = ["River"]
    #DDD_Output_List = ["AreaDistribution","Statistics"]
    DDD_Output_List = ["Statistics"]
    #--- STANDARD INPUT
    SDE_Innsyn = "Database Connections\\AD@innsynWGS_GISSQL01.sde"
    Database = "innsyn_wgs"
    fc_mstaFelt = "%s\\%s.VANN.Hydrologi_INNSYN\\%s.VANN.HYDRA_FeltTotalMstaF" %(SDE_Innsyn,Database,Database)
    fc_rivernet = "%s\\%s.VANN.Elvenett_INNSYN\\%s.VANN.ElvenettL" %(SDE_Innsyn,Database,Database)
    grd_hydflowdir = "%s\\%s.VANN.HYDFLOWDIR" %(SDE_Innsyn,Database)
    grd_hydflowacc = "%s\\%s.VANN.HYDFLOWACC" %(SDE_Innsyn,Database)
    SDE_Kart = "Database Connections\\AD@kart_GISSQL01.sde"
    landuse = "%s\\kart.SK.Feltpar25_NSFR" %(SDE_Kart)
    dtem25 = "%s\\kart.SK.DTEM25_SF" %(SDE_Kart)
    LogFile = "%s\\%s.log" % (arbeidsomr,sys.argv[0])

    scriptPath = "L:\\ArcGIS\\HydrologiskAnalyser\\Python\\script20100414\\"
    resMal = scriptPath + "hyp_hbv_mal.dbf"
    if not arcpy.Exists(resMal):
        arcpy.Addmessage("Tabellmalen %s finnes ikke" %(resMal))
        sys.exit(1)

    env.workspace = arbeidsomr
    test = 1
    for iSta in range(1, 7):
        sta = StaFile.readline()
        print(sta)
        stasjonsnr = sta.rstrip()
        print("%s :  %s"  %(iSta,stasjonsnr))
        Log(LogFile, "%s :  %s"  %(iSta,stasjonsnr))
        Tilrettelegg_Data(stasjonsnr,DDDParameterList,DDD_Output_List,arbeidsomr,fc_mstaFelt,fc_rivernet,grd_hydflowdir,grd_hydflowacc,landuse,dtem25,resMal,test,LogFile)
        Log(LogFile, "%s :  %s ferdig"  %(iSta,stasjonsnr))
    print("Skriptet er ferdig")


#***********************************************************************************
# If script runs independently call main.
# If it is imported as a module in an another script: don't call main.
#***********************************************************************************
if __name__ == '__main__':
    main()
#***********************************************************************************