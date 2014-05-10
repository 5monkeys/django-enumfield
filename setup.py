import os
import sys
from io import open
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


class osx_install_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)


if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}


def fullsplit(path, result=None):
    """ Split a pathname into components (the opposite of os.path.join) in a platform-neutral way."""
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
enum_dir = 'django_enumfield'

for dirpath, dirnames, filenames in os.walk(enum_dir):
    if os.path.basename(dirpath).startswith("."):
        continue
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

version = __import__('django_enumfield').__version__

setup(
    name="django-enumfield",
    version=version,
    description="Custom Django field for using enumerations of named constants",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.rst"), encoding='utf-8').read(),
    author="Hannes Ljungberg",
    author_email="hannes@5monkeys.se",
    url="http://github.com/5monkeys/django-enumfield",
    download_url="https://github.com/5monkeys/django-enumfield/tarball/{version}".format(version=version),
    keywords=["django", "enum", "field", "status", "state", "choices", "form", "model"],
    platforms=['any'],
    license='MIT',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        'Framework :: Django',
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass=cmdclasses,
    data_files=data_files,
    packages=packages,
    tests_require=['Django'],
    test_suite='run_tests.main',
)
