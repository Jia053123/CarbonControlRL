import os
from pyenergyplus.api import EnergyPlusAPI

# idfPath = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPresetCA_Electric.idf"
idfPath = "C:/Users/Eppy/Documents/IDFs/office1111222.idf"
# EPW_PATH = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"
# EPW_PATH = "C:/Users/Eppy/Documents/WeatherFiles/USA_CA_San.Diego-Lindbergh.Field.722900_TMY3.epw"
EPW_PATH = "C:/Users/Eppy/Documents/WeatherFiles/KSFO-San_Francisco-2019.epw"
outputDir = os.path.dirname(idfPath)  + '/output'

energyplus_api = EnergyPlusAPI()
dataExchange = energyplus_api.exchange

energyplus_state = energyplus_api.state_manager.new_state()
runtime = energyplus_api.runtime

totalReward = 0

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

variableHandle1 = -1
variableHandle2 = -1
meterHandle3 = -1
meterHandle4 = -1
variableHandle5 = -1
def collect_observations(state):
    global variableHandle1
    global variableHandle2
    global meterHandle3
    global meterHandle4
    global variableHandle5
    global totalReward
    if not dataExchange.api_data_fully_ready(state):
        return
    writeAvailableApiDataFile(False) # Change to True to write the file in output folder
    
    warmUpFlag = dataExchange.warmup_flag(state)

    if variableHandle1<0: #or variableHandle2<0 or meterHandle3<0 or meterHandle4<0 or variableHandle5<0: 
        variableHandle1 = dataExchange.get_variable_handle(state, 
                                                           "Zone Mean Air Temperature", 
                                                           "BLOCK1:ZONE1")
        variableHandle2 = dataExchange.get_variable_handle(state, 
                                                           "Site Outdoor Air Drybulb Temperature", 
                                                           "ENVIRONMENT")
        meterHandle3 = dataExchange.get_meter_handle(state, 
                                                     "Boiler:Heating:Electricity")
        meterHandle4 = dataExchange.get_meter_handle(state, 
                                                     "Pumps:Electricity")
        # variableHandle5 = dataExchange.get_variable_handle(state, 
        #                                                    "System Node Temperature", 
        #                                                    "BOILER WATER OUTLET NODE")
        variableHandle5 = dataExchange.get_variable_handle(state, 
                                                           "Boiler Heating Energy", 
                                                           "BOILER")
    else: 
        month = dataExchange.month(state)
        day = dataExchange.day_of_month(state)
        hour = dataExchange.hour(state)
        minute = dataExchange.minutes(state)

        variableValue1 = dataExchange.get_variable_value(state, variableHandle1) 
        variableValue2 = dataExchange.get_variable_value(state, variableHandle2) 
        meterValue3 = dataExchange.get_meter_value(state, meterHandle3) 
        meterValue4 = dataExchange.get_meter_value(state, meterHandle4) 
        variableValue5 = dataExchange.get_variable_value(state, variableHandle5) 

        # if meterValue4 > 0.1: 
        print(str(month) +
            ":" + str(day) + 
            ":" + str(hour) + 
            ":" + str(minute) + 
            "__" + str(variableValue1) + 
            #   "__" + str(variableValue2) + 
            "__" + str(meterValue3) + 
            "__" + str(meterValue4) + 
            "__" + str(variableValue5))
        
        totalReward = totalReward - (meterValue3 + meterValue4)
        
    return

actuatorHandle1 = -1
actuatorHandle2 = -1
actuatorHandle3 = -1
def send_actions(state):
    global actuatorHandle1
    global actuatorHandle2
    global actuatorHandle3
    if not dataExchange.api_data_fully_ready(state):
        return
    if actuatorHandle1 < 0: 
        actuatorHandle1 = dataExchange.get_actuator_handle(state, 
                                                    "Plant Component Boiler:HotWater", 
                                                    "On/Off Supervisory", 
                                                    "BOILER")
        # actuatorHandle1 = dataExchange.get_actuator_handle(state, 
        #                                                    "System Node Setpoint", 
        #                                                    "Temperature Setpoint", 
        #                                                    "BOILER WATER INLET NODE")
                                                        #    "HW LOOP SUPPLY SIDE INLET")
        # actuatorHandle1 = dataExchange.get_actuator_handle(state, 
        #                                                    "Schedule:Compact", 
        #                                                    "Schedule Value", 
        #                                                    "HOT WATER FLOW SET POINT TEMPERATURE: ALWAYS 30.0 C")
        actuatorHandle2 = dataExchange.get_actuator_handle(state, 
                                                           "Zone Temperature Control", 
                                                           "Heating Setpoint", 
                                                           "BLOCK1:ZONE1")
    #     actuatorHandle3 = dataExchange.get_actuator_handle(state, 
    #                                                        "Schedule:Compact", 
    #                                                        "Schedule Value", 
    #                                                        "BLOCK1:ZONE1 COOLING SETPOINT SCHEDULE")
    else:
        printApiFlagIfRaised(state)
        
        actuatorValue1 = dataExchange.get_actuator_value(state, actuatorHandle1)
        # actuatorValue2 = dataExchange.get_actuator_value(state, actuatorHandle2)
        # actuatorValue3 = dataExchange.get_actuator_value(state, actuatorHandle3)
        # print("Set Point: " + str(actuatorValue1))
        # print("Set Point: " + str(actuatorValue2))
        # print("Set Point: " + str(actuatorValue3))

        dataExchange.set_actuator_value(state, actuatorHandle1, 1.0)
        dataExchange.set_actuator_value(state, actuatorHandle2, 25.0)
        # dataExchange.set_actuator_value(state, actuatorHandle3, 31.0)
    return

# runtime.callback_begin_system_timestep_before_predictor(energyplus_state, send_actions)
runtime.callback_after_predictor_after_hvac_managers(energyplus_state, send_actions)
# runtime.callback_inside_system_iteration_loop(energyplus_state, send_actions)
runtime.callback_end_zone_timestep_after_zone_reporting(energyplus_state, collect_observations)

exitCode = runtime.run_energyplus(energyplus_state, ['-d', outputDir, '-w', EPW_PATH, idfPath])

print("exit code (zero is success): " + str(exitCode))

print("simulated reward: " + str(totalReward))

