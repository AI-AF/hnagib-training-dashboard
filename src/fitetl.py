from wahooreader import WahooTickrX
import os
from pathlib import Path
import pandas as pd
import dask
import glob
from dask.diagnostics import ProgressBar
import dask.dataframe as dd
import time

datadir_fit = '/Users/hasannagib/Dropbox/Apps/WahooFitness/'
datadir_hrsum = '/Users/hasannagib/Documents/s3stage/wahoo/heartrate_sumstat/'
datadir_hrts = '/Users/hasannagib/Documents/s3stage/wahoo/heartrate_ts/'

@dask.delayed
def export_hr_sumstat(fit, datadir):
    wtx = WahooTickrX(fit)
    ts = wtx.datets.strftime('%Y-%m-%d-%H%M%S')
    output_file = Path(f'{datadir}{ts}.csv')

    dt = {'timestamp': wtx.datets}
    rec = dict(wtx.heartrate.max()[['60_sec_rec', '120_sec_rec', '180_sec_rec']])
    zone = wtx.get_heartrate_zones()

    df = pd.DataFrame({**rec, **zone}, index=[dt['timestamp']])
    df.to_csv(output_file)


@dask.delayed
def export_hr_ts(fit, datadir):
    wtx = WahooTickrX(fit)
    ts = wtx.datets.strftime('%Y-%m-%d-%H%M%S')
    output_file = Path(f'{datadir}{ts}.csv')
    wtx.heartrate.to_csv(output_file)


def proc_fit(fit_files, func, datadir):
    """
    Given fitfiles, process them if the processed files don't exist.

    :param func: fit file processing function that exports csvs
    :param datadir: directory where csv-s are exported
    :return: None
    """
    out = []
    for fit in fit_files:
        ts = os.path.basename(fit)[:17]
        output_file = Path(f'{datadir}{ts}.csv')

        if not output_file.exists():
            out.append(func(fit, datadir))

    with ProgressBar():
        dask.compute(*out)

def read_rcvry_csv(datadir):
    """
    Given directory of summary files, generate a summary df with
    HR recovery data

    :param datadir: directory where csv-s are exported
    :return: HR recovery df
    """
    df = dd.read_csv(Path(f'{datadir}*.csv')).compute()
    df = df.rename(columns={'Unnamed: 0': 'timestamp', '174_': '174_220'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')

    df = df.copy()
    df['L0'] = 22
    df['L1'] = 53
    df['L2'] = 59
    df['L3'] = 66

    df = df.reset_index()
    df['timestamp'] = pd.to_datetime(df['timestamp'].dt.strftime('%Y-%m-%d 07:00:00'))
    df = df.set_index('timestamp')
    return df

def read_hr_profile_csv(datadir):
    """
    Given directory of fit csv files, generate a df with
    column wise HR profile data for use in Bokeh dashboard

    :param datadir: directory where csv-s are exported
    :return: HR profile df for Bokeh
    """

    ts_files = sorted(glob.glob(f'{datadir}*.csv'))

    @dask.delayed
    def read_ts(file):
        df = pd.read_csv(file, parse_dates=['timestamp']
                         ).set_index('timestamp').sort_index().reset_index()[
            ['heart_rate']
        ].rename(columns={
            'heart_rate': pd.to_datetime(os.path.basename(file)[:-11]).strftime('%Y-%m-%d'),

        })
        return df


    dfs = [read_ts(file) for file in ts_files]

    with ProgressBar():
        dfs = dask.compute(dfs)[0]

    df_hr_profile = pd.concat(dfs, axis=1).reset_index().rename(columns={'index': 's'})
    df_hr_profile['Time'] = df_hr_profile['s'].apply(lambda x: time.strftime('%H:%M:%S', time.gmtime(x)))


    # Pick latest date for HR data
    df_hr_profile['BPM'] = df_hr_profile.iloc[:, -2]

    return df_hr_profile


def main():
    fit_files = glob.glob(f'{datadir_fit}*.fit')
    proc_fit(fit_files, export_hr_sumstat, datadir_hrsum)
    proc_fit(fit_files, export_hr_ts, datadir_hrts)


if __name__ == '__main__':
    main()




