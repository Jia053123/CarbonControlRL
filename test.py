import sys
import os
from eppy import modeleditor
from eppy.modeleditor import IDF
from pyenergyplus.api import EnergyPlusAPI

iddPath = "C:/EnergyPlusV9-4-0/Energy+.idd" 
# iddPath = "C:/EnergyPlusV9-5-0/Energy+.idd" 

idfPath = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPresetMA.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/IECC_OfficeSmall_STD2018_SanDiego.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/ASHRAE901_OfficeSmall_STD2019_SanDiego.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/ASHRAE901_OfficeSmall_STD2019_NewYork.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/US+MF+CZ3C+elecres+heatedbsmt+IECC_2021.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/US+MF+CZ4A+elecres+unheatedbsmt+IECC_2021.idf"

# epwPath = "C:/Users/Eppy/Documents/WeatherFiles/USA_CA_San.Diego-Lindbergh.Field.722900_TMY3.epw"
epwPath = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"

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




hasWrittenCSV = False
def writeAvailableApiDataFile(run=True):
    global hasWrittenCSV
    if run:
        if hasWrittenCSV == False: 
            print("writing CSV...")
            csvPath = os.path.join(outputDir, "availableApiData.csv")
            try:
                os.remove(csvPath)
            except OSError:
                pass
            csvData = dataExchange.list_available_api_data_csv(energyplus_state)
            with open(csvPath, 'wb') as temp_file:
                temp_file.write(csvData)
            hasWrittenCSV = True

def printApiFlagIfRaised(state):
        flag = dataExchange.api_error_flag(state)
        if flag:
            print("error flag raised")

sensorHandle1 = -1
sensorHandle2 = -1
def collect_observations(state):
    global sensorHandle1
    global sensorHandle2
    if not dataExchange.api_data_fully_ready(state):
        return
    writeAvailableApiDataFile(False) # Change to True to write the file in output folder
    
    warmUpFlag = dataExchange.warmup_flag(state)

    if sensorHandle1 < 0 or sensorHandle2 < 0: 
        sensorHandle1 = dataExchange.get_variable_handle(state, 
                                                        "Zone Mean Air Temperature", 
                                                        "BLOCK1:ZONE1")
        sensorHandle2 = dataExchange.get_variable_handle(state, 
                                                        "System Node Temperature", 
                                                        "BOILER WATER OUTLET NODE")
    else: 
        hour = dataExchange.hour(state)
        minute = dataExchange.minutes(state)

        sensorValue1 = dataExchange.get_variable_value(state, sensorHandle1) 
        sensorValue2 = dataExchange.get_variable_value(state, sensorHandle2) 

        print(str(hour) + ":" + str(minute) + "__" + str(sensorValue1) + "__" + str(sensorValue2))
    return

actuatorHandle1 = -1
actuatorHandle2 = -1
def send_actions(state):
    global actuatorHandle1
    global actuatorHandle2
    if not dataExchange.api_data_fully_ready(state):
        return
    if actuatorHandle1 < 0: 
        actuatorHandle1 = dataExchange.get_actuator_handle(state, 
                                                           "Schedule:Compact", 
                                                           "Schedule Value", 
                                                           "HOT WATER FLOW SET POINT TEMPERATURE: ALWAYS 80.0 C")
        actuatorHandle2 = dataExchange.get_actuator_handle(state, 
                                                           "Schedule:Compact", 
                                                           "Schedule Value", 
                                                           "BLOCK1:ZONE1 HEATING SETPOINT SCHEDULE")
    else:
        printApiFlagIfRaised(state)
        
        # actuatorValue2 = dataExchange.get_actuator_value(state, actuatorHandle2)
        # print("Set Point: " + str(actuatorValue2))

        dataExchange.set_actuator_value(state, actuatorHandle1, 80.0)
        dataExchange.set_actuator_value(state, actuatorHandle2, 20.0)
    return

# runtime.callback_begin_system_timestep_before_predictor(energyplus_state, send_actions)
runtime.callback_after_predictor_after_hvac_managers(energyplus_state, send_actions)
runtime.callback_end_zone_timestep_after_zone_reporting(energyplus_state, collect_observations)

exitCode = runtime.run_energyplus(energyplus_state, ['-d', outputDir, '-w', epwPath, idfPath])
print("exit code (zero is success): " + str(exitCode))



