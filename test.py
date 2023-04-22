import sys
import os
from eppy import modeleditor
from eppy.modeleditor import IDF
from pyenergyplus.api import EnergyPlusAPI
# from pyenergyplus.datatransfer import DataExchange

iddPath = "C:/EnergyPlusV9-4-0/Energy+.idd" 
# iddPath = "C:/EnergyPlusV9-5-0/Energy+.idd" 

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

# IDF.setiddname(iddPath)
# idf = IDF(idfPath, epwPath)
# print(idf.idfobjects['TIMESTEP']) # put the name of the object you'd like to look at in brackets

# =================================================

energyplus_api = EnergyPlusAPI()
dataExchange = energyplus_api.exchange

energyplus_state = energyplus_api.state_manager.new_state()
runtime = energyplus_api.runtime

counter = 0
def collect_observations(state):
    global counter
    if counter == 0: 
        csvData = dataExchange.list_available_api_data_csv(energyplus_state)
        with open(os.path.join(outputDir, "availableApiData.csv"), 'wb') as temp_file:
            temp_file.write(csvData)
        counter = 1
    handle = dataExchange.get_variable_handle(state, "Zone Mean Air Temperature", "BLOCK1:ZONE1")
    if handle >= 0:
        hour = dataExchange.hour(state)
        sensorValue = dataExchange.get_variable_value(state, handle) 
        print(str(hour) + ":" + str(sensorValue))
    return

runtime.callback_end_zone_timestep_after_zone_reporting(energyplus_state, collect_observations)

exitCode = runtime.run_energyplus(energyplus_state, ['-d', outputDir, '-w', epwPath, idfPath])
print("exit code (zero is success): " + str(exitCode))



