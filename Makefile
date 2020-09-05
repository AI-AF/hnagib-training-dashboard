SHELL=/bin/bash

install-env:
	conda create -n grt python=3.7
	conda activate grt && pip install -r requirements.txt
	conda install ipykernel
	python -m ipykernel install --user --name grt --display-name "grt"

uninstall-env:
	conda remove --name grt --all
