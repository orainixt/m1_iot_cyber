PYTHON = python3
VENV_DIR = .venv 
PIP = $(VENV_DIR)/bin/pip 
PY = $(VENV_DIR)/bin/python
SRC = src

REQ = requirements.txt 

.PHONY: help venv install run  

help:
	@echo "-- make run           -> launch main.py"
	@echo "-- make venv          -> create virtual environment"
	@echo "-- make install       -> install packets needed (requirements.txt)"

venv: 
	$(PYTHON) -m venv $(VENV_DIR) 

install: venv 
	$(PIP) install -r $(REQ) 

run:  
	$(PYTHON) $(SRC)/main.py