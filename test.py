import sys
import os
from eppy import modeleditor
from eppy.modeleditor import IDF
from pyenergyplus.api import EnergyPlusAPI
# from pyenergyplus.datatransfer import DataExchange

# iddPath = "C:/EnergyPlusV9-5-0/Energy+.idd" 
iddPath = "C:/EnergyPlusV9-4-0/Energy+.idd" 

idfPath = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPreset.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/IECC_OfficeSmall_STD2018_SanDiego.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/ASHRAE901_OfficeSmall_STD2019_SanDiego.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/ASHRAE901_OfficeSmall_STD2019_NewYork.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/US+MF+CZ3C+elecres+heatedbsmt+IECC_2021.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/US+MF+CZ4A+elecres+unheatedbsmt+IECC_2021.idf"

epwPath = "C:/Users/Eppy/Documents/WeatherFiles/USA_CA_San.Diego-Lindbergh.Field.722900_TMY3.epw"
# epwPath = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"

outputDir = os.path.dirname(idfPath)  + '/output'

print(outputDir)

IDF.setiddname(iddPath)
idf = IDF(idfPath, epwPath)

#idf.printidf()
#print(idf.idfobjects['BUILDING']) # put the name of the object you'd like to look at in brackets

# fname = idf.idfname
# options = {
#     # 'ep_version':idfversionstr, # runIDFs needs the version number
#         # idf.run does not need the above arg
#     'output_prefix':os.path.basename(fname).split('.')[0],
#     # 'output_suffix':'C',
#     'output_directory':os.path.dirname(fname)  + '/output',
#     'readvars':True,
#     # 'expandobjects':True
#     }
# idf.run(**options)

# =================================================

energyplus_api = EnergyPlusAPI()

# dataExchange = energyplus_api.exchange
# dataExchange.get_variable_handle()

selfenergyplus_state = energyplus_api.state_manager.new_state()
runtime = energyplus_api.runtime

exitCode = runtime.run_energyplus(selfenergyplus_state, ['-d', outputDir, '-w', epwPath, idfPath])
print("exit code (zero is success): " + str(exitCode))

