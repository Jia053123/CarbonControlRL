import numpy as np
from pyenergyplus.api import EnergyPlusAPI
from QueueOfOne import QueueOfOne
from queue import Empty, Full

class ActionObservationManager: 
    def __init__(self, dataExchange, actionQueue: QueueOfOne, observationQueue:QueueOfOne, heatingElecDataQueue:QueueOfOne, outputDir):
        self.dataExchange = dataExchange
        self.outputDir = outputDir

        self.actionQueue: QueueOfOne = actionQueue
        self.observationQueue: QueueOfOne = observationQueue
        self.heatingElecDataQueue: QueueOfOne = heatingElecDataQueue

        NUM_OF_SENSORS = 3
        NUM_OF_ACTUATORS = 2
        self.sensorHandles = np.repeat(-1, NUM_OF_SENSORS)
        self.sensorValues = np.repeat(float('nan'), NUM_OF_SENSORS)
        self.actuatorHandles = np.repeat(-1, NUM_OF_ACTUATORS)
        self.actuatorValues = np.repeat(float('nan'), NUM_OF_ACTUATORS)

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
            self.sensorHandles[1] = self.dataExchange.get_meter_handle(state, 
                                                                    "Boiler:Heating:Electricity")
            self.sensorHandles[2] = self.dataExchange.get_meter_handle(state, 
                                                                    "Pumps:Electricity")

        if -1 not in self.sensorHandles:
            hour = self.dataExchange.hour(state)

            self.sensorValues[0] = self.dataExchange.get_variable_value(state, self.sensorHandles[0]) 
            self.sensorValues[1] = self.dataExchange.get_meter_value(state, self.sensorHandles[1]) 
            self.sensorValues[2] = self.dataExchange.get_meter_value(state, self.sensorHandles[2]) 

            # print(str(hour) + 
            #     ":" + str(minute) + 
            #     "__" + str(self.sensorValues[0]) + 
            #     "__" + str(self.sensorValues[1]) + 
            #     "__" + str(self.sensorValues[2]) + 
            #     "__" + str(self.sensorValues[3]) + 
            #     "__" + str(self.sensorValues[4]))

            observation = [self.sensorValues[0], hour]
            # if the previous observation is taken we want to overwrite the value so the agent always gets the latest info
            self.observationQueue.put_overwrite(observation)

            heatingElecConsumption = self.sensorValues[1] + self.sensorValues[2]
            # print(heatingElecConsumption)
            self.heatingElecDataQueue.put_overwrite(heatingElecConsumption)
        return


    def send_actions(self, state):
        self.warmUpFlag = self.dataExchange.warmup_flag(state)
        if self.warmUpFlag:
            return
        if not self.dataExchange.api_data_fully_ready(state):
            return
        if -1 in self.actuatorHandles: 
            self.actuatorHandles[0] = self.dataExchange.get_actuator_handle(state, 
                                                                            "Plant Component Boiler:HotWater", 
                                                                            "On/Off Supervisory", 
                                                                            "BOILER")
            self.actuatorHandles[1] = self.dataExchange.get_actuator_handle(state, 
                                                                            "Zone Temperature Control", 
                                                                            "Heating Setpoint", 
                                                                            "BLOCK1:ZONE1")

        else:
            self.printApiFlagIfRaised(state)
            
            self.actuatorValues[0] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[0])
            self.actuatorValues[1] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[1])

            # print("On or Off: " + str(self.actuatorValues[0]))
            # print("Set Point: " + str(self.actuatorValues[1]))

            try: 
                # wait until the values are available
                actionChosen = self.actionQueue.get_wait()
                match int(actionChosen): 
                    case 0:
                        print("00, 15")
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 0.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 15.0)
                    case 1:
                        print("11, 15")
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 1.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 15.0)
                    case 2:
                        print("00, 0025")
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 0.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 25.0)
                    case 3:
                        print("11, 0025")
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 1.0)
                        self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 25.0)

            except Empty:
                print("actuatorValuesToSet = self.actionQueue.get_wait() raises Empty exception")
        return

