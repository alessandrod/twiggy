#!/bin/bash
TWIGGY_UNDER_TEST=1 python -m unittest discover
sphinx-build -b doctest -d doc/_build/doctrees doc doc/_build/doctest

