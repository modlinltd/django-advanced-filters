Changelog
=========

1.0.4 - Unbreak Python 3
------------------------

This release contains a fix to allow distribution installation on Python 3 which was broken since 1.0.2

1.0.3 - The Package Fix
-----------------------

This is a quick fix for packaging (setup.py) errors and documentation.

Bugs
~~~~

-  add missing Django 1.7 migrations
-  README updated to mention ``manage.py migrate`` command
-  Use ReST for README and CHANGELOG: avoid conversion from markdown


1.0.2 - A Better Future
-----------------------

This release features better test coverage and support for Django 1.9.

Bugs
~~~~

-  stretch formset table to the modal container width
-  toggle advanced ``vendor/jquery`` dir according to Django version
-  retain support older Django versions
-  clean up legacy tags in templates

Tests
~~~~~

-  add admin views tests
-  add Django 1.9 to test matrix
-  other minor improvements

Docs
~~~~

-  Improve README with a newer screenshot and pretty tables for badges

Contributors:
~~~~~~~~~~~~~

-  Pavel Savchenko
-  Leonardo J. Caballero G
-  Schuyler Duveen

1.0.1 - A Public Release
------------------------

Bugs
~~~~

-  proper support for py26 and py3X and different Django releases
-  avoid querying all instances for choices
-  resolve settings inside view and refine error handling

Tests
~~~~~

-  add doctests to the ``form_helpers``
-  add tests for ``forms``
-  add test case ``views.TestGetFieldChoicesView``
-  setup.py/travis: add ``test-reqs.txt`` as extras\_require
-  refactor testing to use ``py.test`` and run ``tox`` from ``setup.py``
-  travis: use latest version of each Django release

Docs:
~~~~~

-  ``README``: explain what we test against

1.0 - First contact
-------------------

Major changes
~~~~~~~~~~~~~

-  Add a new (required) field
   ```AdvancedFilter.model`` <https://raw.githubusercontent.com/modlinltd/django-advanced-filters/develop/README.rst#model-correlation>`__
-  Add parsing query dict into initialized formsets (allows for `editing
   existing
   instance <https://raw.githubusercontent.com/modlinltd/django-advanced-filters/develop/README.rst#editing-previously-created-advanced-filters>`__).
-  Add
   ```AdvancedFilterAdmin`` <#editing-previously-created-advanced-filters>`__
   for actually accessing and `editing existing ``AdvancedFilter``
   instances <https://raw.githubusercontent.com/modlinltd/django-advanced-filters/develop/README.rst#editing-previously-created-advanced-filters>`__.
-  Use `Select2 <https://github.com/asyncee/django-easy-select2>`__ and
   an AJAX view to dynamically populate ```field``
   options <https://raw.githubusercontent.com/modlinltd/django-advanced-filters/develop/README.rst#fields>`__.
-  Add proper support for nested serialization of queries.

Minor changes
~~~~~~~~~~~~~

-  Implement more ```operators`` <https://raw.githubusercontent.com/modlinltd/django-advanced-filters/develop/README.rst#operators>`__ (``isnull``,
   ``istrue`` and ``isfalse``)
-  Allow `custom verbose naming of fields in
   advanced\_filter\_fields <https://raw.githubusercontent.com/modlinltd/django-advanced-filters/develop/README.rst#custom-naming-of-fields>`__
-  Add helper methods to the model to hide (and decouple) core
   serialization functionality from users.
-  Strip whitespace in field values validation
-  Setup and packaging (``setup.py``/``MANIFEST.in``)
-  Hide ``QSerializer`` calling logic in the model
-  Allow modifying ``advanced_filter_form`` property (defaults to
   ``AdvancedFilterForm``)
-  Correct documentation regarding position of mixin in subclass (issue
   #1)
