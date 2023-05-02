import os
import numpy as np
import gymnasium as gym
from GymEnvironment import Environment

from stable_baselines3 import DQN
from stable_baselines3 import PPO
from stable_baselines3 import A2C
from stable_baselines3 import SAC

from stable_baselines3.common.evaluation import evaluate_policy

import pandas as pd  
import ControlPanel

PATH_MODEL = "C:/Users/Eppy/Documents/CarbonControlRL/Models/TrainedModel"
EPW_PATH_Eval = "C:/Users/Eppy/Documents/WeatherFiles/KACV-Eureka-2020.epw"
SAVE_PATH_CSV = "C:/Users/Eppy/Documents/CarbonControlRL/Analysis/AnalysisData_agent.csv"

modelToEval = PPO.load(PATH_MODEL)

analysisData = []
evalEnvironment = Environment(analysisDataList=analysisData, epwPath=EPW_PATH_Eval)
mean_reward, std_reward = evaluate_policy(modelToEval, evalEnvironment, n_eval_episodes=1)
print("evaluation complete ****************************************")
print(f"mean_reward:{mean_reward:.2f} +/- {std_reward:.2f}")

print("reward count: " + str(evalEnvironment.rewardCount))
print("accumulated reward: " + str(evalEnvironment.accumulatedReward))

df = pd.DataFrame(analysisData, columns=ControlPanel.getAnalysisColumns()) 
df.to_csv(SAVE_PATH_CSV, index=False)
print("analysis data saved ****************************************") 