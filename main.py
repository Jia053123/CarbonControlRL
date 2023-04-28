import os
import numpy as np
import gymnasium as gym
from GymEnvironment import Environment

from stable_baselines3 import PPO
from stable_baselines3 import DQN
# from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.evaluation import evaluate_policy
# from stable_baselines3.common.env_checker import check_env

SAVE_PATH = "C:/Users/Eppy/Documents/CarbonControlRL/Models/TrainedModel"


environment = Environment()
model = DQN("MlpPolicy", environment, verbose=2)
model.learn(total_timesteps=16384) #100000)

print("done learning **********************************************")
model.save(SAVE_PATH)
print("model saved *****************************************")

# environment.close()
# print("testing model ************************************************")

# evalEnvironment = Environment()
# mean_reward, std_reward = evaluate_policy(model, evalEnvironment, n_eval_episodes=100)
# print(f"mean_reward:{mean_reward:.2f} +/- {std_reward:.2f}")