#!/usr/bin/env python

import subprocess
import sys

import setuptools

try:
    from numpy import get_include
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.19.2"])
    from numpy import get_include

try:
    from Cython.Build import cythonize
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Cython==0.29.22"])
    from Cython.Build import cythonize

setuptools.setup(
    name="streamp3",
    version="0.1.7",
    description="streaming mp3 decoder",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pylon/streamp3/",
    author="Brent M. Spell",
    author_email="brent@pylon.com",
    packages=setuptools.find_packages(),
    setup_requires=["setuptools", "wheel", "numpy==1.19.2", "Cython>=0.29.22"],
    install_requires=["setuptools", "wheel", "numpy==1.19.2", "Cython>=0.29.22"],
    python_requires=">=3.6",
    ext_modules=cythonize(
        [setuptools.Extension("lame.hip", ["lame/hip.pyx"], libraries=["mp3lame"])]
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
