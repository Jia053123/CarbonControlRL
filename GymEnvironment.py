import os
import gymnasium as gym
from gymnasium.spaces import Box
import numpy as np
from queue import Queue, Empty, Full
from EnergyPlusController import EnergyPlusRuntimeController
from ActionObservationManager import ActionObservationManager

IDF_PATH = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPresetCA_Electric.idf"
EPW_PATH = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"
OUTPUT_DIR = os.path.dirname(IDF_PATH)  + '/output'

class Environment(gym.Env):
    def __init__(self):
        self.energyPlusController: EnergyPlusRuntimeController = None
        self.actionObserverManager: ActionObservationManager = None
        self.observation_queue: Queue = None
        self.action_queue: Queue = None

        self.episode = -1
        self.timestep = 0

        # observation space: Zone Mean Air Temp: 0-50C; Electricity for heating: 0-100 * 10000000
        self.observation_space = Box(low=np.array([0, 0], high=np.array([50, 100]), dtype=np.float32))
        # action space: Heating Setpoint: 15-30C
        self.action_space = Box(low=np.array([15], high=np.array([30]), dtype=np.float32))
        return
    
    def reset(self):
        '''
        The reset method will be called to initiate a new episode. 
        You may assume that the step method will not be called before reset has been called. 
        Moreover, reset should be called whenever a done signal has been issued.
        '''
        self.episode += 1

        # if the two threads coorporate correctly only a single entry is needed
        self.observation_queue = Queue(maxsize=1)
        self.action_queue = Queue(maxsize=1)

        if self.energyPlusController is not None:
            self.energyPlusController.stop()
        self.energyPlusController = EnergyPlusRuntimeController(self.observation_queue, self.action_queue)
        self.actionObserverManager = ActionObservationManager(self.energyPlusController.dataExchange, 
                                                              self.action_queue, 
                                                              self.observation_queue, 
                                                              OUTPUT_DIR)
        
        runtime = self.energyPlusController.createRuntime()
        runtime.callback_begin_system_timestep_before_predictor(self.energyPlusController.energyplus_state, 
                                                                self.actionObserverManager.send_actions)
        runtime.callback_end_zone_timestep_after_zone_reporting(self.energyPlusController.energyplus_state, 
                                                                self.actionObserverManager.collect_observations)

        self.energyPlusController.start(runtime, IDF_PATH, EPW_PATH, OUTPUT_DIR)



        # # randomly generate the first past observation
        # self.last_observation = self.observation_space.sample()



        # try:
        #     observation = self.obs_queue.get()
        # except Empty:
        #     observation = self.last_obs

        # observationList = np.array(list(observation.values()))
        observationList = {}
        info = {}
        return observationList, info
    
    def step(self, action):
        '''
        Compute the state of the environment after applying the action
        '''
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
        '''
        Render the graphs
        '''
        return
    
    def close(self):
        '''
        Close any open resources that were used by the environment
        '''
        return
    