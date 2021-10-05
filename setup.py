#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
from zana import version

requirements = [
]

test_requirements = [
    "pytest",
]

setuptools.setup(
    name="zana",
    version=version.__version__,

    description="",
    long_description="",

    author="Sam Nicholls",
    author_email="sam@samnicholls.net",

    maintainer="Sam Nicholls",
    maintainer_email="sam@samnicholls.net",

    packages=setuptools.find_packages(),
    install_requires=requirements,

    entry_points = {
    },

    test_suite="tests",
    tests_require=test_requirements,

)
