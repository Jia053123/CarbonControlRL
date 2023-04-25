import os
from pyenergyplus.api import EnergyPlusAPI
import numpy as np
from EnergyPlusController import EnergyPlusRuntimeController
from GymEnvironment import Environment


environment = Environment()
environment.reset()