# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
from setuptools import setup, find_packages, findall


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)
    return requirements


def not_py(file_path):
    return not(file_path.endswith('.py') or file_path.endswith('.pyc'))

core_packages = find_packages()
core_package_data = {}
for package in core_packages:
    package_path = package.replace('.', '/')
    core_package_data[package] = filter(not_py, findall(package_path))

setup(
    name='pluct',
    version='0.2.0',
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
    packages=core_packages,
    package_data=core_package_data,
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
)
