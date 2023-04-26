 To run unit tests: 

 ```shell
 python UnitTests.py
 ```

==============================================

Make sure energyplus 9.4 is installed on computer (download from official site) 
Make sure environmental variable PYTHONPATH has value C:\EnergyPlusV9-4-0

To test the energyplus api is accessalbe: 

```shell
python -c 'from pyenergyplus.api import EnergyPlusAPI; print(EnergyPlusAPI.api_version())'
``` 
should output 0.2

Install Stable Baselines 3:
https://stable-baselines3.readthedocs.io/en/master/guide/install.html

============================================

Use the DesignBuilder's example file: under floor heating example

Make sure energy plus 9.4 is selected in tools -> program options

Modify the design builder file as needed

File -> export -> energy plus -> simulation

In export options: 
	A lot of options to choose from! 
	In Output tab, Miscellaneous, check EDD/RDD file if needed (slightly slows down the simulation) 

==========================================

Make sure ! Schedule: On 24/7 is set to 1 (active) with a high Cooling setpoint if using the schedule as actuator! 
