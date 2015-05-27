#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="waterfall",
      version='0',
      author="Rachel Shorey",
      author_email='rshorey@sunlightfoundation.com',
      license="BSD",
      description="cascades foreign key merges",
      long_description="cascades foreign key merges when combining two django objects (postgres only)",
      url="",
      py_modules=[],
      packages=['waterfall.waterfall'],
      include_package_data=True,
      platforms=["any"],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.4",
                   ],
      )
