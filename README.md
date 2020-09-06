## Wahoo Heart Rate Data Reader 
<img width=200 src="https://github.com/hnagib/Wahoo-Fit-Reader/blob/master/img/wahoo-tickrx.png">

Using python to read and analyze heart rate data from Wahoo TickrX heart rate belt. Check out [notebook](https://nbviewer.jupyter.org/github/hnagib/Wahoo-Tickrs-Logs/blob/master/notebooks/hn-parse-fit-file.ipynb) for example usage. :warning: fitparse (v1.0.0) source code had to be modified to parse wahoo's .fit files. See [issue](https://github.com/dtcooper/python-fitparse/issues/113) for details.

:open_file_folder: Repo Organization
--------------------------------

    ├── src                
    │   ├── plotutils.py                         <-- Bokeh plotting functions    
    │   └── wahooreader.py                       <-- .fit file data reader
    │
    ├── notebooks          
    │   ├── hn-parse-fit-file.ipynb              <-- parsing and visualizing heart rate data         
    │   └── ...            
    │
    ├── data               
    │   ├── 2020-09-05.fit                       <-- sample .fit file      
    │   └── ... 
    │
    ├── Makefile                                 <- Makefile with commands to automate installation of python environment
    ├── requirements.txt                         <- List of python packages required     
    ├── README.md
    └── .gitignore         
