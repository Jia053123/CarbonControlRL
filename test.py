import sys
import os
from pyenergyplus.api import EnergyPlusAPI
import gymnasium as gym
from gymnasium.spaces import Box
import numpy as np
from queue import Queue, Empty, Full

iddPath = "C:/EnergyPlusV9-4-0/Energy+.idd" 
# iddPath = "C:/EnergyPlusV9-5-0/Energy+.idd" 

idfPath = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPresetCA_Electric.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/TT_03-26_Test.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPresetMA.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/IECC_OfficeSmall_STD2018_SanDiego.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/ASHRAE901_OfficeSmall_STD2019_SanDiego.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/ASHRAE901_OfficeSmall_STD2019_NewYork.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/US+MF+CZ3C+elecres+heatedbsmt+IECC_2021.idf"
# idfPath = "C:/Users/Eppy/Documents/IDFs/US+MF+CZ4A+elecres+unheatedbsmt+IECC_2021.idf"

# epwPath = "C:/Users/Eppy/Documents/WeatherFiles/USA_CA_San.Diego-Lindbergh.Field.722900_TMY3.epw"
epwPath = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"

outputDir = os.path.dirname(idfPath)  + '/output'

energyplus_api = EnergyPlusAPI()
dataExchange = energyplus_api.exchange

energyplus_state = energyplus_api.state_manager.new_state()
runtime = energyplus_api.runtime


class EnergyPlusEnv(gym.Env):
    def __init__(self):
        self.episode = -1
        self.timestep = 0

        # observation space: Zone Mean Air Temp: 0-50C; Natural Gas for heating: 0-100 * 1000000
        self.observation_space = Box(low=np.array([0, 0], high=np.array([50, 100]), dtype=np.float32))

        # action space: Boiler Temperature: 20-90C; Heating Setpoint: 15-30C
        self.action_space = Box(low=np.array([20, 15], high=np.array([90, 30]), dtype=np.float32))

        # self.energyplus_runner: Optional[EnergyPlusRunner] = None
        self.observation_queue: Queue = None
        self.action_queue: Queue = None

        return
    
    def reset(self):
        # initiate a new episode
        self.episode += 1

        # if the two threads coorporate correctly only a single entry is needed
        self.observation_queue = Queue(maxsize=1)
        self.action_queue = Queue(maxsize=1)

        # randomly generate the first past observation
        self.last_observation = self.observation_space.sample()

        try:
            observation = self.obs_queue.get()
        except Empty:
            observation = self.last_obs

        observationList = np.array(list(observation.values()))
        info = {}
        return observationList, info
    
    def step(self, action):
        # compute the state of the environment after applying the action
        self.timestep += 1

        timeout = 2
        try:
            self.action_queue.put(action, timeout=timeout)
            self.last_observation = observation = self.observation_queue.get(timeout=timeout)
        except (Full, Empty):
            terminated = True
            observation = self.last_observation

        observationList = np.array(list(observation.values()))

        reward = -1 * observationList[1]
        if observationList[0] < 20:
            reward -= 1000

        done = False
        info = {}
        return observationList, reward, terminated, done, info
    
    def render(self):
        # render the graphs
        return
    
    def close(self):
        # close any open resources that were used by the environment
        return
    




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
meterHandle2 = -1
meterHandle3 = -1
variableHandle4 = -1
def collect_observations(state):
    global variableHandle1
    global meterHandle2
    global meterHandle3
    global variableHandle4
    if not dataExchange.api_data_fully_ready(state):
        return
    writeAvailableApiDataFile(False) # Change to True to write the file in output folder
    
    warmUpFlag = dataExchange.warmup_flag(state)

    if variableHandle1 < 0 or meterHandle2 < 0 or meterHandle3 < 0 or variableHandle4 < 0: 
        variableHandle1 = dataExchange.get_variable_handle(state, 
                                                           "Zone Mean Air Temperature", 
                                                           "BLOCK1:ZONE1")
        meterHandle2 = dataExchange.get_meter_handle(state, 
                                                     "Boiler:Heating:Electricity")
        meterHandle3 = dataExchange.get_meter_handle(state, 
                                                     "Pumps:Electricity")
        variableHandle4 = dataExchange.get_variable_handle(state, 
                                                           "System Node Temperature", 
                                                           "BOILER WATER OUTLET NODE")
    else: 
        hour = dataExchange.hour(state)
        minute = dataExchange.minutes(state)

        variableValue1 = dataExchange.get_variable_value(state, variableHandle1) 
        meterValue2 = dataExchange.get_meter_value(state, meterHandle2) 
        meterValue3 = dataExchange.get_meter_value(state, meterHandle3) 
        variableValue4 = dataExchange.get_variable_value(state, variableHandle4) 

        print(str(hour) + 
              ":" + str(minute) + 
              "__" + str(variableValue1) + 
              "__" + str(meterValue2) + 
              "__" + str(meterValue3) + 
              "__" + str(variableValue4))
        
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
                                                           "Schedule:Compact", 
                                                           "Schedule Value", 
                                                           "HOT WATER FLOW SET POINT TEMPERATURE: ALWAYS 80.0 C")
        actuatorHandle2 = dataExchange.get_actuator_handle(state, 
                                                           "Schedule:Compact", 
                                                           "Schedule Value", 
                                                           "BLOCK1:ZONE1 HEATING SETPOINT SCHEDULE")
        actuatorHandle3 = dataExchange.get_actuator_handle(state, 
                                                           "Schedule:Compact", 
                                                           "Schedule Value", 
                                                           "BLOCK1:ZONE1 COOLING SETPOINT SCHEDULE")
    else:
        printApiFlagIfRaised(state)
        
        # actuatorValue1 = dataExchange.get_actuator_value(state, actuatorHandle1)
        # actuatorValue2 = dataExchange.get_actuator_value(state, actuatorHandle2)
        # actuatorValue3 = dataExchange.get_actuator_value(state, actuatorHandle3)
        # print("Set Point: " + str(actuatorValue1))
        # print("Set Point: " + str(actuatorValue2))
        # print("Set Point: " + str(actuatorValue3))

        dataExchange.set_actuator_value(state, actuatorHandle1, 60.0)
        dataExchange.set_actuator_value(state, actuatorHandle2, 25.0)
        dataExchange.set_actuator_value(state, actuatorHandle3, 30.0)
    return

runtime.callback_begin_system_timestep_before_predictor(energyplus_state, send_actions)
runtime.callback_after_predictor_after_hvac_managers(energyplus_state, send_actions)
runtime.callback_end_zone_timestep_after_zone_reporting(energyplus_state, collect_observations)

exitCode = runtime.run_energyplus(energyplus_state, ['-d', outputDir, '-w', epwPath, idfPath])
print("exit code (zero is success): " + str(exitCode))



