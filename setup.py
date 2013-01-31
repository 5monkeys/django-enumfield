"""
Based entirely on Django's own ``setup.py``.
"""
import codecs
import os
import sys
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # NOQA


class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is at:
    #   /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific
    # fix for this in distutils.command.install_data#306. It fixes install_lib
    # but not install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to
        # the fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)

if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
enum_dir = 'django_enumfield'

for dirpath, dirnames, filenames in os.walk(enum_dir):
    # Ignore dirnames that start with '.'
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
    long_description=codecs.open(
        os.path.join(
            os.path.dirname(__file__),
            "README.rst"
        )
    ).read(),
    author="Hannes Ljungberg",
    author_email="hannes@5monkeys.se",
    url="http://github.com/5monkeys/django-enumfield",
    download_url="https://github.com/5monkeys/django-enumfield/tarball/%s" % (version,),
    keywords=["django", "enum", "field", "status", "state", "choices", "form", "model"],
    platforms=['any'],
    license='MIT',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
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
