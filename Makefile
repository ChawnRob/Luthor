PYTHON ?= python3
export PYTHONPATH := src

.PHONY: install demo active test

install:
	$(PYTHON) -m pip install -r requirements.txt

demo:
	$(PYTHON) src/luthor/demo.py

active:
	$(PYTHON) src/luthor/active_demo.py

test:
	$(PYTHON) -m unittest discover -s tests -v
