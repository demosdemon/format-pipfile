#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    setup_requires=[
        "git+https://github.com/demosdemon/pbr.git@resolve-valueerror#egg=pbr"
    ],
    pbr=True,
)
