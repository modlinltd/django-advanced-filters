from django.db.models import Q
from django.test import TestCase
import django

import simplejson as json

from advanced_filters.q_serializer import QSerializer

NEWER_DJANGO = django.VERSION >= (1, 6)


class QSerializerTest(TestCase):
    correct_query = {
        'children': [('test', 1234)],
        'connector': u'AND',
        'negated': False,
    }
    if not NEWER_DJANGO:
        correct_query['subtree_parents'] = []

    correct_query_json = json.dumps(correct_query)

    def setUp(self):
        self.s = QSerializer()
        self.query_a = Q(test=1234)
        self.query_b = Q(another="test")

    def test_serialize_q(self):
        res = self.s.serialize(self.query_a)

        self.assertEquals(res, self.correct_query)

        jres = self.s.dumps(self.query_a)
        self.assertEquals(jres, self.correct_query_json)
        # '{"connector": "AND", "negated": false, "children": [["test", '
        # '1234]], "subtree_parents": []}'
        # )

    def test_deserialize_q(self):
        qres = self.s.deserialize({
            'children': [('test', 1234)],
            'connector': u'AND',
            'negated': False,
            'subtree_parents': []
        })
        self.assertIsInstance(qres, Q)

        qres = self.s.loads('{"connector": "AND", "negated": false, "children"'
                            ' :[["test", 1234]], "subtree_parents": []}')
        self.assertIsInstance(qres, Q)
