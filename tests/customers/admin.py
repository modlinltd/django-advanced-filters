from django.contrib import admin

from advanced_filters.admin import AdminAdvancedFiltersMixin

from .models import Client


class ClientAdmin(AdminAdvancedFiltersMixin, admin.ModelAdmin):
    pass

admin.site.register(Client, ClientAdmin)
