#!/usr/bin/env python

import os
import sys

from setuptools import setup

# Importing the package to get the version fails if our
# own requirements aren't available.
with open('e_ood/__init__.py') as f:
    line_1 = f.readline()
    _, _, VERSION = line_1.split(' ')

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

setup(
    name='emptyhammock_out_of_date',
    packages=['e_ood'],
    include_package_data=True,
    license='Apache 2.0 License',
    version=VERSION,
    description='A Python app and library that analyzes "pip freeze" output',
    author='Emptyhammock Software and Services LLC',
    author_email='info@emptyhammock.com',
    url='https://github.com/trawick/emptyhammock-out-of-date',
    classifiers=[
        'License :: OSI Approved :: Apache 2.0 License',
        'Development Status :: 3 - Alpha',
    ],
    install_requires=[
        'requests', 'PyYAML',
    ],
    scripts=('out_of_date.py',),
)
