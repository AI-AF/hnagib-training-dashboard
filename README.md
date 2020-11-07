## Training Dashboard
Hasan's [training dashboard](http://hnagib.com) aggregating data from Wahoo, WodUp & Fitbit.

[<img width=600 src="https://github.com/hnagib/training-dashboard/blob/master/img/dash-demo.png">](http://hnagib.com)


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
