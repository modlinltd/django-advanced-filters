from operator import itemgetter
from pprint import pformat
import logging

from django.conf import settings
from django.contrib.admin.util import get_fields_from_path
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.views.generic import View

from braces.views import (CsrfExemptMixin, StaffuserRequiredMixin,
                          JSONResponseMixin)

logger = logging.getLogger('advanced_filters.views')

DISABLE_FOR_FIELDS = getattr(settings, 'ADVANCED_FILTERS_DISABLE_FOR_FIELDS',
                             tuple())
MAX_CHOICES = getattr(settings, 'ADVANCED_FILTERS_MAX_CHOICES', 254)


class GetFieldChoices(CsrfExemptMixin, StaffuserRequiredMixin,
                      JSONResponseMixin, View):
    """
    A JSONResponse view that accepts a model and a field (path to field),
    resolves and returns the valid choices for that field.

    If this field is not a simple Integer/CharField with predefined choices,
    all distinct entries in the DB are presented, unless field name is in
    DISABLE_FOR_FIELDS and limited to a maximum of MAX_CHOICES.
    """
    def get(self, request, model, field_name):
        app_label, model_name = model.split('.', 1)
        model_obj = models.get_model(app_label, model_name)
        if not model_obj:
            return self.render_json_response(
                {'error': 'No model found for %s' % model}, status=400)

        try:
            field = get_fields_from_path(model_obj, field_name)[-1]
            model_obj = field.model  # use new model if followed a ForeignKey
        except FieldDoesNotExist:
            return self.render_json_response(
                {'error': 'No such field %s found in model %s' %
                    (field_name, model)}, status=400)

        choices = field.choices
        # if no choices, populate with distinct values from instances
        if not choices:
            choices = []
            if field.name in DISABLE_FOR_FIELDS:
                logger.debug('Skipped lookup of choices for disabled fields')
            elif isinstance(field, (models.BooleanField, models.DateField,
                                    models.TimeField)):
                logger.debug('No choices calculated for field %s of type %s',
                             field, type(field))
            else:
                choices = set(model_obj.objects.values_list(
                    field.name, flat=True))
                if len(choices) < MAX_CHOICES:
                    choices = zip(choices, choices)
                    logger.debug('Choices found for field %s: %s',
                                 field.name, pformat(choices))
                else:
                    choices = []

        results = [{'id': c[0], 'text': unicode(c[1])} for c in sorted(
                   choices, key=itemgetter(0))]

        return self.render_json_response({'results': results})
