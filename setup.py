# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in customizer/__init__.py
from customizer import __version__ as version

setup(
	name='customizer',
	version=version,
	description='Custom for payroll ',
	author='ahmad',
	author_email='ahmad18189',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
