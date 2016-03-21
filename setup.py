# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='pluct',
    version='1.2.7',
    description='JSON Hyper Schema client',
    long_description=open('README.rst').read(),
    author='Marcos Daniel Petry',
    author_email='marcospetry@gmail.com',
    url='https://github.com/globocom/pluct',
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'uritemplate>=0.6,<1.0',
        'jsonschema',
        'jsonpointer',
    ],
)
