.PHONY: test
test:
	python setup.py test

.PHONY: flake8
flake8:
	flake8 django_enumfield


.PHONY: isort
isort:
	isort -rc django_enumfield

.PHONY: black
black:
	find django_enumfield -name '*.py' | xargs black

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
