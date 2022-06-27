from django.urls import path

from advanced_filters.views import GetFieldChoices

urlpatterns = [
    path('field_choices/<model>/<field_name>/',
        GetFieldChoices.as_view(),
        name='afilters_get_field_choices'),

    # only to allow building dynamically
    path('field_choices/',
        GetFieldChoices.as_view(),
        name='afilters_get_field_choices'),
]
