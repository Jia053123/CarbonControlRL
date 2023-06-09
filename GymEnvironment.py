import os
import gymnasium as gym
from gymnasium.spaces.box import Box
from gymnasium.spaces.discrete import Discrete
from gymnasium.spaces.multi_discrete import MultiDiscrete
import numpy as np
from QueueOfOne import QueueOfOne
from EnergyPlusController import EnergyPlusRuntimeController
from ActionObservationManager import ActionObservationManager
from queue import Empty, Full
import ControlPanel

IDF_PATH = "C:/Users/Eppy/Documents/IDFs/office111_allOff_fullyOccupied_1Y.idf"
OUTPUT_DIR = os.path.dirname(IDF_PATH)  + '/output'

class Environment(gym.Env):
    def __init__(self, epwPaths, analysisDataList:list = None):
        print("init+++++++++++++++++++++++++++++++++++++")
        self.epwPaths = epwPaths
        self.energyPlusController: EnergyPlusRuntimeController = None
        self.actionObserverManager: ActionObservationManager = None
        self.observation_queue: QueueOfOne = None
        self.action_queue: QueueOfOne = None
        self.dataForReward_queue: QueueOfOne = None

        self.stillSizingSystem = True
        self.observation = None
        self.dataForReward = None
        self.terminated = False

        self.analysisDataList = analysisDataList

        self.episode = -1
        self.timestep = 0

        self.observation_space = ControlPanel.getObservationSpace()
        self.action_space = ControlPanel.getActionSpace()

        self.accumulatedReward = 0
        self.rewardCount = 0

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

        self.terminated = False

        currentEpwPath = self.epwPaths[self.episode % len(self.epwPaths)]
        print(currentEpwPath)

        self.observation_queue = QueueOfOne(timeout=5)
        self.action_queue = QueueOfOne(timeout=5)
        self.dataForReward_queue = QueueOfOne(timeout=5)

        self.energyPlusController = EnergyPlusRuntimeController() 
        self.actionObserverManager = ActionObservationManager(self.energyPlusController.dataExchange, 
                                                            self.action_queue, 
                                                            self.observation_queue, 
                                                            self.dataForReward_queue,
                                                            OUTPUT_DIR)
        
        runtime = self.energyPlusController.createRuntime()
        runtime.callback_inside_system_iteration_loop(self.energyPlusController.energyplus_state, 
                                                        self.actionObserverManager.send_actions)
        runtime.callback_end_zone_timestep_after_zone_reporting(self.energyPlusController.energyplus_state, 
                                                                self.actionObserverManager.collect_observations)

        self.energyPlusController.start(runtime, IDF_PATH, currentEpwPath, OUTPUT_DIR)

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
            # energy plus runs here on its own thread
            self.observation = self.observation_queue.get_wait()
            self.dataForReward = self.dataForReward_queue.get_wait()
        except (Full, Empty):
            self.terminated = True
            print("Terminated !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        year = self.energyPlusController.dataExchange.year(self.energyPlusController.energyplus_state)
        month = self.energyPlusController.dataExchange.month(self.energyPlusController.energyplus_state)
        day = self.energyPlusController.dataExchange.day_of_month(self.energyPlusController.energyplus_state)
        hour = self.energyPlusController.dataExchange.hour(self.energyPlusController.energyplus_state)
        minute = self.energyPlusController.dataExchange.minutes(self.energyPlusController.energyplus_state)
        minute = minute - 1 # for the carbon script

        reward = ControlPanel.calculateReward(year, month, day, hour, minute, self.dataForReward)
        self.accumulatedReward += reward
        self.rewardCount += 1

        if self.analysisDataList is not None:
            newAnalysis = ControlPanel.getNewAnalysis(year=year, month=month, day=day, hour=hour, minute=minute, 
                                                      dataForReward=self.dataForReward,
                                                      action=action)
            self.analysisDataList.append(newAnalysis)

        info = {}
        # print(self.timestep)
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

    