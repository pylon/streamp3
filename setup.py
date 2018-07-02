#!/usr/bin/env python

import setuptools
from distutils.core import setup
from distutils.extension import Extension

setup(name='streamp3',
      version='0.1.5',
      description="streaming mp3 decoder",
      long_description=open('README.md', 'r').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/pylon/streamp3/',
      author="Brent M. Spell",
      author_email='brent@pylon.com',
      packages=setuptools.find_packages(),
      setup_requires=['Cython>=0.28.3'],
      ext_modules=[Extension('lame.hip',
                             ['lame/hip.pyx'],
                             libraries=['mp3lame'])],
      classifiers=("Programming Language :: Python :: 3",
                   "License :: OSI Approved :: Apache Software License",
                   "Operating System :: OS Independent"))
