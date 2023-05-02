COMFORT_RANGE_HIGH = 30
COMFORT_RANGE_LOW = 20
EXP_FACTOR = 1.0

def calcComfortReward(temperature, weight):
    if temperature < COMFORT_RANGE_LOW:
        return pow((temperature - COMFORT_RANGE_LOW), EXP_FACTOR) * weight
    elif temperature > COMFORT_RANGE_HIGH:
        return pow((COMFORT_RANGE_HIGH - temperature), EXP_FACTOR) * weight
    else:
        return 0.0 # TODO: always give a small positive reward?
    
