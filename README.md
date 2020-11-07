## [hnagib.com](http://www.hnagib.com)

<div class="header" style="style=font-size:12px; font-family:helvetica; color:grey; margin-left: 40px; width: 400px; float: left;">
<h1>Hasan Nagib</h1> 
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<a href="https://www.linkedin.com/in/hnagib?_l=en_US" class="fa fa-linkedin" style="font-size:24px"></a>
<a href="https://github.com/hnagib" class="fa fa-github" style="font-size:24px"></a>
<a href="https://www.facebook.com/bigannasah/" class="fa fa-facebook" style="font-size:24px"></a>
<a href="https://www.instagram.com/hnagib/" class="fa fa-instagram" style="font-size:24px"></a>
<a href="mailto:hasan.nagib@gmail.com?subject = Hasan's fitness data blog&body = Hello!" class="fa fa-envelope" style="font-size:24px"></a>
<a href="https://s3.amazonaws.com/hnagib.com/Hasan-Nagib-Resume.pdf" class="tooltip fa fa-file" style="font-size:24px">
<span class="tooltiptext">Resume</span></a>

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
