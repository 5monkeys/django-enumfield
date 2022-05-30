.PHONY: test
test:
	python setup.py test

.PHONY: flake8
flake8:
	flake8 django_enumfield

.PHONY: mypy
mypy:
	mypy django_enumfield

.PHONY: isort
isort:
	isort -rc django_enumfield run_tests.py setup.py

.PHONY: black
black:
	black django_enumfield run_tests.py setup.py

.PHONY: black-check
black-check:
	black --check django_enumfield run_tests.py setup.py

.PHONY: checks
checks: mypy flake8 black-check

.PHONY: format
format: black isort

.PHONY: install
install:
	python setup.py install

.PHONY: develop
develop:
	python setup.py develop

.PHONY: coverage
coverage:
	coverage run --include=django_enumfield/* setup.py test

.PHONY: clean
clean:
	rm -rf build dist .tox/ *.egg *.egg-info .coverage* .eggs
	find . -name *.pyc -type f -delete
	find . -name __pycache__ -type d -delete

.PHONY: build
build: clean
	python -m pip install --upgrade pip
	python -m pip install --upgrade wheel
	python setup.py sdist bdist_wheel

.PHONY: release
release: build
	python -m pip install --upgrade twine
	python -m twine check dist/*
	python -m twine upload dist/*
