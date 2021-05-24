import logging

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

from .forms import AdvancedFilterForm, AdvancedFilterQueryForm
from .models import AdvancedFilter
from .q_serializer import QSerializer

# django < 1.9 support
from django import VERSION
if VERSION >= (2, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _


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
            filters = AdvancedFilter.objects.filter(id=self.value())
            if hasattr(filters, 'first'):
                advfilter = filters.first()
            if not advfilter:
                logger.error("AdvancedListFilters.queryset: Invalid filter id")
                return queryset
            query = advfilter.query
            logger.debug(query.__dict__)
            return queryset.filter(query).distinct()
        return queryset


class AdvancedQueryFilters(admin.SimpleListFilter):
    """Allow filtering by advanced filters query"""
    title = ' '
    template = 'admin/query_filter.html'

    parameter_name = '_aquery'

    def lookups(self, request, model_admin):
        return None

    def queryset(self, request, queryset):
        if self.value():
            query_serializer = QSerializer(base64=True)
            query = query_serializer.loads(self.value())
            return queryset.filter(query).distinct()

        return queryset

    def choices(self, changelist):
        return []

    def has_output(self):
        return True


class AdminAdvancedFiltersMixin(object):
    """ Generic AdvancedFilters mixin """
    advanced_change_list_template = "admin/advanced_filters.html"
    advanced_filter_form = AdvancedFilterForm

    def __init__(self, *args, **kwargs):
        super(AdminAdvancedFiltersMixin, self).__init__(*args, **kwargs)
        if self.change_list_template:
            self.original_change_list_template = self.change_list_template
        else:
            self.original_change_list_template = "admin/change_list.html"
        self.change_list_template = self.advanced_change_list_template
        # add list filters to filters
        self.list_filter = (AdvancedListFilters, AdvancedQueryFilters,) + tuple(self.list_filter)

    def save_advanced_filter(self, request, form, save_instance):
        if '_just_filter' in request.POST:
            search_query = form.generate_query()
            query_serializer = QSerializer(base64=True)
            b64_query = query_serializer.dumps(search_query)
            url = "{path}?_aquery={query}"\
                .format(path=request.path, query=b64_query)
            return HttpResponseRedirect(url)
        if form.is_valid():
            afilter = form.save(commit=False)
            afilter.created_by = request.user
            afilter.query = form.generate_query()

            if save_instance:
                afilter.save()
                afilter.users.add(request.user)
            messages.add_message(
                request, messages.SUCCESS,
                _('Advanced filter added successfully.')
            )
            if '_save_goto' in (request.GET or request.POST):
                url = "{path}{qparams}".format(
                    path=request.path, qparams="?_afilter={id}".format(
                        id=afilter.id))
                return HttpResponseRedirect(url)
        elif request.method == "POST":
            logger.info('Failed saving advanced filter, params: %s', form.data)

    def get_advanced_filter_data(self, request):
        if request.POST.get('action') == 'advanced_filters':
            return request.POST, True

        search_query = request.GET.get('_aquery')
        if search_query:
            query_serializer = QSerializer(base64=True)
            raw_query = query_serializer.loads(search_query, raw=True)
            query_list = query_serializer.get_field_values_list(raw_query)

            data = {
                'form-TOTAL_FORMS': 0,
                'form-INITIAL_FORMS': 0,
                'title': 'unsaved filter'
            }

            for idx, query in enumerate(query_list):
                query_dict = AdvancedFilterQueryForm._parse_query_dict(query, self.model)

                for key, value in query_dict.items():
                    data['form-{idx}-{key}'.format(idx=idx, key=key)] = value

                data['form-TOTAL_FORMS'] += 1

            return data, False

        return None, False

    def adv_filters_handle(self, request, extra_context={}):
        data, save_instance = self.get_advanced_filter_data(request)
        adv_filters_form = self.advanced_filter_form(
            data=data, model_admin=self, extra_form=True)
        extra_context.update({
            'original_change_list_template': self.original_change_list_template,
            'advanced_filters': adv_filters_form,
            'current_afilter': request.GET.get('_afilter'),
            'app_label': self.opts.app_label,
        })
        return self.save_advanced_filter(request, adv_filters_form, save_instance)

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

    list_display = ('title', 'model', 'created_by', )
    readonly_fields = ('created_by', 'model', 'created_at', )
    list_filter = ('model', )

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

    @staticmethod
    def user_has_permission(user):
        """Filters by user if not superuser or explicitly allowed in settings"""
        return user.is_superuser or not getattr(settings, "ADVANCED_FILTER_EDIT_BY_USER", True)

    def get_queryset(self, request):
        if self.user_has_permission(request.user):
            return super(AdvancedFilterAdmin, self).get_queryset(request)
        else:
            return self.model.objects.filter_by_user(request.user)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return super(AdvancedFilterAdmin, self).has_change_permission(request)
        return self.user_has_permission(request.user) or obj in self.model.objects.filter_by_user(request.user)

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return super(AdvancedFilterAdmin, self).has_delete_permission(request)
        return self.user_has_permission(request.user) or obj in self.model.objects.filter_by_user(request.user)


admin.site.register(AdvancedFilter, AdvancedFilterAdmin)
