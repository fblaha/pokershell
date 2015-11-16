#!/usr/bin/env python

PROJECT = 'pokershell'

# Change docs/sphinx/conf.py too!
VERSION = '0.1'

from setuptools import setup, find_packages

setup(
    name=PROJECT,
    version=VERSION,

    description='Poker Shell',

    author='Filip Blaha',
    author_email='blahaf@gmail.com',

    classifiers=['Environment :: Console', ],

    platforms=['Any'],

    scripts=[],

    provides=[],

    namespace_packages=[],
    packages=find_packages(),
    package_data={
        'pokershell.eval': ['preflop/*.txt']},
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'pokershell = pokershell.shell:main'
        ]
    },

    zip_safe=False,
)
