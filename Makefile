SHELL=/bin/bash

install-env:
	conda create -n wahoo python=3.7
	source activate wahoo && pip install -r requirements.txt
	conda install ipykernel
	python -m ipykernel install --user --name wahoo --display-name "wahoo"

uninstall-env:
	conda remove --name wahoo --all
