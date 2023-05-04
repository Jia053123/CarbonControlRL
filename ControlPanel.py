import numpy as np
from gymnasium.spaces.box import Box
from gymnasium.spaces.discrete import Discrete
from gymnasium.spaces.multi_discrete import MultiDiscrete
from info_for_agent import CarbonPredictor

##############################################################
def getObservationSpace():
    # observation space (upper bound not included!!): 
    #  Indoor Temp Celsius
    #  Outdoor Air Temp Celsius
    #  Carbon Trend: difference from the current rate
    obs_sp = Box(low=np.array([-0.5, -0.5, -0.5]), high=np.array([0.5, 0.5, 0.5]), dtype=np.float32)
    return obs_sp

def getObservation(zoneMeanAirTemp, siteDrybulbTemp, carbonTrend, boilerElecMeter, hour, zoneMeanRadientTemp):
    ZMRT_MEAN = 24.11623491
    ZMRT_MAX = 37.28791303
    ZMRT_MIN = 14.53138072

    SDBT_MEAN = 11.1931376
    SDBT_MAX = 31.462
    SDBT_MIN = -1.7

    CT_MEAN = 0.039630055
    CT_MAX = 75.15164845
    CT_MIN = -80.9608567

    obs = [zoneMeanRadientTemp / (ZMRT_MAX - ZMRT_MIN) - ZMRT_MEAN, 
           siteDrybulbTemp / (SDBT_MAX - SDBT_MIN) - SDBT_MEAN, 
           carbonTrend /(CT_MAX - CT_MIN) - CT_MEAN]
    return obs


##############################################################
def getActionSpace(): 
    # action space: Boiler on/off 
    # Zone heating setpoint high/low
    act_sp = MultiDiscrete(np.array([2])) #[{0, 1}]
    return act_sp

def heatSetPoint(agentAction:np.ndarray): 
    v = float('nan')
    match int(agentAction.item(0)): 
        case 0: 
            v = 15.0
        case 1:
            v = 25.0
        case _:
            raise ValueError("heatSetPoint: invalid action")
    return v


##############################################################
def getDataForReward(zoneMeanAirTemp, boilerElecMeter, pumpElecMeter, carbonRate, comfortMetric, heatingEnergy, boilerInletTemp, boilerOutletTemp, boilerInletFlow, boilerOutletFlow, heatingElec, outdoorDryBulb, zoneMeanRadientTemp, carbonTrend):
    return [zoneMeanAirTemp, boilerElecMeter, pumpElecMeter, carbonRate, comfortMetric, heatingEnergy, boilerInletTemp, boilerOutletTemp, boilerInletFlow, boilerOutletFlow, heatingElec, outdoorDryBulb, zoneMeanRadientTemp, carbonTrend]

def calculateReward(year, month, day, hour, minute, dataForReward):
    heatElec = dataForReward[1]
    carbonRate = dataForReward[2]
    comfort = dataForReward[3]
    rawReward = -1 * heatElec * carbonRate / 1000000 + comfort * 1
    reward = 0
    if rawReward < -100:
        reward = 0
    else:
        reward = 1
    return reward

def getNewAnalysis(year, month, day, hour, minute, dataForReward, action):
    reward = calculateReward(year, month, day, hour, minute, dataForReward)
    return [year, month, day, hour, minute, dataForReward[0], dataForReward[1], dataForReward[2], dataForReward[5], dataForReward[3], dataForReward[4], heatSetPoint(action), 
            dataForReward[6], dataForReward[7], dataForReward[8], dataForReward[9], dataForReward[10], dataForReward[11], dataForReward[12], reward, dataForReward[13]]

def getAnalysisColumns():
    return ['year', 'month', 'day', 'hour', 'minute', 'zone mean air temp', 'heating electricity', 'pump electricity', 'heating Energy', 'carbon rate', 'comfort metric', 'heating setpoint', 
            'boiler inlet temp', 'boiler outlet temp', 'boiler inlet flow', 'boiler outlet flow', 'heating electricity', 'outdoor drybulb', 'zone mean radient temp', 'reward', 'carbon trend']
