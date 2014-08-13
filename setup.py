# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='pluct',
    version='0.7.0',
    description='python client to Jsonschema APIs',
    author='Marcos Daniel Petry',
    author_email='marcospetry@gmail.com',
    url='git@github.com:globocom/pluct.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='pluct.tests',
    packages=find_packages(exclude=('pluct.tests.*', 'pluct.tests')),
    include_package_data=True,
    install_requires=[
        'requests',
        'uritemplate',
        'jsonschema',
    ],
)
