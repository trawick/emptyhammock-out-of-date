#!/usr/bin/env python

import os
import sys

from setuptools import setup

# Importing the package to get the version fails if our
# own requirements aren't available.
with open('e_ood/__init__.py') as f:
    line_1 = f.readline()
    _, _, VERSION = line_1.replace("'", "").strip().split(' ')

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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'requests', 'PyYAML',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    scripts=('out_of_date.py',),
)
