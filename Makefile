.PHONY: test
test:
	pytest $(test)

.PHONY: flake8
flake8:
	flake8 django_enumfield

.PHONY: mypy
mypy:
	mypy django_enumfield

.PHONY: isort
isort:
	isort -rc django_enumfield setup.py

.PHONY: black
black:
	black django_enumfield setup.py

.PHONY: black-check
black-check:
	black --check django_enumfield setup.py

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

.PHONY: clean
clean:
	rm -rf .tox/ dist/ *.egg *.egg-info .coverage* .eggs

.PHONY: publish
publish: clean
	python setup.py sdist bdist_wheel
	python -m twine upload dist/*
