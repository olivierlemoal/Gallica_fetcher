#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='gallica_fetcher',
    version='0.9',
    description='Script to fetch high definition scans from Gallica website.',
    packages=find_packages(),
    author='Olivier Le Moal',
    author_email='mail@olivierlemoal.fr',
    url='https://github.com/olivierlemoal/Gallica_fetcher',
    license='MIT',
    platforms=['any'],
    install_requires=['pillow'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
    ],
    entry_points={
        "console_scripts": [
            "gallica_fetcher = gallica_fetcher.gallica_fetcher:main",
        ]
    },
)