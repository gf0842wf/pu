# -*- coding: utf-8 -*-
from distutils.core import setup

import pu


classifiers = [
    "Programming Language :: Python 2.7",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='pu',
    version=pu.version,
    packages=[
        'pu',
        'pu.pattern',
        'pu.adt',
    ],
    description='Python utils',
    license='MIT',
    author='fk',
    author_email='gf0842wf@gmail.com',
    url='https://github.com/gf0842wf/pu',
    keywords=['python', 'util'],
    classifiers=classifiers,
)