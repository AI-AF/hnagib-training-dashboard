SHELL=/bin/bash

install-env:
	conda create -n hnagib python=3.7
	source activate hnagib && pip install -r requirements.txt
	conda install ipykernel
	python -m ipykernel install --user --name hnagib --display-name "wahoo"

uninstall-env:
	conda remove --name hnagib --all
