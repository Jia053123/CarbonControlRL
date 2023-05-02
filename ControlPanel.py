import numpy as np
from gymnasium.spaces.box import Box
from gymnasium.spaces.discrete import Discrete
from gymnasium.spaces.multi_discrete import MultiDiscrete
from info_for_agent import CarbonPredictor

##############################################################
def getObservationSpace():
    # observation space (upper bound not included!!): 
    #  Outdoor Air Temp Celsius: [-40, 60) -> normalize by dividing by 20
    obs_sp = Box(low=np.array([-2]), high=np.array([3]), dtype=np.float32)
    return obs_sp

def getObservation(zoneMeanAirTemp, siteDrybulbTemp, boilerElecMeter, hour):
    # obs = [ZoneMeanAirTemp, SiteDrybulbTemp, hour]
    obs = [siteDrybulbTemp/20]
    return obs


##############################################################
def getActionSpace(): 
    # action space: Boiler on/off 
    # Zone heating setpoint high/low
    act_sp = MultiDiscrete(np.array([2, 2])) #[{0, 1}, {0, 1}]
    return act_sp

def boilerOnOrOff(agentAction:np.ndarray):
    v = float('nan')
    match int(agentAction.item(0)): 
        case 0: 
            v = 0.0
        case 1:
            v = 1.0
        case _:
            raise ValueError("boilerOnOrOff: invalid action")
    return v

def heatSetPoint(agentAction:np.ndarray): 
    v = float('nan')
    match int(agentAction.item(1)): 
        case 0: 
            v = 15.0
        case 1:
            v = 25.0
        case _:
            raise ValueError("heatSetPoint: invalid action")
    return v


##############################################################
def getDataForReward(zoneMeanAirTemp, boilerElecMeter, carbonRate, comfortMetric):
    return [zoneMeanAirTemp, boilerElecMeter, carbonRate, comfortMetric]

def calculateReward(year, month, day, hour, minute, dataForReward):
    heatElec = dataForReward[1]
    carbonRate = dataForReward[2]
    comfort = dataForReward[3]
    reward = -1 * heatElec * carbonRate / 1000000 + comfort * 3
    return reward

def getNewAnalysis(year, month, day, hour, minute, dataForReward):
    return [year, month, day, hour, minute, dataForReward[0], dataForReward[1], dataForReward[2], dataForReward[3]]

def getAnalysisColumns():
    return ['year', 'month', 'day', 'hour', 'minute', 'zone mean air temp', 'heating electricity', 'carbon rate', 'comfort metric']
