test:
	python setup.py test

flake8:
	flake8 django_enumfield

install:
	python setup.py install

develop:
	python setup.py develop

coverage:
	coverage run --source django_enumfield setup.py test
