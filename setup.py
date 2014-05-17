#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='rcviz',
    version='0.1',
    description='Python call graph visualization for recursive functions',
    author='Ran',
    author_email='dugal@gmx.com',
    url='https://github.com/carlsborg/rcviz',
    packages=['rcviz'],
    include_package_data=True,
    install_requires=['pygraphviz'],
    zip_safe=False,
)
