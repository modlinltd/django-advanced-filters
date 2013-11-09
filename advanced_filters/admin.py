import logging

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from .forms import AdvancedFilterForm
from .models import AdvancedFilter
from .q_serializer import QSerializer


logger = logging.getLogger('advanced_filters')


class AdvancedListFilters(admin.SimpleListFilter):
    """Allow filtering by stored advanced filters (selection by title)"""
    title = _('Advanced filters')

    parameter_name = '_afilter'

    def lookups(self, request, model_admin):
        return AdvancedFilter.objects.filter_by_user(request.user).values_list(
            'id', 'title')

    def queryset(self, request, queryset):
        if self.value():
            try:
                advfilter = AdvancedFilter.objects.get(id=self.value())
            except AdvancedFilter.DoesNotExist:
                advfilter = None
            if not advfilter:
                logger.error("AdvancedListFilters.queryset: Invalid filter id")
                return queryset
            s = QSerializer(base64=True)
            query = s.loads(advfilter.b64_query)
            logger.debug(query.__dict__)
            return queryset.filter(query).distinct()
        return queryset


class AdminAdvancedFiltersMixin(admin.ModelAdmin):
    """ Generic AdvancedFilters mixin """
    change_list_template = "admin/advanced_filters.html"

    def __init__(self, *args, **kwargs):
        super(AdminAdvancedFiltersMixin, self).__init__(*args, **kwargs)
        # add list filters to filters
        self.list_filter = (AdvancedListFilters,) + self.list_filter

    def save_advanced_filter(self, request, form):
        if form.is_valid():
            afilter = form.save(commit=False)
            afilter.created_by = request.user
            s = QSerializer(base64=True)
            afilter.b64_query = s.dumps(form.generate_query())
            afilter.save()
            afilter.users.add(request.user)
            messages.add_message(
                request, messages.SUCCESS,
                _('Advanced filter added succesfully.'))
            if '_save_goto' in request.REQUEST:
                url = "{path}{qparams}".format(
                    path=request.path, qparams="?_afilter={id}".format(
                        id=afilter.id))
                return HttpResponseRedirect(url)
        elif request.method == "POST":
            logger.info('Failed saving advanced filter, params: %s', form.data)

    def adv_filters_handle(self, request, kwargs):
        data = request.POST if request.REQUEST.get(
            'action') == 'advanced_filters' else None
        adv_filters_form = AdvancedFilterForm(data=data,
                                              model_admin=self)
        extra_context = kwargs.get('extra_context', {})
        extra_context.update({'advanced_filters': adv_filters_form})
        kwargs['extra_context'] = extra_context
        return self.save_advanced_filter(request, adv_filters_form)

    def changelist_view(self, request, **kwargs):
        """Add advanced_filters form to changelist context"""
        response = self.adv_filters_handle(request, kwargs)
        if response:
            return response
        return super(AdminAdvancedFiltersMixin, self).changelist_view(
            request, **kwargs)
