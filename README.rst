=============
Core Main App
=============

This Django reusable app contains the main functionalities for the curator
core project.

Pre-requisites
==============

For automated and manual install, the following software are needed:

* ``python``
* ``pip``
* virtual env (``conda`` or ``venv``)

In addition, for manual setup, ``git`` is needed.

Installation
============

Automated installation
----------------------

.. code:: bash

  $ pip install core_main_app

Manual installation
-------------------

.. code:: bash

    $ git clone https://github.com/usnistgov/core_main_app.git
    $ cd core_main_app
    $ python setup.py
    $ pip install sdist/*.tar.gz


Configuration
=============

Edit the setting.py file
------------------------

Add the ``"core_main_app"`` and ``"tz_detect"`` under ``INSTALLED_APPS`` as
such:

.. code:: python

    INSTALLED_APPS = [
        ...
        "tz_detect",
        "core_main_app",
    ]

Add the middleware required by ``tz_detect``:

.. code:: python

    MIDDLEWARE = (
        ...
        'tz_detect.middleware.TimezoneMiddleware',
    )


Edit the urls.py file
---------------------

Add the ``core_main_app`` urls to the Django project as such.

.. code:: python

    url(r'^', include("core_main_app.urls")),


Internationalization (i18n)
===========================

Before running the project, don't forget to compile the translation file at
project level. i18n uses the ``gettext`` package, so please make sure it is
installed prior to using this command.

.. code:: bash

    $ python manage.py compilemessages

Tests
=====

To play the test suite created for this package, download the git repository
and run:

.. code:: bash

  $ python runtests.py

Documentation
=============

Documentation has been generated using Sphinx. To generate a local version of
the docs, please clone the repository and run:

.. code:: bash

  $ cd docs/
  $ make html

Or, directly using Sphinx:

.. code:: bash

  $ cd docs/
  $ sphinx-build -b html . ../dist/_docs
