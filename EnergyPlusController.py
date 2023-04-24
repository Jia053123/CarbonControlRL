import sys
import os
from pyenergyplus.api import EnergyPlusAPI
import gymnasium as gym
from gymnasium.spaces import Box
import numpy as np
from queue import Queue, Empty, Full
import threading


class EnergyPlusController:
    def __init__(self, observation_queue: Queue, action_queue: Queue):
        self.energyplus_api = EnergyPlusAPI()
        self.dataExchange = self.energyplus_api.exchange

        self.observation_queue = observation_queue
        self.action_queue = action_queue

        self.energyplus_exec_thread: threading.Thread = None
        self.energyplus_state = None
        self.progress_value: int = 0
        return

    def start(self):
        self.energyplus_state = self.energyplus_api.state_manager.new_state()
        runtime = self.energyplus_api.runtime