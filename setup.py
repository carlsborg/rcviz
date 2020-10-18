#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import setuptools

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    sys.exit()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='rcviz',
    version='0.1',
    description='Python call graph visualization for recursive functions',
    author='Ran',
    author_email='dugal@gmx.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/carlsborg/rcviz',
    packages=['rcviz'],
    include_package_data=True,
    install_requires=['pygraphviz'],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL2",
        "Operating System :: OS Independent",
    ]
)
