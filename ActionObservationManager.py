import os
import numpy as np
from pyenergyplus.api import EnergyPlusAPI
from queue import Queue, Empty, Full

class ActionObservationManager: 
    def __init__(self, dataExchange, actionQueue: Queue, observationQueue:Queue, outputDir):
        self.dataExchange = dataExchange
        self.outputDir = outputDir

    hasWrittenCSV = False
    def writeAvailableApiDataFile(self, state, run=True):
        global hasWrittenCSV
        if run:
            if hasWrittenCSV == False: 
                print("writing CSV...")
                csvPath = os.path.join(self.outputDir, "availableApiData.csv")
                try:
                    os.remove(csvPath)
                except OSError:
                    pass
                csvData = self.dataExchange.list_available_api_data_csv(state)
                with open(csvPath, 'wb') as temp_file:
                    temp_file.write(csvData)
                hasWrittenCSV = True

    def printApiFlagIfRaised(self, state):
            flag = self.dataExchange.api_error_flag(state)
            if flag:
                print("error flag raised")

    variableHandle1 = -1
    variableHandle2 = -1
    meterHandle3 = -1
    meterHandle4 = -1
    variableHandle5 = -1
    def collect_observations(self, state):
        global variableHandle1
        global variableHandle2
        global meterHandle3
        global meterHandle4
        global variableHandle5
        if not self.dataExchange.api_data_fully_ready(state):
            return
        self.writeAvailableApiDataFile(False) # Change to True to write the file in output folder
        
        warmUpFlag = self.dataExchange.warmup_flag(state)

        if variableHandle1<0 or variableHandle2<0 or meterHandle3<0 or meterHandle4<0 or variableHandle5<0: 
            variableHandle1 = self.dataExchange.get_variable_handle(state, 
                                                                    "Zone Mean Air Temperature", 
                                                                    "BLOCK1:ZONE1")
            variableHandle2 = self.dataExchange.get_variable_handle(state, 
                                                                    "Site Outdoor Air Drybulb Temperature", 
                                                                    "ENVIRONMENT")
            meterHandle3 = self.dataExchange.get_meter_handle(state, 
                                                              "Boiler:Heating:Electricity")
            meterHandle4 = self.dataExchange.get_meter_handle(state, 
                                                              "Pumps:Electricity")
            variableHandle5 = self.dataExchange.get_variable_handle(state, 
                                                                    "System Node Temperature", 
                                                                    "BOILER WATER OUTLET NODE")
        else: 
            hour = self.dataExchange.hour(state)
            minute = self.dataExchange.minutes(state)

            variableValue1 = self.dataExchange.get_variable_value(state, variableHandle1) 
            variableValue2 = self.dataExchange.get_variable_value(state, variableHandle2) 
            meterValue3 = self.dataExchange.get_meter_value(state, meterHandle3) 
            meterValue4 = self.dataExchange.get_meter_value(state, meterHandle4) 
            variableValue5 = self.dataExchange.get_variable_value(state, variableHandle5) 

            print(str(hour) + 
                ":" + str(minute) + 
                "__" + str(variableValue1) + 
                "__" + str(variableValue2) + 
                "__" + str(meterValue3) + 
                "__" + str(meterValue4) + 
                "__" + str(variableValue5))
            
        return

    actuatorHandle1 = -1
    actuatorHandle2 = -1
    actuatorHandle3 = -1
    def send_actions(self, state):
        global actuatorHandle1
        global actuatorHandle2
        global actuatorHandle3
        if not self.dataExchange.api_data_fully_ready(state):
            return
        if actuatorHandle1 < 0: 
            actuatorHandle1 = self.dataExchange.get_actuator_handle(state, 
                                                                    "Schedule:Compact", 
                                                                    "Schedule Value", 
                                                                    "HOT WATER FLOW SET POINT TEMPERATURE: ALWAYS 80.0 C")
            actuatorHandle2 = self.dataExchange.get_actuator_handle(state, 
                                                                    "Schedule:Compact", 
                                                                    "Schedule Value", 
                                                                    "BLOCK1:ZONE1 HEATING SETPOINT SCHEDULE")
            actuatorHandle3 = self.dataExchange.get_actuator_handle(state, 
                                                                    "Schedule:Compact", 
                                                                    "Schedule Value", 
                                                                    "BLOCK1:ZONE1 COOLING SETPOINT SCHEDULE")
        else:
            self.printApiFlagIfRaised(state)
            
            actuatorValue1 = self.dataExchange.get_actuator_value(state, actuatorHandle1)
            actuatorValue2 = self.dataExchange.get_actuator_value(state, actuatorHandle2)
            actuatorValue3 = self.dataExchange.get_actuator_value(state, actuatorHandle3)
            print("Set Point: " + str(actuatorValue1))
            print("Set Point: " + str(actuatorValue2))
            print("Set Point: " + str(actuatorValue3))

            self.dataExchange.set_actuator_value(state, actuatorHandle1, 80.0)
            self.dataExchange.set_actuator_value(state, actuatorHandle2, 20.0)
            self.dataExchange.set_actuator_value(state, actuatorHandle3, 31.0)
        return
