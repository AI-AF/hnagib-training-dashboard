import pandas as pd
from selenium import webdriver
from lxml import html
import time
import re
import numpy as np
import os
from datetime import datetime


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
        self.browser = webdriver.Chrome(chrome_driver_path)
        self.browser.get(self.url)
        self.login()

    def login(self):
        """
        Sign into WodUp using self.email and self.password
        """
        time.sleep(4)
        self.browser.find_element_by_xpath("//input[@type='email']").send_keys(self.email)
        self.browser.find_element_by_xpath("//input[@type='password']").send_keys(self.password)
        self.browser.find_element_by_xpath("//button[@id='ember694']").click()
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

        for log in sleep_logs[:3]:

            self.browser.find_element_by_xpath(log).click()
            time.sleep(4)

            tree = html.fromstring(self.browser.page_source)
            date.append(tree.xpath('//div[@class="sleep-log-edit ember-view"]/div/div/p/text()')[0])    


            start.append(self.browser.find_element_by_xpath('//input[@data-test-qa="start-time-input"]').get_attribute('value'))
            end.append(self.browser.find_element_by_xpath('//input[@data-test-qa="start-time-input"]/../../../following-sibling::div//input').get_attribute('value'))
            time.sleep(4)

            sleep_stages.append([float(tree.xpath(
                f'//li[@class="column legend-item {stage}"]//span[@class="legend-label"]/text()'
            )[0].strip().split(' - ')[-1][:-1])/100
                for stage in ['wake', 'rem', 'light', 'deep']
            ])

            self.browser.back()
            time.sleep(4)
        
        self.browser.close()
        
        df = pd.DataFrame({'date':date, 'start':start, 'end':end}).join(
            pd.DataFrame(sleep_stages, columns=['awake', 'rem', 'light', 'deep'])
        )

        df['start'] = pd.to_datetime(df['date'].astype(str)+" "+df['start']+ " PM")
        df['end'] = pd.to_datetime(df['date'].astype(str)+" "+df['end']+ " AM") + pd.Timedelta('1 days')
        df['duration'] = (df['end'] - df['start']).apply(lambda x: x.total_seconds())/60

        for stage in ['awake', 'rem', 'light', 'deep']:
            df[stage] = df[stage]*df['duration']

        df['time_asleep'] = df['rem'] + df['light'] + df['deep']
        df['start_hour'] = df['start'].dt.hour + (df['start'].dt.minute/60)
        df['end_hour'] = df['end'].dt.hour + (df['end'].dt.minute/60)
        
        return df
    

fb = fitbit(email='hasan.nagib@gmail.com', password=os.environ['fitbit_password'])
time.sleep(4)
df_new = fb.get_sleep_data()
df_existing = pd.read_csv('../data/sleep.csv', parse_dates=['start', 'end'])
df = pd.concat([df_new, df_existing]).round(2).drop_duplicates()
df.to_csv('../data/sleep.csv', index=None)
