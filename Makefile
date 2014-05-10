test:
	python setup.py test

flake8:
	flake8 --ignore=E501,F403 --max-complexity 12 django_enumfield

install:
	python setup.py install

develop:
	python setup.py develop

coverage:
	coverage run --include=django_enumfield/* setup.py test
