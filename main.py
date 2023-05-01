import os
import numpy as np
import gymnasium as gym
from GymEnvironment import Environment

from stable_baselines3 import DQN # unstable
from stable_baselines3 import PPO
from stable_baselines3 import A2C # chose the higher setpoint in test
from stable_baselines3 import SAC # much, much slower then PPO (multiple actors); did not produce optimal policy


SAVE_PATH_MODEL = "C:/Users/Eppy/Documents/CarbonControlRL/Models/TrainedModel"
IDF_TIMESTEP = 6 # Timesteps/hour (must match with setting within idf file) 

environment = Environment()
model = PPO("MlpPolicy", environment, verbose=2, gamma=0.99) # gamma: discount factor
model.learn(total_timesteps = 8192 * IDF_TIMESTEP) # 16384 when Timestep=2
print("done learning ***************************************")

model.save(SAVE_PATH_MODEL)
print("model saved *****************************************")

