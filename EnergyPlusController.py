import sys
import os
from pyenergyplus.api import EnergyPlusAPI
import gymnasium as gym
from gymnasium.spaces import Box
import numpy as np
from queue import Queue, Empty, Full
import threading

IDF_PATH = "C:/Users/Eppy/Documents/IDFs/UnderFloorHeatingPresetCA_Electric.idf"
EPW_PATH = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"
OUTPUT_DIR = os.path.dirname(IDF_PATH)  + '/output'

class EnergyPlusRuntimeController:
    def __init__(self, observation_queue: Queue, action_queue: Queue):
        self.energyplus_api = EnergyPlusAPI()
        self.dataExchange = self.energyplus_api.exchange

        self.observation_queue = observation_queue
        self.action_queue = action_queue

        self.energyplus_exec_thread: threading.Thread = None
        self.energyplus_state = None
        self.runtime = None
        self.exitCode = None
        # self.progress_value: int = 0
        return

    def start(self):
        self.energyplus_state = self.energyplus_api.state_manager.new_state()
        self.runtime = self.energyplus_api.runtime

        def _run_energyplus(runtime, state, exitCode):
            print("starting up EnergyPlus simulaiton")
            exitCode = runtime.run_energyplus(state, ['-d', OUTPUT_DIR, '-w', EPW_PATH, IDF_PATH])
        
        self.energyplus_exec_thread = threading.Thread(
            target=_run_energyplus,
            args=(
                self.runtime,
                self.energyplus_state,
                self.exitCode
            )
        )
        self.energyplus_exec_thread.start()
        return

    def stop(self): 
        if self.energyplus_exec_thread is not None:
            self.energyplus_exec_thread.join()
            self.energyplus_exec_thread = None
        self.energyplus_api.runtime.clear_callbacks()
        self.energyplus_api.state_manager.delete_state(self.energyplus_state)