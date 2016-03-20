# Changelog

## 1.0.2 - A Better Future

This release features better test coverage and support for Django 1.9.

### Bugs
   - stretch formset table to the modal container width
   - toggle advanced `vendor/jquery` dir according to Django version
   - retain support older Django versions
   - clean up legacy tags in templates

### Tests
   - add admin views tests
   - add Django 1.9 to test matrix
   - other minor improvements

### Docs
   - Improve README with a newer screenshot and pretty tables for badges

### Contributors:
   - Pavel Savchenko
   - Leonardo J. Caballero G
   - Schuyler Duveen

## 1.0.1 - A Public Release

### Bugs
   - proper support for py26 and py3X and different Django releases
   - avoid querying all instances for choices
   - resolve settings inside view and refine error handling

### Tests
   - add doctests to the `form_helpers`
   - add tests for `forms`
   - add test case `views.TestGetFieldChoicesView`
   - setup.py/travis: add `test-reqs.txt` as extras_require
   - refactor testing to use `py.test` and run `tox` from `setup.py`
   - travis: use latest version of each Django release

### Docs:
   - `README`: explain what we test against

## 1.0 - First contact

#### Major changes
* Add a new (required) field [`AdvancedFilter.model`](README.md#model-correlation)
* Add parsing query dict into initialized formsets (allows for [editing existing instance](README.md#editing-previously-created-advanced-filters)).
* Add [`AdvancedFilterAdmin`](#editing-previously-created-advanced-filters) for actually accessing and [editing existing `AdvancedFilter` instances](README.md#editing-previously-created-advanced-filters).
* Use [Select2](https://github.com/asyncee/django-easy-select2) and an AJAX view to
dynamically populate [`field` options](README.md#fields).
* Add proper support for nested serialization of queries.

#### Minor changes
* Implement more [`operators`](README.md#operators) (`isnull`, `istrue` and `isfalse`)
* Allow [custom verbose naming of fields in advanced_filter_fields](README.md#custom-naming-of-fields)
* Add helper methods to the model to hide (and decouple) core serialization functionality from users.
* Strip whitespace in field values validation
* Setup and packaging (`setup.py`/`MANIFEST.in`)
* Hide `QSerializer` calling logic in the model
* Allow modifying `advanced_filter_form` property (defaults to `AdvancedFilterForm`)
* Correct documentation regarding position of mixin in subclass (issue #1)
