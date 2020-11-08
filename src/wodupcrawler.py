import pandas as pd
from selenium import webdriver
from lxml import html
import time
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime
import os

datadir = '/Users/hasannagib/Documents/s3stage/wodup/'


class WodUp:

    def __init__(self, email, password, username, chrome_driver_path='../src/chromedriver'):
        """

        :param email: Email address login for WodUp
        :param password: WodUp login password
        :param url: url for profile/user to scrape
        :param chrome_driver_path: path to chromedriver executable
        """
        self.url = f'https://www.wodup.com/{username}'
        self.email = email
        self.password = password
        self.username = username
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(
            chrome_driver_path, 
            #options=chrome_options
            ) #, options=chrome_options
        self.browser.get(self.url)
        self.login()
        self.raw_logs = {}
        self.logs = {}
        self.session_urls = {}
        self.session_wods = {}

    def login(self):
        """
        Sign into WodUp using self.email and self.password
        """
        time.sleep(2)
        self.browser.find_element_by_xpath("//input[@name='username']").send_keys(self.email)
        self.browser.find_element_by_xpath("//input[@type='password']").send_keys(self.password)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(2)

    def get_timeline_tree(self, dt, wait=1.5):
        """
        Get html tree for a given movement
        :param movement: movement to pull html for
        :param wait: wait to load page
        :return:
        """

        self.browser.get(f'https://www.wodup.com/timeline?date={dt}')
        time.sleep(wait)
        return html.fromstring(self.browser.page_source)

    def get_session_urls(self, dates, overwrite_dates=[]):
        for dt in dates:
            if (dt not in self.session_urls.keys())|(dt in overwrite_dates):
                urls = []
                for url in self.get_timeline_tree(dt).xpath('//a/@href'):
                    if (url.startswith(f'/{self.username}/sessions/')) and url.endswith('result'):
                        urls.append(url)

                if len(urls) > 0:
                    self.session_urls[dt] = urls
                else:
                    self.session_urls[dt] = None

        return self.session_urls

    def get_session_wods(self, overwrite_dates=[]):
        for k, v in self.session_urls.items():
            if (k not in self.session_wods.keys())|(k in overwrite_dates):
                wods = []
                if v:
                    for url in v:
                        self.browser.get('https://wodup.com' + url)
                        time.sleep(1.5)
                        e = self.browser.find_element_by_xpath("//div[@id='WODUP_ACTIVITY_DETAIL_SELECTED_ITEM_ID']/a/div")
                        wods.append(e.get_attribute('innerHTML'))
                else:
                    wods = ['', '', '', '']

                self.session_wods[k] = wods

        return self.session_wods


def get_latest_wodup_log_date(wods):
    dts = sorted(wods.keys())
    latest_wodup_log_dt = dts[-1]

    i = -1
    while wods[latest_wodup_log_dt] == '<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>': 
        i -= 1
        latest_wodup_log_dt = dts[i]

    return latest_wodup_log_dt


def read_wods_json(file):
    with open(file) as json_file:
        wods = json.load(json_file)

    for k,v in wods.items():
        wods[k] = '<p>&nbsp;</p>'.join(v)
        
    df_wod = pd.DataFrame(wods, index=['html']).T
    df_wod.index.name = 'date'
    df_wod = df_wod.reset_index()
    df_wod['date'] = pd.to_datetime(df_wod['date'])

    return wods, df_wod

def main():
    with open(f'{datadir}session_urls.json') as json_file:
        urls = json.load(json_file)

    with open(f'{datadir}session_wods.json') as json_file:
        wods = json.load(json_file)

    # Get list of dates to look urls for
    dts = [dt.strftime('%Y-%m-%d') for dt in pd.date_range('2019-09-16', datetime.today())]
    
    # Overwrite scrape data for these days to pick up logs entered after script run
    overwrite_dates = dts[-3:]
    print('Scraping WoUp logs for: ', overwrite_dates)


    wu = WodUp(
        email='hasan.nagib@gmail.com',
        password=os.environ['wodify_password'],
        username='hasannagib'
    )

    wu.session_urls = urls
    wu.session_wods = wods

    # Add missing urls
    urls = wu.get_session_urls(dts, overwrite_dates)
    with open(f'{datadir}session_urls.json', 'w') as outfile:
        json.dump(urls, outfile)
    
    # Get wods from urls
    wods = wu.get_session_wods(overwrite_dates)
    for k, v in wods.items():
        if len(v) < 4:
            for i in range(4-len(v)):
                wods[k].append('')

    with open(f'{datadir}session_wods.json', 'w') as outfile:
        json.dump(wods, outfile)


    wu.browser.quit()

if __name__ == '__main__':
    main()
