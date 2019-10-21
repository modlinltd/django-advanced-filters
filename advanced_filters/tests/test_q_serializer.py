from django.db.models import Q
from django.test import TestCase
import json

from ..q_serializer import QSerializer


class QSerializerTest(TestCase):
    correct_query = {
        'children': [('test', 1234)],
        'connector': u'AND',
        'negated': False,
    }

    def setUp(self):
        self.s = QSerializer()
        self.query_a = Q(test=1234)
        self.query_b = Q(another="test")

    def test_serialize_q(self):
        res = self.s.serialize(self.query_a)
        self.assertEqual(res, self.correct_query)

    def test_jsondump_q(self):
        jres = self.s.dumps(self.query_a)
        self.assertJSONEqual(jres, json.dumps(self.correct_query))

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
