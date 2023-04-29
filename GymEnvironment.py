import os
import gymnasium as gym
# from gymnasium import spaces
from gymnasium.spaces.box import Box
from gymnasium.spaces.discrete import Discrete
import numpy as np
from QueueOfOne import QueueOfOne
from EnergyPlusController import EnergyPlusRuntimeController
from ActionObservationManager import ActionObservationManager
from queue import Empty, Full

IDF_PATH = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPresetCA_Electric.idf"
EPW_PATH = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"
OUTPUT_DIR = os.path.dirname(IDF_PATH)  + '/output'

class Environment(gym.Env):
    def __init__(self):
        print("init+++++++++++++++++++++++++++++++++++++")
        self.energyPlusController: EnergyPlusRuntimeController = None
        self.actionObserverManager: ActionObservationManager = None
        self.observation_queue: QueueOfOne = None
        self.action_queue: QueueOfOne = None

        self.observation = None
        self.terminated = False

        self.episode = -1
        self.timestep = 0

        # observation space (upper bound not included!!): Zone Mean Air Temp: 0-50C; hour of the day; Electricity for heating: 0-100 * 10000000
        self.observation_space = Box(low=np.array([0, 0]), high=np.array([50, 24]), dtype=np.float32)
        # action space: Heating Setpoint: choosing between two options
        self.action_space = Discrete(2) #{0, 1} 

        super().__init__()
        return
    
    def reset(self):
        '''
        The reset method will be called to initiate a new episode. 
        You may assume that the step method will not be called before reset has been called. 
        Moreover, reset should be called whenever a done signal has been issued.
        '''
        print("resetting===================================================")

        self.episode += 1
        print("episode: " + str(self.episode))

        if self.energyPlusController is not None:
            self.energyPlusController.stop()

        if not self.terminated: 
            self.observation_queue = QueueOfOne(timeout=5)
            self.action_queue = QueueOfOne(timeout=5)

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

            print("waiting for observation")
            while self.actionObserverManager.warmUpFlag:
                pass
            self.observation = self.observation_queue.get_wait()
            
        print("finish reset========================================================")
        print(self.observation)
        info = {}
        return self.observation, info
    
    def step(self, action):
        '''
        Compute the state of the environment after applying the action
        '''
        self.timestep += 1

        try:
            # if the last action has not been taken, make sure that is taken first
            self.action_queue.put_wait(action)
            self.observation = self.observation_queue.get_wait()
        except (Full, Empty):
            self.terminated = True
            print("Terminated !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


        reward = -1 * self.observation[0]

        info = {}
        return self.observation, reward, self.terminated, False, info
    
    def render(self):
        '''
        Render the graphs
        '''
        return
    
    def close(self):
        '''
        Close any open resources that were used by the environment
        '''
        print("closing environment +++++++++++++++++++++++++++++++++")
        self.energyPlusController.stop()
        return

    