========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |coveralls| |codecov|
        | |landscape|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-lyth/badge/?style=flat
    :target: https://readthedocs.org/projects/python-lyth
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/gmantelet/python-lyth.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/gmantelet/python-lyth

.. |requires| image:: https://requires.io/github/gmantelet/python-lyth/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/gmantelet/python-lyth/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/gmantelet/python-lyth/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/gmantelet/python-lyth

.. |codecov| image:: https://codecov.io/github/gmantelet/python-lyth/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/gmantelet/python-lyth

.. |landscape| image:: https://landscape.io/github/gmantelet/python-lyth/master/landscape.svg?style=flat
    :target: https://landscape.io/github/gmantelet/python-lyth/master
    :alt: Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/lyth.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/lyth

.. |wheel| image:: https://img.shields.io/pypi/wheel/lyth.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/lyth

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/lyth.svg
    :alt: Supported versions
    :target: https://pypi.org/project/lyth

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/lyth.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/lyth

.. |commits-since| image:: https://img.shields.io/github/commits-since/gmantelet/python-lyth/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/gmantelet/python-lyth/compare/v0.0.1...master



.. end-badges

A (monolithic) compiled language

* Free software: BSD 2-Clause License

Installation
============

::

    pip install lyth

You can also install the in-development version with::

    pip install https://github.com/gmantelet/python-lyth/archive/master.zip


Documentation
=============


https://python-lyth.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
