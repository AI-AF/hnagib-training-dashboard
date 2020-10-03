import fitparse
import pandas as pd
import os

class WahooTickrX:

    def __init__(self, filepath):
        """
        :param filepath: path to fit file directory
        :param fitfile: fit file parser object
        :param heartrate: pandas dataframe with heart rate data
        """
        self.filepath = filepath
        self.fitfile = fitparse.FitFile(filepath)
        self.datets = pd.to_datetime(os.path.basename(filepath)[:17])
        self.heartrate = self._get_heartrate_data()
        self.add_heartrate_detla()
        
        
    def _get_heartrate_data(self):
        data = []
        for record in self.fitfile.get_messages('record'):
            records = {}
            for record_data in record: 
                if record_data.name in ['heart_rate', 'timestamp']:
                    records[record_data.name] = record_data.value
            data.append(records)
        return pd.DataFrame(data).set_index('timestamp').iloc[:-20] #.tz_localize('GMT').tz_convert('EST')
    
    
    def add_heartrate_detla(self, lags=[60,120,180]):
        """
        Create a lagged column for each of the specified heart rate recovery period in seconds
        :param lags: heart recovery periods in seconds.
        """
        df = self.heartrate
        for lag in lags:
            df[f'{lag}_sec_rec'] = df['heart_rate'] - df['heart_rate'].shift(-lag)
            
    def get_heartrate_zones(self):
        zones ={
            '174_': (self.heartrate.query('heart_rate >= 174')).shape[0],
            '152_173': (self.heartrate.query('(heart_rate >= 152) & (heart_rate <= 173)')).shape[0],
            '138_151': (self.heartrate.query('(heart_rate >= 138) & (heart_rate <= 151)')).shape[0],
            '119_137': (self.heartrate.query('(heart_rate >= 119) & (heart_rate <= 137)')).shape[0],
            '_118': (self.heartrate.query('heart_rate <= 118')).shape[0]
        }
        return zones
        
