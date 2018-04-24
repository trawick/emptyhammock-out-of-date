#!/bin/sh

if ! coverage run -m unittest discover; then
    exit 1
fi

coverage report -m

if ! flake8 .; then
    exit 1
fi
