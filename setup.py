#!/usr/bin/env python

PROJECT = 'minsk'

# Change docs/sphinx/conf.py too!
VERSION = '0.1'

from setuptools import setup, find_packages

setup(
    name=PROJECT,
    version=VERSION,

    description='Minsk Shell',

    author='Filip Blaha',
    author_email='blahaf@gmail.com',

    classifiers=['Environment :: Console', ],

    platforms=['Any'],

    scripts=[],

    provides=[],

    namespace_packages=[],
    packages=find_packages(),
    package_data={
        'minsk.eval': ['preflop/*.txt']},
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'minsk = minsk.shell:main'
        ]
    },

    zip_safe=False,
)
