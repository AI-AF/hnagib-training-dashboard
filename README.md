# Wahoo TickrX Data Analysis

:construction:
Line `291` of `~/opt/anaconda3/envs/wahoo/lib/python3.7/site-packages/fitdecode/records.py` changed:

```python
    0x07: BaseType(name='string', identifier=0x07, fmt='s', parse=lambda x: x),
}
```

:open_file_folder: Repo Organization
--------------------------------

    ├── src                <- Modules used in and shared by different lectures & assignments
    │   ├── ...       
    │   └── ...            
    │
    ├── notebooks          <- Jupyter notebooks for each lecture
    │   ├── ...            
    │   └── ...            
    │
    ├── data               <- Directory for storing small datasets and staging larger ones
    │   ├── ...       
    │   └── ... 
    │
    ├── Makefile           <- Makefile with commands to automate installation of python environment
    ├── requirements.txt   <- List of python packages required     
    ├── README.md
    └── .gitignore         
