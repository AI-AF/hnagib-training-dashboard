## Training Dashboard
My personal training dashboard aggregating data from Wahoo, WodUp & Fitbit. Check out the dashboard at [hnagib.com](hnagib.com)

:open_file_folder: Repo Organization
--------------------------------

    ├── src                
    │   ├── chromedriver                         <-- chromedriver for selenium    
    │   ├── fitetl.py                            <-- wahoo .fit file ETL job    
    │   ├── plotutils.py                         <-- Bokeh plotting functions   
    │   ├── refresh_dashboard.py                 <-- hnagib.com dashboard update
    │   ├── wahooreader.py                       <-- module for processing wahoo .fit files       
    │   └── wodupcrawler.py                      <-- module for scraping WodUp
    │
    ├── notebooks          
    │   ├── hn-hr-dataviz.ipynb                  <-- demo of hnagib.com dashboard build         
    │   └── ...            
    │
    ├── data                                     <-- directory for staging data
    │   ├── 2020-09-05.fit                       <-- sample .fit file      
    │   └── ... 
    │
    ├── Makefile                                 <- Makefile with commands to automate installation of python environment
    ├── requirements.txt                         <- List of python packages required     
    ├── README.md
    └── .gitignore         
