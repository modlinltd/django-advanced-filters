from django.conf.urls import url

from advanced_filters.views import GetFieldChoices

urlpatterns = [
    url(r'^field_choices/(?P<model>.+)/(?P<field_name>.+)/?',
        GetFieldChoices.as_view(),
        name='afilters_get_field_choices'),

    # only to allow building dynamically
    url(r'^field_choices/$',
        GetFieldChoices.as_view(),
        name='afilters_get_field_choices'),
]
