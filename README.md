django-advanced-filters
=======================

A django ModelAdmin mixin which adds advanced filtering abilities to the admin.

Mimics the advanced search feature in [VTiger](https://www.vtiger.com/),
[see here for more info](https://wiki.vtiger.com/index.php/Create_Custom_Filters)


TODO
----

* Add more tests (specifically the form and view parts)
* Add packaging (setup.py, etc...)
* Add edit/view functionality to the filters
* Add permission user/group selection functionality to the filter form


Requirements
============
Django >= 1.5


Integration Example
===================

Extending a ModelAdmin is pretty straightforward:

    class ProfileAdmin(models.ModelAdmin, AdminAdvancedFiltersMixin):
        list_filter = ('name', 'language', 'ts')   # simple list filters

        # select from these fields in the advanced filter creation form
        advanced_filter_fields = (
            'name', 'language', 'ts'
            # even use related fields as lookup fields
            'country__name', 'posts__title', 'comments__content'
        )

Adding a new advanced filter (see below) will display a new list filter
named "Advanced filters" which will list all the filter the currently
logged in user is allowed to use (by default only those he/she created).


Adding new Advanced Filters
===========================

By default the mixin uses a template which extends django's built-in
`change_list` template. This template is based off of grapelli's
fork of this template, hence the 'grp' classes and funny looking javascript.

The default template also uses the superb [magnificPopup](dimsemenov/Magnific-Popup)
which is currently linked from a CDN.

Regardless of the above, you can easily write your own template which uses
context variables `{{ advanced_filters }}` and
`{{ advanced_filters.formset }}`, to render the advanced filter creation form.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/modlinltd/django-advanced-filters/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

