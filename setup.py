#!/usr/bin/env python3

from os.path import abspath, dirname, join
from setuptools import setup, find_packages


# Stolen from: https://github.com/pypa/pip/blob/master/setup.py
def read(rel_path):
    here = abspath(dirname(__file__))
    with open(join(here, rel_path)) as file_pointer:
        return file_pointer.read()


def get_metadata(rel_path, mdata):
    for line in read(rel_path).splitlines():
        if line.startswith(mdata):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find metadata string.")


def get_requirements(requirements):
    return [line.rstrip('\n') for line in open(requirements)]


INSTALL_REQUIRE = get_requirements('setup-requirements.txt')
LINT_REQUIRE = get_requirements('lint-requirements.txt')
TESTS_REQUIRE = get_requirements('test-requirements.txt')
DEV_REQUIRE = LINT_REQUIRE.extend(TESTS_REQUIRE)

setup(
    name='hostsman',
    version=get_metadata("src/hostsman/__init__.py", "__version__"),
    description='KISS and efficient tool to manage hosts files',
    long_description='KISS and efficient tool to manage hosts files',
    author=get_metadata("src/hostsman/__init__.py", "__author__"),
    author_email=get_metadata("src/hostsman/__init__.py", "__email__"),
    url='https://git.domain.tld/meliurwen/hostsman',
    license=get_metadata("src/hostsman/__init__.py", "__license__"),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Topic :: Utilities",
    ],
    install_requires=INSTALL_REQUIRE,
    tests_require=DEV_REQUIRE,
    test_suite="pytest",
    include_package_data=True,
    keywords=['hostnames', 'hostname', 'hostsfiles', 'dns', 'hosts'],
    entry_points={
        'console_scripts': ['hostsman = hostsman.__main__:main']
    },
)
