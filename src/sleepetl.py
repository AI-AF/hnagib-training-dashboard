import pandas as pd
from selenium import webdriver
from lxml import html
import time
import os
from datetime import datetime
from selenium.webdriver.chrome.options import Options


datadir = '/Users/hasannagib/Documents/s3stage/fitbit/sleep.csv'


class fitbit:

    def __init__(self, email, password, chrome_driver_path='../src/chromedriver'):
        """

        :param email: Email address login for WodUp
        :param password: WodUp login password
        :param url: url for profile/user to scrape
        :param chrome_driver_path: path to chromedriver executable
        """
        self.url = f'https://www.fitbit.com/sleep/'
        self.email = email
        self.password = password
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(chrome_driver_path, options=chrome_options)
        self.browser.get(self.url)
        self.login()

    def login(self):
        """
        Sign into WodUp using self.email and self.password
        """
        time.sleep(4)
        self.browser.find_element_by_xpath("//input[@type='email']").send_keys(self.email)
        self.browser.find_element_by_xpath("//input[@type='password']").send_keys(self.password)
        self.browser.find_element_by_xpath("//button[@id='ember702']").click()
        time.sleep(2)

    def get_sleep_data(self):
        """
        Get html tree for a given movement
        :param movement: movement to pull html for
        :param wait: wait to load page
        :return:
        """
        tree = html.fromstring(self.browser.page_source)
        
        sleep_logs = ['//'+tree.getroottree().getelementpath(xp) 
         for xp in tree.xpath('//span[@data-test-qa="item-date"]')
        ]

        start = []
        end = []
        date = []
        sleep_stages = []

        for log in sleep_logs[:30]:

            self.browser.find_element_by_xpath(log).click()
            time.sleep(4)

            tree = html.fromstring(self.browser.page_source)
            date.append(tree.xpath('//div[@class="sleep-log-edit ember-view"]/div/div/p/text()')[0])    
            print(f'Scraping sleep log for: {date[-1]}')

            start.append(self.browser.find_element_by_xpath('//input[@data-test-qa="start-time-input"]').get_attribute('value'))
            end.append(self.browser.find_element_by_xpath('//input[@data-test-qa="start-time-input"]/../../../following-sibling::div//input').get_attribute('value'))
            time.sleep(4)

            try:
                sleep_stages.append([float(tree.xpath(
                    f'//li[@class="column legend-item {stage}"]//span[@class="legend-label"]/text()'
                )[0].strip().split(' - ')[-1][:-1])/100
                    for stage in ['wake', 'rem', 'light', 'deep']
                ])

            except IndexError:
                sleep_stages.append([0.125, 0.20, 0.5, 0.175])

            self.browser.back()
            time.sleep(4)
        
        self.browser.close()
        
        df = pd.DataFrame({'date': date, 'start': start, 'end': end}).join(
            pd.DataFrame(sleep_stages, columns=['awake', 'rem', 'light', 'deep'])
        )

        df['start'] = pd.to_datetime(df['date'].astype(str)+" "+df['start']+ " PM") - pd.Timedelta('1 days')
        df['end'] = pd.to_datetime(df['date'].astype(str)+" "+df['end']+ " AM")
        df['duration'] = (df['end'] - df['start']).apply(lambda x: x.total_seconds())/60

        for stage in ['awake', 'rem', 'light', 'deep']:
            df[stage] = df[stage]*df['duration']

        df['time_asleep'] = df['rem'] + df['light'] + df['deep']
        df['start_hour'] = df['start'].dt.hour + (df['start'].dt.minute/60)
        df['end_hour'] = df['end'].dt.hour + (df['end'].dt.minute/60)
        
        return df


def read_sleep_plot_df(datadir=datadir):
    df_sleep = pd.read_csv(datadir, parse_dates=['start', 'end', 'date'])
    stages = ["deep", "rem", "light", "awake"]

    for s in stages:
        df_sleep[s] = df_sleep[s]/60

    sleep_thresholds = [-4,5,7,8,9,20]

    for t in sleep_thresholds:
        df_sleep[f'{t}hr'] = t

    df_sleep['time_asleep'] = df_sleep['deep'] + df_sleep['rem'] + df_sleep['light']
    df_sleep.loc[df_sleep['time_asleep'].isna(), "time_asleep"] = df_sleep.loc[df_sleep['time_asleep'].isna(), "duration"] * 0.75 / 60
    df_sleep.loc[df_sleep['time_asleep']==0, "time_asleep"] = df_sleep.loc[df_sleep['time_asleep']==0, "duration"] * 0.75 / 60

    for i in ['awake', 'rem', 'light', 'deep']:    
        df_sleep.loc[df_sleep[i].isna(), i] = df_sleep[i].mean()
        df_sleep.loc[df_sleep[i]==0, i] = df_sleep[i].mean()

    df_sleep['7day_avg'] = df_sleep.set_index('date')['time_asleep'].rolling('7d', closed='both').mean().reset_index()['time_asleep']
    df_sleep['start_last_7day_avg'] = df_sleep.set_index('date')['start_hour'].rolling('7d', closed='both', ).mean().reset_index()['start_hour'].shift(1)
    df_sleep['end_last_7day_avg'] = df_sleep.set_index('date')['end_hour'].rolling('7d', closed='both', ).mean().reset_index()['end_hour'].shift(1)
    df_sleep['start_last_7day_stdev'] = df_sleep.set_index('date')['start_hour'].rolling('7d', closed='both', ).std().reset_index()['start_hour'].shift(1)
    df_sleep['end_last_7day_stdev'] = df_sleep.set_index('date')['end_hour'].rolling('7d', closed='both', ).std().reset_index()['end_hour'].shift(1)

    df_sleep['start_last_3day_avg'] = df_sleep.set_index('date')['start_hour'].rolling('3d', closed='both', ).mean().reset_index()['start_hour'].shift(1)
    df_sleep['end_last_3day_avg'] = df_sleep.set_index('date')['end_hour'].rolling('3d', closed='both', ).mean().reset_index()['end_hour'].shift(1)
    df_sleep['start_last_3day_stdev'] = df_sleep.set_index('date')['start_hour'].rolling('3d', closed='both', ).std().reset_index()['start_hour'].shift(1)
    df_sleep['end_last_3day_stdev'] = df_sleep.set_index('date')['end_hour'].rolling('3d', closed='both', ).std().reset_index()['end_hour'].shift(1)

    df_sleep['start_hour_prev_day'] = df_sleep['start_hour'].shift(1) 
    df_sleep['end_hour_prev_day'] = df_sleep['end_hour'].shift(1)
    df_sleep['time_asleep_prev_day'] = df_sleep['time_asleep'].shift(1) 

    df_sleep['date_str'] = df_sleep['date'].dt.strftime('%a %b %d %Y')
    df_sleep['ts_str'] = df_sleep['date'].dt.strftime('%a %b %d %Y')

    df_sleep['start_time'] = df_sleep['start'].dt.strftime('%I:%M %p')
    df_sleep['end_time'] = df_sleep['end'].dt.strftime('%I:%M %p')

    df_sleep['start_hour_rel'] = df_sleep['start_hour']-24
    df_sleep['start_rel_last_7day_avg'] = df_sleep.set_index('date')['start_hour_rel'].rolling('7d', closed='both', ).mean().reset_index()['start_hour_rel'].shift(1)
    df_sleep['efficiency'] = 1- (df_sleep['awake'] / (df_sleep['end_hour']-df_sleep['start_hour_rel']))
    
    return df_sleep

def main():
    df_existing = pd.read_csv(datadir, parse_dates=['start', 'end'])

    if not datetime.today().strftime('%Y-%m-%d') in list(df_existing['end'].apply(lambda x: x.strftime('%Y-%m-%d'))):
        fb = fitbit(email='hasan.nagib@gmail.com', password=os.environ['fitbit_password'])
        time.sleep(4)
        df_new = fb.get_sleep_data()
        df = pd.concat([df_new, df_existing]).round(2).drop_duplicates()
        df.to_csv(datadir, index=None)


if __name__ == "__main__":
    main()
