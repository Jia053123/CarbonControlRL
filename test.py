import sys
import os
from eppy import modeleditor
from eppy.modeleditor import IDF

#iddfile = "C:/EnergyPlusV9-4-0/Energy+.idd" 
iddfile = "C:/EnergyPlusV9-5-0/Energy+.idd" 

#idfname = "C:/Users/Eppy/Documents/IDFs/ASHRAE901_OfficeSmall_STD2019_NewYork.idf"
idfname = "C:/Users/Eppy/Documents/IDFs/US+MF+CZ4A+elecres+unheatedbsmt+IECC_2021.idf"

epwname = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"

IDF.setiddname(iddfile)
idf = IDF(idfname, epwname)

#idf.printidf()
#print(idf.idfobjects['BUILDING']) # put the name of the object you'd like to look at in brackets

fname = idf.idfname
options = {
    # 'ep_version':idfversionstr, # runIDFs needs the version number
        # idf.run does not need the above arg
    'output_prefix':os.path.basename(fname).split('.')[0],
    # 'output_suffix':'C',
    'output_directory':os.path.dirname(fname)  + '/output',
    # 'readvars':True,
    # 'expandobjects':True
    }
idf.run(**options)

