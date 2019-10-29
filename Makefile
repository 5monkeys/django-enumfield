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
checks: flake8 mypy black-check

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
	rm -rf .tox/ dist/ *.egg *.egg-info .coverage* .eggs

.PHONY: publish
publish: clean
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
