#!/usr/bin/env python

import setuptools

PROJECT = 'pokershell'
VERSION = '0.1'

setuptools.setup(
    name=PROJECT,
    version=VERSION,
    description='Poker Shell',
    author='Filip Blaha',
    author_email='blahaf@gmail.com',
    classifiers=['Environment :: Console', ],
    platforms=['Any'],
    namespace_packages=[],
    packages=setuptools.find_packages(),
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
