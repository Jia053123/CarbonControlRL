import os
import numpy as np
import gymnasium as gym
from GymEnvironment import Environment

from stable_baselines3 import PPO
from stable_baselines3 import DQN
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.evaluation import evaluate_policy

SAVE_PATH = "C:/Users/Eppy/Documents/CarbonControlRL/Models/TrainedModel"
model = PPO.load(SAVE_PATH)

evalEnvironment = Environment()
mean_reward, std_reward = evaluate_policy(model, evalEnvironment, n_eval_episodes=1)
print("finish evaluation ****************************************")
print(f"mean_reward:{mean_reward:.2f} +/- {std_reward:.2f}")