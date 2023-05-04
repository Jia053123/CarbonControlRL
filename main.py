import os
import numpy as np
import gymnasium as gym
from GymEnvironment import Environment

from stable_baselines3 import DQN # unstable
from stable_baselines3 import PPO
from stable_baselines3 import A2C 
from stable_baselines3 import SAC # much, much slower then PPO (multiple actors)


SAVE_PATH_MODEL = "C:/Users/Eppy/Documents/CarbonControlRL/Models/TrainedModel"
EPW_PATHS_Train = ["C:/Users/Eppy/Documents/WeatherFiles/KACV-Eureka-2019.epw", 
                   "C:/Users/Eppy/Documents/WeatherFiles/KACV-Eureka-2019.epw"]

IDF_TIMESTEP = 10 # Timesteps/hour (must match with setting within idf file) 
NUM_OF_EPISODES = 100

environment = Environment(epwPaths=EPW_PATHS_Train)
# gamma: discount factor; gae_lambda: Factor for trade-off of bias vs variance
model = PPO("MlpPolicy", environment, verbose=2, n_steps=219, gamma=0.99, gae_lambda=0.95, tensorboard_log="./TensorBoardLog") 
model.learn(total_timesteps = 8760 * IDF_TIMESTEP * NUM_OF_EPISODES) 
print("done learning ***************************************")

model.save(SAVE_PATH_MODEL)
print("model saved *****************************************")

