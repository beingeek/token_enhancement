# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in token_enhancement/__init__.py
from token_enhancement import __version__ as version

setup(
	name="token_enhancement",
	version=version,
	description="Token Enhancement for paint mixing company",
	author="Createch Global Solutions",
	author_email="furqan@createch.solutions",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
