import numpy as np
from pyenergyplus.api import EnergyPlusAPI
from QueueOfOne import QueueOfOne
from queue import Empty, Full
import ControlPanel
from info_for_agent import CarbonPredictor
from ComfortMetrics import calcComfortMetric

class ActionObservationManager: 
    def __init__(self, dataExchange, actionQueue: QueueOfOne, observationQueue:QueueOfOne, heatingElecDataQueue:QueueOfOne, outputDir):
        self.dataExchange = dataExchange
        self.outputDir = outputDir

        self.actionQueue: QueueOfOne = actionQueue
        self.observationQueue: QueueOfOne = observationQueue
        self.rewardDataQueue: QueueOfOne = heatingElecDataQueue

        NUM_OF_SENSORS = 10
        NUM_OF_ACTUATORS = 2
        self.sensorHandles = np.repeat(-1, NUM_OF_SENSORS)
        self.sensorValues = np.repeat(float('nan'), NUM_OF_SENSORS)
        self.actuatorHandles = np.repeat(-1, NUM_OF_ACTUATORS)
        self.actuatorValues = np.repeat(float('nan'), NUM_OF_ACTUATORS)

        self.observationNumber = 0
        self.oldObservationNumber = 0
        self.oldActionChosen = None

        self.carbonPredictor = CarbonPredictor()

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
                                                                          "Boiler Heating Energy", 
                                                                          "BOILER")
            self.sensorHandles[5] = self.dataExchange.get_variable_handle(state, 
                                                                          "System Node Temperature", 
                                                                          "BOILER WATER INLET NODE")
            self.sensorHandles[6] = self.dataExchange.get_variable_handle(state, 
                                                                          "System Node Temperature", 
                                                                          "BOILER WATER OUTLET NODE")
            self.sensorHandles[7] = self.dataExchange.get_variable_handle(state, 
                                                                          "System Node Mass Flow Rate", 
                                                                          "BOILER WATER INLET NODE")
            self.sensorHandles[8] = self.dataExchange.get_variable_handle(state, 
                                                                          "System Node Mass Flow Rate", 
                                                                          "BOILER WATER OUTLET NODE")
            self.sensorHandles[9] = self.dataExchange.get_meter_handle(state, 
                                                                       "Heating:Electricity")
            

        if -1 not in self.sensorHandles:
            year = self.dataExchange.year(state)
            hour = self.dataExchange.hour(state)
            month = self.dataExchange.month(state)
            day = self.dataExchange.day_of_month(state)
            minute = self.dataExchange.minutes(state)

            self.sensorValues[0] = self.dataExchange.get_variable_value(state, self.sensorHandles[0]) 
            self.sensorValues[1] = self.dataExchange.get_variable_value(state, self.sensorHandles[1])
            self.sensorValues[2] = self.dataExchange.get_meter_value(state, self.sensorHandles[2]) 
            self.sensorValues[3] = self.dataExchange.get_meter_value(state, self.sensorHandles[3]) 
            self.sensorValues[4] = self.dataExchange.get_variable_value(state, self.sensorHandles[4]) 

            print(str(month) +
                ":" + str(day) +
                ":" + str(hour) + 
                ":" + str(minute) + 
                "__" + str(self.sensorValues[0]) + 
                "__" + str(self.sensorValues[1]) + 
                "__" + str(self.sensorValues[2]) + 
                "__" + str(self.sensorValues[3]))

            carbonRate = self.carbonPredictor.get_emissions_rate(year, month, day, hour, minute)
            carbonTrend = self.carbonPredictor.get_emissions_trend(year, month, day, hour, minute)
            comfortMetric = calcComfortMetric(temperature=self.sensorValues[0], month=month, day=day, hour=hour)

            observation = ControlPanel.getObservation(zoneMeanAirTemp=self.sensorValues[0], 
                                                      siteDrybulbTemp=self.sensorValues[1], 
                                                      carbonTrend=carbonTrend,
                                                      boilerElecMeter=self.sensorValues[2], 
                                                      hour=hour)
            # if the previous observation is taken we want to overwrite the value so the agent always gets the latest info
            self.observationQueue.put_overwrite(observation)

            rewardData = ControlPanel.getDataForReward(zoneMeanAirTemp=self.sensorValues[0], 
                                                       boilerElecMeter=self.sensorValues[2], 
                                                       pumpElecMeter=self.sensorValues[3],
                                                       carbonRate=carbonRate, 
                                                       comfortMetric=comfortMetric, 
                                                       heatingEnergy=self.sensorValues[4])
            self.rewardDataQueue.put_overwrite(rewardData)

            self.observationNumber += 1 # a new observation is already available! Wait for the new action the agent will soon issue
        return

    def set_actuators(self, action, state): 
        self.dataExchange.set_actuator_value(state, self.actuatorHandles[0], ControlPanel.boilerOnOrOff(action))
        self.dataExchange.set_actuator_value(state, self.actuatorHandles[1], ControlPanel.heatSetPoint(action))

        self.actuatorValues[0] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[0])
        print(self.actuatorValues[0])
        self.actuatorValues[1] = self.dataExchange.get_actuator_value(state, self.actuatorHandles[1])
        print("____" + str(self.actuatorValues[1]))
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
                                                                            "Schedule:Compact", 
                                                                            "Schedule Value", 
                                                                            "HEATING SET POINT SCHEDULE")

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

