## [hnagib.com](http://www.hnagib.com)

Welcome to my health & fitness data journal project! This project was born out of my love for fitness, data & Bokeh. This is a Bokeh dashboard hosted on AWS S3. The data is sourced from my Fitbit, Polar HR10, Wahoo TickerX and WodUp account. The data is refreshed by a daily batch job. 

Why did I go through the trouble to aggregate all this data from different devices and services? What's the point? For me this is a tool to help keep me motivated and accountable. Now that I have put in so much effort into visualizing my data, I guess I have to keep working out to produce more data to visualize... 💪🏽🤓 

:open_file_folder: Repo Organization
--------------------------------

    ├── src                
    │   ├── chromedriver                         <-- chromedriver for selenium    
    │   ├── fitetl.py                            <-- wahoo .fit file ETL job    
    │   ├── sleepetl.py                          <-- Fitbit sleep data scrape and ETL job
    │   ├── htmltext.py                          <-- html content for hnagib.com      
    │   ├── plotutils.py                         <-- Bokeh plotting functions   
    │   ├── dashboard.py                         <-- generate hnagib.com page
    │   ├── wahooreader.py                       <-- module for processing wahoo .fit files       
    │   └── wodupcrawler.py                      <-- module for scraping WodUp
    │
    ├── notebooks          
    │   ├── hn-calendar-plots.ipynb              <-- demo of calendar plot heatmaps         
    │   └── ...            
    │
    ├── data                                     <-- directory for staging data
    │   └── ... 
    │
    ├── Makefile                                 <- Makefile with commands to automate installation of python environment
    ├── requirements.txt                         <- List of python packages required     
    ├── README.md
    └── .gitignore         
