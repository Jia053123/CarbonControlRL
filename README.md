 To run unit tests: 

 ```shell
 python UnitTests.py
 ```

==============================================
# Installation: 

Make sure energyplus 9.4 is installed on computer (download from official site) 
Make sure environmental variable PYTHONPATH has value C:\EnergyPlusV9-4-0

To test the energyplus api is accessalbe: 

```shell
python -c 'from pyenergyplus.api import EnergyPlusAPI; print(EnergyPlusAPI.api_version())'
``` 
should output 0.2

Install Stable Baselines 3, Bleeding Edge version:
 ```shell
pip install git+https://github.com/DLR-RM/stable-baselines3
```

Create IDF files and EPW files directories outside of the project folder, and modify the paths in testrun.py (used to run energyplus without agent, with hard-coded or no actuator settings), main.py (run the train the agent) and evaluate.py (run to load and test the agent)

First run the main.py to train the agent, then run evaluate.py to test it. 

To save the available sensors and actuators as csv, run testrun.py with line 64 set to True. Make sure to set it back to False afterwards. The csv file will be saved in the output folder within the IDF folder. 

The sensors history data are saved in Analysis folder (SAVE_PATH_CSV), and trained models in Models folder. 
============================================

Use the DesignBuilder's example file: under floor heating example

Make sure energy plus 9.4 is selected in tools -> program options

Modify the design builder file as needed

Places to insert custom schedule: 
	1. Building -> HVAC tab on top -> Heating -> Operation -> Schedule -> turn on for only weekdays
	2. HW Loop Setpoint Manager -> Edit Component on right panel -> Schedule -> Setpoint variable schedule

File -> export -> energy plus -> simulation

In export options: 
	A lot of options to choose from! 
	In Output tab, Miscellaneous, check EDD/RDD file if using EMS (slightly slows down the simulation) 

==========================================

Make sure ! Schedule: On 24/7 is set to 1 (active) with a high Cooling setpoint if using the schedule as actuator! 
