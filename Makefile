PYTHON ?= python3

venv:
	python3 -m venv ./venv \
		&& . venv/bin/activate \
		&& python3 -m pip install -r requirements.txt

rmvenv:
	rm -rf venv/
