#!/usr/bin/python

from setuptools import setup, find_packages
setup( name='picts_gif',
       version='1.0.0',
       author='Vito Foderà',
       author_email='vito.fodera2@studio.unibo.it',
       packages=find_packages(),
       package_dir={'picts_gif': 'picts_gif'},
       include_package_data=True,
       license='MIT')