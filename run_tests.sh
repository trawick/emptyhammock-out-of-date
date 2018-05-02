#!/bin/sh

MIN_COVERAGE=94

if ! coverage run -m unittest discover; then
    exit 1
fi

if ! coverage report --fail-under ${MIN_COVERAGE}; then
    echo 'FAILED!' 1>&2
    exit 1
fi

if ! flake8 .; then
    exit 1
fi

if ! pylint out_of_date.py e_ood; then
    exit 1
fi
