Changelog
=========

1.2.0 - Django 3 and more
-------------------------

It's finally time to drop the dirty old rags and don some fresh colors.

Thanks to effort from multiple contributors, this version includes support
for newest Django version.

Breaking Changes
~~~~~~~~~~~~~~~~

* Add support for Django 2.2 and 3.0
* Drop support for Django < 1.9
* Drop support for Python 3.3-3.4

*django-advanced-filters now support only* **python 2.7, and 3.5 - 3.8.**

Features
~~~~~~~~

- Switch deprecated force_text to force_str (Merge 0427d11)

Bug fixes
~~~~~~~~~

- Avoid installing newer braces (Merge 0427d11)
- Allow choices sort on None fields (Merge 142ecd0)

Docs / Tests
~~~~~~~~~~~~

- Update dependencies stated in the README
- Refactor some unittest test cases into pytest (Merge 41271b7)
- Test the CleanWhiteSpacesMixin helper

Misc
~~~~

- Update requirements for new test deps matrix (Merge 0427d11)
- Replace deprecated assertEquals (Merge 41271b7)
- Replace deprecated logger.warn with warning (Merge 41271b7)
- Bump test dependencies (Merge 41271b7)
- Update python and add Django classifiers


Contributors
~~~~~~~~~~~~

- Petr Dlouhý
- Alon Raizman
- Hugo Maingonnat
- Arpit
- Pavel Savchenko


1.1.1 - CHANGELOG rendering is hard
-----------------------------------

This release is for fixing the bug when installing with specific environment (
locale that defaults to CP-1252).

Bug fixes
~~~~~~~~~

- Add encoding='utf-8' to open() in setup.py (Merge 2fe81aa)

Docs / Other
~~~~~~~~~~~~

- add CONTRIBUTING.rst with common processes (Merge ee7907e)
- Update issue templates (Merge ee7907e)

Contributors
~~~~~~~~~~~~

- Rebecca Turner
- Pavel Savchenko


1.1.0 - The future is bright
----------------------------

This release highlights support for Django 2.0 and 2.1 as well as
deprecating support for versions Django < 1.7 and Python 2.6 and 3.3

Bug fixes
~~~~~~~~~

- bump django-braces==1.13 for Django 2 support (Merge 80e055e)
- use request context processor in test_project (Merge 80e055e)

Misc.
~~~~~

- ignore .DS_Store
- fixes for Django 2.0 and 1.11, update tests (Merge 80e055e)
- test in Django 2.1 (Merge d8d236d)
- add updated migrations of model attributes (Merge 80e055e)
- fix ValueError while creating empty form (Merge d8d236d)
- python 2.6 and django < 1.7 are deprecated
- lower and upper bounds in install_requires
- avoid all-catch except clause (Merge 80e055e)

Tests
~~~~~

- correct tox env django spec for ver 1.11 (Merge 80e055e)
- correct make_query assertion for Django>=2 (Merge 80e055e)
- update pytest-django in diff. envs + tox (Merge d8d236d)

Contributors
~~~~~~~~~~~~

- Goncalo Gomes
- predatell
- Petr Dlouhý
- benny daon
- Pavel Savchenko


1.0.7.1 - Fix PyPi fail
-----------------------

- Equivalent to the prev version, bumped since we can't reupload the files to PyPi.

1.0.7 - The holiday edition
---------------------------

This is mostly a minor release with the biggest being the `AdvancedFilterForm.Media` fix, 2 additional translations and bunch of docs cleanup (thanks everyone)!

Changes since 1.0.6:

Bug Fixes
~~~~~~~~~

- Fix AdvancedFilterForm Media declaration
- Fix pep8: E128 on forms.py (Merge d7acb36)

Features
~~~~~~~~

- Add Japanese locale (Merge d7acb36)
- Add Spanish locale (Merge 1a482cf)

Documentation:
~~~~~~~~~~~~~~

- a bit of polishing (Merge 4c88ea3)
- removing confusing migrations paragraph (Merge 4c88ea3)

Contributors:
~~~~~~~~~~~~~

- KINOSHITA Shinji
- Pavel Savchenko
- Benny Daon
- Mathieu Richardoz
- José Sánchez Moreno


1.0.6 - Bout Time
-----------------

This release is long overdue, and includes some important fixes as well as general improvements to code and documentation.

Bug Fixes
~~~~~~~~~

- fixing TypeError: can only concatenate tuple (not "list") to tuple
- ensure select2 is included last (Merge 9831ba5)
- add script to load jQuery globally
- remove invalid template variables
- fix input focusing error in chrome
- fix error when one missing range parameter caused error + test (Merge 365b646)

Features
~~~~~~~~

- don't override original change_list_templates in AdminAdvancedFiltersMixin
- make date range placeholder more pleasant (Merge 365b646)
- add created_at field
- Russian locale provided

Documentation
~~~~~~~~~~~~~

   - make it clear easy-select2 is not required anymore (Merge 9831ba5)
   - Clarify how to import AdminAdvancedFiltersMixin in README

Tests
~~~~~

   - add more fields/filter to test ModelAdmin

Contributors
~~~~~~~~~~~~

   - Grigoriy Beziuk
   - Никита Конин
   - Pavel Savchenko
   - Yuval Adam
   - Petr Dlouhý


1.0.5 - Compatibility bump
--------------------------

Bugs
~~~~

- updated AdvancedFilterQueryForm to include numeric comparison operators (Merge d3ee9f4)
- Fixed a bug where editing an existing Advanced Filter defaulted all operators to 'Equals' (Merge d3ee9f4)
- set AFQFormSet extra=0 instead of extra=1. I did this because having to check Delete is not clear to end users. (Merge d3ee9f4)
- changed the Advanced Filter admin so you a User by default can only view/edit filters that they create (unless they are a superuser) (Merge d3ee9f4)
- Fixed failing tests. Fixed bug where users weren't properly getting permissions to change or delete their filters (Merge d3ee9f4)
- changed solution for extra form appearing on editing. Now initialize form checks for falsy value for extra rather than extra just being None (Merge d3ee9f4)
- removed 'not instance from requirements for no extras (Merge d3ee9f4)
- pep8 fix (Merge d3ee9f4)
- Fixed labeling error with 'Greater Than or Equal To' (Merge d3ee9f4)
- Changes URL declaration to avoid deprecated pattern
- select2 only initializes if there are choices available. otherwise, the standard text input will be used (Merge 35d7063)
- Revert "select2 only initializes if there are choices available. otherwise, the standard text input will be used" (Merge 35d7063)
- updated query for choices for select2 field so that it will take only distinct choices. This allows max_choices to be the maximum unique choices. (Merge 35d7063)
- Changes URL declaration to avoid deprecated pattern (Merge 35d7063)
- refactored retrieval of choices so that the db is getting distinct values; added test (Merge 35d7063)
- pep8 (Merge 35d7063)
- Use order_by to avoid ambiguity
- drop django-easy-select2 and include select2 directly

Tests
~~~~~

- test with both Python 3.5 and Django 1.10
- removed print statement from test (Merge 35d7063)
- fixed failing test to account for new distinct for max choices (Merge 35d7063)
- added test to make sure all operators are properly restored from Queries (Merge d3ee9f4)

Contributors
~~~~~~~~~~~~

- Pavel Savchenko
- PJ Passalacqua
- Hermano Cabral


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
