from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('advanced_filters/', include('advanced_filters.urls'))
]
