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
def AreaDistributionRivernet(workspace,fc_msta_River,catchment,grd_hydflowdir,grd_hydflowacc,test,LogFile):

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

        # Set workspace
        arcpy.env.workspace = workspace

        # Set lokal variables
        grd_msta_River = os.path.join(workspace,"grd_msta_River")

        # Check if Riverentt is within nedb�rfeltet
        if int(arcpy.GetCount_management(fc_msta_River).getOutput(0)) > 0:

            #Sette extent til feltpolygon snappet med hydflowdir
            dsc_catchment = arcpy.Describe(catchment)
            extent_felt = dsc_catchment.extent
            env.extent = sett_snapextent(extent_felt, grd_hydflowdir)
            cellSize = arcpy.Describe(grd_hydflowdir).MeanCellHeight
            print("Satt snapextent")

            # Convert rivernet to raster
            arcpy.FeatureToRaster_conversion(fc_msta_River, "LTEMA", "HRiver", cellSize)
            # give all cells in the network tha river code
            River_grd = Con("HRiver", 3201)
            River_grd.save(grd_msta_River)
            print("rivernet convertet to raster")
            arcpy.BuildRasterAttributeTable_management(grd_msta_River)
            Rows = arcpy.SearchCursor(River_grd)
            #print(Rows)
            for row in Rows:
               countRiverHong = int(row.getValue("Count"))
               print("the number of river cells")
               print(countRiverHong)
			# extract flow acc by mask
            CatFlowAcc = ExtractByMask(grd_hydflowacc, catchment)
            CatFlowAcc.save(os.path.join(workspace,"CatFlowAcc"))
            print(" extract flow acc by catchment mask")
            arr = arcpy.RasterToNumPyArray(CatFlowAcc)
            brr = numpy.sort(arr, axis=None, kind = "mergesort")
            brr[:] = brr[::-1]
            thValue = brr[countRiverHong-1]
            print(thValue)
            ConAcc = "Value < %s" % (thValue)
            outCon = SetNull(CatFlowAcc, 1, ConAcc)
            #outCon.save(os.path.join(workspace,"outCon"))
            print("get river cells according to the flow acc")
            # extract flow dir to the river cells
            #CatFlowDir = ExtractByMask(grd_hydflowdir, outCon)
            CatFlowDir = Con(outCon, grd_hydflowdir)			
            CatFlowDir.save(os.path.join(workspace,"CatFlowDir"))
            print("get flow dir at the river cells")
            print(CatFlowDir)
            flowlen_diff = Int(FlowLength(os.path.join(workspace,"CatFlowDir"), "DOWNSTREAM", ""))
            flowlen_diff.save("%s\\flowlen_diff" % (workspace))
            flowlen_diff = "%s\\flowlen_diff" % (workspace)	

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "CatDir"
#arcpy.gp.FlowLength_sa("CatDir", "C:/Users/holi/Documents/ArcGIS/Default.gdb/FlowLen_CatD1", "DOWNSTREAM", "")
            print("Flowlength calculated")
            #arcpy.BuildRasterAttributeTable_management(flowlen_diff)
            print("Reell flowlengh in the rivernet calculated")
            arcpy.BuildRasterAttributeTable_management(flowlen_diff)

            #calculate statistics
            RiverStat = ZonalStatisticsAsTable(grd_msta_River, "VALUE", flowlen_diff, "RiverStatTab", "DATA", "ALL")
               
        else:
            LogTekst = "No Rivers within the Catchment"
            return LogTekst
            print(LogTekst)
            Log(LogFile,LogTekst)
    except:
        ErrorHandling(LogFile)
        sys.exit(9)
#***********************************************************************************

def Tilrettelegg_Data(stasjonsnr,DDDParameterList,DDD_Output_List,arbeidsomr,fc_mstaFelt,fc_rivernet,grd_hydflowdir,grd_hydflowacc,landuse,dtem25,resMal,test,LogFile):
    try:

        loggtekst = "\nMalestasjon: %s\n" % (stasjonsnr)
        print("Malestasjon: %s" % (stasjonsnr))

        for DDDParameter in DDDParameterList:

            print("calc DDDparameter: %s " %(DDDParameter))
            resultatkatalog = os.path.join(arbeidsomr,"resultat")
            if not os.path.exists(resultatkatalog):
               os.makedirs(resultatkatalog)

            ok_stnr = stasjonsnr.replace(".", "_")
            resultatGdb = os.path.join(arbeidsomr, "%s.gdb" % (ok_stnr))

            if DDDParameter == "River":
               utfil = os.path.join(resultatkatalog, "%s_river.txt" %(ok_stnr))

            # check resultfiles
            resOk = Resultat_Eksisterer(utfil)
            print("%s made? %s" %(utfil,resOk))

            #--- if resultfile and result gbg exist.
            if resOk:
                print("%s already calculated" % (stasjonsnr))
                loggtekst += "%s already calculated\n" % (stasjonsnr)
            else:
                msta_ws = resultatGdb

                # Creates geodatabase per station
                if not arcpy.Exists(resultatGdb):
                   arcpy.CreateFileGDB_management(os.path.dirname(resultatGdb), os.path.basename(resultatGdb))
                print("Created filegeodatabase %s" % (resultatGdb))

                env.extent = "MAXOF"

                # Get the catchment for the station
                msta_query = "\"STASJON_NR\" = '%s'" % (stasjonsnr)
                catchment = "%s\\msta_felt" % (msta_ws)
                if arcpy.Exists("lyr"):
                    arcpy.Delete_management("lyr")
                arcpy.MakeFeatureLayer_management(fc_mstaFelt, "lyr")
                arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", msta_query)
                if int(arcpy.GetCount_management("lyr").getOutput(0)) > 0:
                    arcpy.CopyFeatures_management("lyr", catchment)
                    print("Copied catchment polygon for %s" % (stasjonsnr))
                    #--- get the catchment polygon area
                    for row in arcpy.da.SearchCursor(catchment,("SHAPE@","FELTNR","STASJON_NR")):
                        catchmentarea = row[0].area
                    print("catchment area = %s m2" %(catchmentarea))
                    # already done <=10000000
                    #if ((catchmentarea <= 10000000) or (catchmentarea > 100000000)):
                    #   print "this catchment is already done or too big"
                    #   return None
                    #--- get the river net inside the catchment
                    fc_msta_River = os.path.join(msta_ws,"msta_River")
                    xy_tol=""

                    arcpy.Clip_analysis(fc_rivernet, catchment, fc_msta_River, xy_tol)
                    RiverLength = 0
                    for row in arcpy.da.SearchCursor(fc_msta_River,("SHAPE@")):
                        RiverLength += row[0].length
                    print("River lentgh = %s m" %(RiverLength))

                    #---- Create a distance dirtibution file for the River network
                    if DDDParameter == "River":
                       para = "river"
                       if "Statistics" in DDD_Output_List:
                           utfil = os.path.join(resultatkatalog, "%s_Stat.txt" %(ok_stnr))
                           resOk = Resultat_Eksisterer(utfil)
                           print("%s made? %s" %(utfil, resOk))
                           if (resOk):
                              return None
                       AreaDistributionRivernet(msta_ws,fc_msta_River,catchment,grd_hydflowdir,grd_hydflowacc,test,LogFile)
                       frekvenstabell = "%s\\flowlen_diff" % (msta_ws)
                       statistikktabell = os.path.join(msta_ws, "statistikk")
                       #if "AreaDistribution" in DDD_Output_List:
                       #    if arcpy.Exists(frekvenstabell):
                       #        CalculateAreaDistribution(frekvenstabell,statistikktabell,utfil,LogFile)
                       StatisticsRiver(para,utfil,RiverLength,LogFile)
                       print("DDD %s beregning ferdig" %(DDDParameter))
                else:
                     linje = "No features found for %s" % (stasjonsnr)
                     print(linje)
                     resultatfil = open(utfil, 'w')
                     resultatfil.write(linje)
                     resultatfil.close()

    except:
        ErrorHandling(LogFile)
        sys.exit(9)
#***********************************************************************************
def StatisticsRiver(para,utfil,RiverLength,LogFile):
    try:
        resultatfil = open(utfil, 'a')
        resultatfil.write("Statistics for %s\n" %para)
        resultatfil.write('\n')
        #FieldList = ["VALUE","COUNT","AREA", "MIN","MAX","RANGE","MEAN", "STD","SUM","VARIETY","MAJORITY","MINORITY","MEDIAN"]
        FieldList = ["MAX","MEAN","STD"]
        if arcpy.Exists("%sStatTab" %para):
            searchcur = arcpy.da.SearchCursor("%sStatTab" %para,(FieldList))
            for row in searchcur:
                resultatfil.write('LENGHT%s, %s\n' %(para,RiverLength))
                for n in range(0,len(FieldList)):
                    resultatfil.write('%s%s, %s\n' %(FieldList[n],para,row[n]))
        resultatfil.write('\n')
        resultatfil.close()
    except:
        ErrorHandling(LogFile)
        sys.exit(9)
# Hovedskript
#***********************************************************************************
def main():

    #--- INPUT ARGUMENTER
    msta = sys.argv[1]
    #msta = 101.1
    #datotag = "20161115"                        # dette er bare en tag
    arbeidsomr = "C:\\Temp\\FlowLength"  # katalogen m� finnes
	#arbeidsomr = "C:\\Temp\\DDD_%s" %(datotag)  # katalogen m� finnes
    #mstaliste = ['6.71.0','12.114.0','12.150.0','12.286.0','12.290.0','15.49.0','16.140.0','36.9.0','78.8.0','107.3.0','121.20.0','163.5.0','234.1','311.6.0','313.1']          # Stasjons liste

    #check if stasjonsnr er format xx.x.0
    if msta.count(".") == 1:
        msta = "%s.0" %msta

    mstaliste = []
    mstaliste.append(msta)
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
    teller = 0
    for stasjonsnr in mstaliste:
        teller += 1
        print("%s :  %s"  %(teller,stasjonsnr))
        Log(LogFile, "%s :  %s"  %(teller,stasjonsnr))
        Tilrettelegg_Data(stasjonsnr,DDDParameterList,DDD_Output_List,arbeidsomr,fc_mstaFelt,fc_rivernet,grd_hydflowdir,grd_hydflowacc,landuse,dtem25,resMal,test,LogFile)
        Log(LogFile, "%s :  %s ferdig"  %(teller,stasjonsnr))
    print("Skriptet er ferdig")


#***********************************************************************************
# If script runs independently call main.
# If it is imported as a module in an another script: don't call main.
#***********************************************************************************
if __name__ == '__main__':
    main()
#***********************************************************************************