import numpy as np
from pyenergyplus.api import EnergyPlusAPI
from QueueOfOne import QueueOfOne
from queue import Empty, Full

class ActionObservationManager: 
    def __init__(self, dataExchange, actionQueue: QueueOfOne, observationQueue:QueueOfOne, outputDir):
        self.dataExchange = dataExchange
        self.outputDir = outputDir

        self.actionQueue: QueueOfOne = actionQueue
        self.observationQueue: QueueOfOne = observationQueue

        self.sensorHandles = np.repeat(-1, 5)
        self.sensorValues = np.repeat(float('nan'), 5)
        self.actuatorHandles = np.repeat(-1, 3)
        self.actuatorValues = np.repeat(float('nan'), 3)

        self.warmUpFlag = True
        return

    def printApiFlagIfRaised(self, state):
        flag = self.dataExchange.api_error_flag(state)
        if flag:
            print("error flag raised")
        return

    def collect_observations(self, state):
        self.warmUpFlag = self.dataExchange.warmup_flag(state)
        
        if not self.dataExchange.api_data_fully_ready(state):
            return
 
        if -1 in self.sensorHandles:
            self.sensorHandles[0] = self.dataExchange.get_variable_handle(state, 
                                                                        "Zone Mean Air Temperature", 
                                                                        "BLOCK1:ZONE1")
            self.sensorHandles[1] = self.dataExchange.get_variable_handle(state, 
                                                                        "Site Outdoor Air Drybulb Temperature", 
                                                                        "ENVIRONMENT")
            self.sensorHandles[2] = self.dataExchange.get_meter_handle(state, 
                                                                    "Boiler:Heating:Electricity")
            self.sensorHandles[3] = self.dataExchange.get_meter_handle(state, 
                                                                    "Pumps:Electricity")
            self.sensorHandles[4] = self.dataExchange.get_variable_handle(state, 
                                                                        "System Node Temperature", 
                                                                        "BOILER WATER OUTLET NODE")
        if -1 not in self.sensorHandles:
            hour = self.dataExchange.hour(state)
            minute = self.dataExchange.minutes(state)

            self.sensorValues[0] = self.dataExchange.get_variable_value(state, self.sensorHandles[0]) 
            self.sensorValues[1] = self.dataExchange.get_variable_value(state, self.sensorHandles[1]) 
            self.sensorValues[2] = self.dataExchange.get_meter_value(state, self.sensorHandles[2]) 
            self.sensorValues[3] = self.dataExchange.get_meter_value(state, self.sensorHandles[3]) 
            self.sensorValues[4] = self.dataExchange.get_variable_value(state, self.sensorHandles[4]) 

            # print(str(hour) + 
            #     ":" + str(minute) + 
            #     "__" + str(self.sensorValues[0]) + 
            #     "__" + str(self.sensorValues[1]) + 
            #     "__" + str(self.sensorValues[2]) + 
            #     "__" + str(self.sensorValues[3]) + 
            #     "__" + str(self.sensorValues[4]))
            
            observation = [self.sensorValues[2], hour]
            # if the previous observation is taken we want to overwrite the value so the agent always gets the latest info
            self.observationQueue.put_overwrite(observation)
        return


    def send_actions(self, state):
        self.warmUpFlag = self.dataExchange.warmup_flag(state)
        if self.warmUpFlag:
            return
        if not self.dataExchange.api_data_fully_ready(state):
            return
        if -1 in self.actuatorHandles: 
            self.actuatorHandles[0] = self.dataExchange.get_actuator_handle(state, 
                                                                            "Schedule:Compact", 
                                                                            "Schedule Value", 
                                                                            "HOT WATER FLOW SET POINT TEMPERATURE: ALWAYS 80.0 C")
            self.actuatorHandles[1] = self.dataExchange.get_actuator_handle(state, 
                                                                            "Schedule:Compact", 
                                                                            "Schedule Value", 
                                                                            "BLOCK1:ZONE1 HEATING SETPOINT SCHEDULE")
            self.actuatorHandles[2] = self.dataExchange.get_actuator_handle(state, 
                                                                            "Schedule:Compact", 
                                                                            "Schedule Value", 
                                                                            "BLOCK1:ZONE1 COOLING SETPOINT SCHEDULE")
        else:
            self.printApiFlagIfRaised(state)
            
            self.actuatorValues[0] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[0])
            self.actuatorValues[1] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[1])
            self.actuatorValues[2] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[2])
            # print("Set Point: " + str(self.actuatorValues[0]))
            # print("Set Point: " + str(self.actuatorValues[1]))
            # print("Set Point: " + str(self.actuatorValues[2]))

            try: 
                # wait until the values are available
                actionChosen = self.actionQueue.get_wait() #[0]
                match int(actionChosen): 
                    case 0:
                        print("setpoint: 15")
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 80.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 15.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[2], 31.0)
                    case 1:
                        print("setpoint: 0025")
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 80.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 25.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[2], 31.0)

            except Empty:
                print("actuatorValuesToSet = self.actionQueue.get_wait() raises Empty exception")
        return
