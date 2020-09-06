import fitparse
import pandas as pd

class WahooTickrX:

    def __init__(self, filepath):
        """
        :param filepath: path to fit file directory
        :param fitfile: fit file parser object
        :param heartrate: pandas dataframe with heart rate data
        """
        self.filepath = filepath
        self.fitfile = fitparse.FitFile(filepath)
        self.heartrate = self._get_heartrate_data()
        self.gen_heartrate_detla()
        
        
    def _get_heartrate_data(self):
        data = []
        for record in self.fitfile.get_messages('record'):
            records = {}
            for record_data in record: 
                if record_data.name in ['heart_rate', 'timestamp']:
                    records[record_data.name] = record_data.value
            data.append(records)
        return pd.DataFrame(data).set_index('timestamp').tz_localize('GMT').tz_convert('EST')
    
    
    def gen_heartrate_detla(self, lags=[60,120,180]):
        """
        Create a lagged column for each of the specified heart rate recovery period in seconds
        :param lags: heart recovery periods in seconds.
        """
        df = self.heartrate
        for lag in lags:
            df[f'{lag}_sec_rec'] = df['heart_rate'] - df['heart_rate'].shift(-lag)
            
