import datetime
import pandas as pd

class CarbonPredictor():
    def __init__(self):
        self.dataframe = pd.read_csv('table_for_agent_info_function.csv', index_col=0, parse_dates=True)
        self.dataframe.index = pd.to_datetime(self.dataframe.index)

    def get_emissions_rate(self, year, month, day, hour, minute):
        
        if hour >= 24:
            hour = 23
            minute = 59
        
        if minute >= 60 and minute < 100:
            minute = 59
        elif minute >= 100:
            minute = 10
            
        # convert the date and time to a datetime object
        date_time = datetime.datetime(round(year), round(month), round(day), round(hour), (int((round(minute)/10)))*10) # round the minute down to the nearest 10 minutes
        # use the date_time to get the predicted emissions
        predicted_emissions_rate = self.dataframe.loc[date_time]['predicted_emissions']
        return predicted_emissions_rate