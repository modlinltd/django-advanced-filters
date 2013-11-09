"""This is a module to serializers/deserializes Django Q (query) object."""
import base64
import logging
from time import mktime
from datetime import datetime, date

from django.db.models import Q
from django.core.serializers.base import SerializationError

try:
    import simplejson as json
except ImportError:
    import json


dt2ts = lambda obj: mktime(obj.timetuple()) if isinstance(obj, date) else obj

logger = logging.getLogger('advanced_filters')


class QSerializer(object):
    """
    A Q object serializer base class. Pass base64=True when initalizing
    to base64 encode/decode the returned/passed string.

    By default the class provides loads/dumps methods that wrap around
    json serialization, but they may be easily overwritten to serialize
    into other formats (i.e xml, yaml, etc...)
    """
    b64_enabled = False

    def __init__(self, base64=False):
        if base64:
            self.b64_enabled = True

    def prepare_value(self, qtuple):
        if qtuple[0].endswith("__range") and len(qtuple[1]) == 2:
            qtuple[1] = (datetime.fromtimestamp(qtuple[1][0]),
                         datetime.fromtimestamp(qtuple[1][1]))
        return qtuple

    def serialize(self, q):
        """
        Serialize a Q object.
        """
        children = []
        for child in q.children:
            if isinstance(child, Q):
                children.append(self.serialize(child))
            else:
                children.append(child)
        serialized = q.__dict__
        serialized['children'] = children
        return serialized

    def deserialize(self, d):
        """
        Serialize a Q object.
        """
        children = []
        for child in d.pop('children'):
            if isinstance(child, dict):
                children.append(self.deserialize(child))
            else:
                children.append(self.prepare_value(child))
        query = Q()
        query.children = children
        query.connector = d['connector']
        query.negated = d['negated']
        query.subtree_parents = d['subtree_parents']
        return query

    def dumps(self, obj):
        if not isinstance(obj, Q):
            raise SerializationError
        string = json.dumps(self.serialize(obj), default=dt2ts)
        if self.b64_enabled:
            return base64.b64encode(string)
        return string

    def loads(self, string):
        if self.b64_enabled:
            d = json.loads(base64.b64decode(string))
        else:
            d = json.loads(string)
        return self.deserialize(d)
