import django

IGNORE_MIGRATIONS = django.VERSION < (1, 7)

if IGNORE_MIGRATIONS:
    collect_ignore = ["advanced_filters/migrations"]
