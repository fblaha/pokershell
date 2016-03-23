#!/usr/bin/env python

import setuptools

PROJECT = 'pokershell'
VERSION = '0.1.5'

setuptools.setup(
    name=PROJECT,
    version=VERSION,
    description="Poker Shell - Texas hold 'em command line calculator and simulator",
    author='Filip Blaha',
    author_email='blahaf@gmail.com',
    url='https://github.com/fblaha/pokershell',
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
    keywords=['poker'],
    zip_safe=False
)
