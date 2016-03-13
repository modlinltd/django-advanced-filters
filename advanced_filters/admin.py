import logging

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import unquote
from django.shortcuts import resolve_url

from .forms import AdvancedFilterForm
from .models import AdvancedFilter


logger = logging.getLogger('advanced_filters.admin')


class AdvancedListFilters(admin.SimpleListFilter):
    """Allow filtering by stored advanced filters (selection by title)"""
    title = _('Advanced filters')

    parameter_name = '_afilter'

    def lookups(self, request, model_admin):
        if not model_admin:
            raise Exception('Cannot use AdvancedListFilters without a '
                            'model_admin')
        model_name = "%s.%s" % (model_admin.model._meta.app_label,
                                model_admin.model._meta.object_name)
        return AdvancedFilter.objects.filter_by_user(request.user).filter(
            model=model_name).values_list('id', 'title')

    def queryset(self, request, queryset):
        if self.value():
            advfilter = AdvancedFilter.objects.filter(id=self.value()).first()
            if not advfilter:
                logger.error("AdvancedListFilters.queryset: Invalid filter id")
                return queryset
            query = advfilter.query
            logger.debug(query.__dict__)
            return queryset.filter(query).distinct()
        return queryset


class AdminAdvancedFiltersMixin(object):
    """ Generic AdvancedFilters mixin """
    change_list_template = "admin/advanced_filters.html"
    advanced_filter_form = AdvancedFilterForm

    def __init__(self, *args, **kwargs):
        super(AdminAdvancedFiltersMixin, self).__init__(*args, **kwargs)
        # add list filters to filters
        self.list_filter = (AdvancedListFilters,) + self.list_filter

    def save_advanced_filter(self, request, form):
        if form.is_valid():
            afilter = form.save(commit=False)
            afilter.created_by = request.user
            afilter.query = form.generate_query()
            afilter.save()
            afilter.users.add(request.user)
            messages.add_message(
                request, messages.SUCCESS,
                _('Advanced filter added successfully.')
            )
            if '_save_goto' in request.REQUEST:
                url = "{path}{qparams}".format(
                    path=request.path, qparams="?_afilter={id}".format(
                        id=afilter.id))
                return HttpResponseRedirect(url)
        elif request.method == "POST":
            logger.info('Failed saving advanced filter, params: %s', form.data)

    def adv_filters_handle(self, request, extra_context={}):
        data = request.POST if request.GET.get(
            'action') == 'advanced_filters' else None
        adv_filters_form = self.advanced_filter_form(
            data=data, model_admin=self, extra_form=True)
        extra_context.update({
            'advanced_filters': adv_filters_form,
            'current_afilter': request.GET.get('_afilter'),
            'app_label': self.opts.app_label,
        })
        return self.save_advanced_filter(request, adv_filters_form)

    def changelist_view(self, request, extra_context=None):
        """Add advanced_filters form to changelist context"""
        if extra_context is None:
            extra_context = {}
        response = self.adv_filters_handle(request,
                                           extra_context=extra_context)
        if response:
            return response
        return super(AdminAdvancedFiltersMixin, self
                     ).changelist_view(request, extra_context=extra_context)


class AdvancedFilterAdmin(admin.ModelAdmin):
    model = AdvancedFilter
    form = AdvancedFilterForm
    extra = 0

    list_display = ('title', 'created_by', )
    readonly_fields = ('created_by', 'model', )

    def has_add_permission(self, obj=None):
        return False

    def save_model(self, request, new_object, *args, **kwargs):
        if new_object and not new_object.pk:
            new_object.created_by = request.user

        super(AdvancedFilterAdmin, self).save_model(
            request, new_object, *args, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        orig_response = super(AdvancedFilterAdmin, self).change_view(
            request, object_id, form_url, extra_context)
        if '_save_goto' in request.POST:
            obj = self.get_object(request, unquote(object_id))
            if obj:
                app, model = obj.model.split('.')
                path = resolve_url('admin:%s_%s_changelist' % (
                    app, model.lower()))
                url = "{path}{qparams}".format(
                    path=path, qparams="?_afilter={id}".format(id=object_id))
                return HttpResponseRedirect(url)
        return orig_response


admin.site.register(AdvancedFilter, AdvancedFilterAdmin)
