#!/usr/bin/env python

from __future__ import print_function

import os
import re
import sys

from setuptools import setup

# Importing the package to get the version fails if our
# own requirements aren't available.
version = None
with open('e_out_of_date/__init__.py') as f:
    for line in f:
        mo = re.match(r"^__version__ = '([^']+)'$", line)
        if mo:
            version = mo.group(1)
if not version:
    print('Could not find package version', file=sys.stderr)
    sys.exit(1)

if sys.argv[-1] == 'version':
    print('Version: %s' % version)
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

setup(
    name='emptyhammock_out_of_date',
    packages=['e_out_of_date'],
    include_package_data=True,
    license='Apache 2.0 License',
    version=version,
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
