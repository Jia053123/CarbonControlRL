import os
import numpy as np
import gymnasium as gym
from GymEnvironment import Environment

from stable_baselines3 import DQN # unstable
from stable_baselines3 import PPO
from stable_baselines3 import A2C # chose the higher setpoint in test
from stable_baselines3 import SAC # much, much slower then PPO (multiple actors); did not produce optimal policy

SAVE_PATH = "C:/Users/Eppy/Documents/CarbonControlRL/Models/TrainedModel"

environment = Environment()
model = PPO("MlpPolicy", environment, verbose=2, gamma=1.0) # gamma: discount factor
model.learn(total_timesteps=16384) 

print("done learning ***************************************")
model.save(SAVE_PATH)
print("model saved *****************************************")
