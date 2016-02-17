from django.contrib import admin

from advanced_filters.admin import AdminAdvancedFiltersMixin

from .models import Client


class ClientAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    advanced_filter_fields = ('language', 'first_name',
                              ('assigned_to__email', 'Sales Rep.'))

admin.site.register(Client, ClientAdmin)
