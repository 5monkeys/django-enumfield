.PHONY: test
test:
	python setup.py test

.PHONY: flake8
flake8:
	flake8 --ignore=E501,F403 --max-complexity 12 django_enumfield

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
