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

        NUM_OF_SENSORS = 4
        NUM_OF_ACTUATORS = 2
        self.sensorHandles = np.repeat(-1, NUM_OF_SENSORS)
        self.sensorValues = np.repeat(float('nan'), NUM_OF_SENSORS)
        self.actuatorHandles = np.repeat(-1, NUM_OF_ACTUATORS)
        self.actuatorValues = np.repeat(float('nan'), NUM_OF_ACTUATORS)

        self.observationNumber = 0
        self.oldObservationNumber = 0
        self.oldActionChosen = None

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

        if -1 not in self.sensorHandles:
            hour = self.dataExchange.hour(state)
            month = self.dataExchange.month(state)
            day = self.dataExchange.day_of_month(state)
            minute = self.dataExchange.minutes(state)

            self.sensorValues[0] = self.dataExchange.get_variable_value(state, self.sensorHandles[0]) 
            self.sensorValues[1] = self.dataExchange.get_variable_value(state, self.sensorHandles[1])
            self.sensorValues[2] = self.dataExchange.get_meter_value(state, self.sensorHandles[2]) 
            self.sensorValues[3] = self.dataExchange.get_meter_value(state, self.sensorHandles[3]) 

            print(str(month) +
                ":" + str(day) +
                ":" + str(hour) + 
                ":" + str(minute) + 
                "__" + str(self.sensorValues[0]) + 
                "__" + str(self.sensorValues[1]) + 
                "__" + str(self.sensorValues[2]) + 
                "__" + str(self.sensorValues[3]))

            observation = [self.sensorValues[0], self.sensorValues[1], hour]
            # if the previous observation is taken we want to overwrite the value so the agent always gets the latest info
            self.observationQueue.put_overwrite(observation)

            heatingElecConsumption = self.sensorValues[2]
            # print(heatingElecConsumption)
            self.heatingElecDataQueue.put_overwrite(heatingElecConsumption)

            self.observationNumber += 1 # a new observation is already available! Wait for the new action the agent will soon issue
        return

    def set_actuators(self, action, state): 
        match int(action.item(0)): 
            case 0:
                self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 0.0)
            case 1:
                self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], 1.0)

        match int(action.item(1)): 
            case 0:
                self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 15.0)
            case 1:
                self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], 25.0)

        self.actuatorValues[0] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[0])
        print(self.actuatorValues[0])
        self.actuatorValues[1] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[1])
        print("_" + str(self.actuatorValues[1]))
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
            if self.observationNumber > self.oldObservationNumber: 
                # a new observation is already made and read by agent so no further action needed for that one; 
                # wait for the new action soon to be issued by agent
                self.oldObservationNumber = self.observationNumber
                self.printApiFlagIfRaised(state)

                try: 
                    # wait until the values are available
                    actionChosen = self.actionQueue.get_wait()
                    self.oldActionChosen = actionChosen
                    self.set_actuators(actionChosen, state)
                except Empty:
                    print("actuatorValuesToSet = self.actionQueue.get_wait() raises Empty exception")
            else:
                # a new observation has not been made and read by agent;
                # keep sending the old one
                self.set_actuators(self.oldActionChosen, state)

        return

