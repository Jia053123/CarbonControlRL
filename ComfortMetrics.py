import math

COMFORT_RANGE_LOW = 22
EXP_FACTOR = 3

def calcComfortMetric(temperature, month, day, hour):
    if temperature < COMFORT_RANGE_LOW:
        return -1 * math.pow((COMFORT_RANGE_LOW - temperature), EXP_FACTOR)
    else:
        return 0.001 # always give a small positive reward?
    
