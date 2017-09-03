from django.contrib import admin

from advanced_filters.admin import AdminAdvancedFiltersMixin

from .models import Client


class ClientAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    list_display = ('language', 'first_name', 'last_name', 'assigned_to', 'email')
    list_filter = ('language', 'last_name')
    advanced_filter_fields = ('language', 'first_name',
                              ('assigned_to__email', 'Sales Rep.'))

admin.site.register(Client, ClientAdmin)
