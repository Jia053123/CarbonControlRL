import numpy as np
from gymnasium.spaces.box import Box
from gymnasium.spaces.discrete import Discrete
from gymnasium.spaces.multi_discrete import MultiDiscrete
from info_for_agent import CarbonPredictor

def getIdfPath():
    p = "C:/Users/Eppy/Documents/IDFs/office111_allOff_fullyOccupied_1Y.idf"
    return p
def getEpwPath():
    # p = "C:/Users/Eppy/Documents/WeatherFiles/USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw"
    p = "C:/Users/Eppy/Documents/WeatherFiles/KACV-Eureka-2019.epw"
    return p

##############################################################
def getObservationSpace():
    # observation space (upper bound not included!!): 
    #  Zone Mean Air Temp Celsius: [0, 50)
    #  Outdoor Air Temp Celsius: [-40, 60)
    #  Hour of the day: [0, 24)
    obs_sp = Box(low=np.array([-40]), high=np.array([60]), dtype=np.float32)
    return obs_sp

def getObservation(zoneMeanAirTemp, siteDrybulbTemp, boilerElecMeter, hour):
    # obs = [ZoneMeanAirTemp, SiteDrybulbTemp, hour]
    obs = [siteDrybulbTemp]
    return obs


##############################################################
def getActionSpace(): 
    # action space: Boiler on/off and Zone heating setpoint; choosing between four options
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
def getDataForReward(zoneMeanAirTemp, boilerElecMeter):
    return [boilerElecMeter, zoneMeanAirTemp]

def calculateReward(carbonPredictor: CarbonPredictor, 
                    year, month, day, hour, minute, 
                    dataForReward):
    heatElec = dataForReward[0]
    carbonRate = carbonPredictor.get_emissions_rate(year, month, day, hour, minute)
    reward = -1 * heatElec #* carbonRate
    return reward

def getNewAnalysis(year, month, day, hour, minute, dataForReward):
    return [year, month, day, hour, minute, dataForReward[1], dataForReward[0]]

def getAnalysisColumns():
    return ['year', 'month', 'day', 'hour', 'minute', 'zone mean air temp', 'heating electricity']
