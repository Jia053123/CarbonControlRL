import os
import numpy as np
import gymnasium as gym
from GymEnvironment import Environment

from stable_baselines3 import PPO
from stable_baselines3 import DQN
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.evaluation import evaluate_policy

SAVE_PATH = "C:/Users/Eppy/Documents/CarbonControlRL/Models/TrainedModel"
modelToEval = DQN.load(SAVE_PATH)

evalEnvironment = Environment()
mean_reward, std_reward = evaluate_policy(modelToEval, evalEnvironment, n_eval_episodes=1)
print("evaluation complete ****************************************")
print(f"mean_reward:{mean_reward:.2f} +/- {std_reward:.2f}")