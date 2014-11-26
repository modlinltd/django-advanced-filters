# Changelog

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

## 0.1 - Beta / concept initial version

* Initial commits
