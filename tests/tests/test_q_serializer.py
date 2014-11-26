from django.db.models import Q
from django.test import TestCase

from advanced_filters.q_serializer import QSerializer


class QSerializerTest(TestCase):

    def setUp(self):
        self.s = QSerializer()
        self.query_a = Q(test=1234)
        self.query_b = Q(another="test")

    def test_serialize_q(self):
        res = self.s.serialize(self.query_a)
        self.assertEquals(
            res, {
                'children': [('test', 1234)],
                'connector': u'AND',
                'negated': False,
            }
        )

        jres = self.s.dumps(self.query_a)
        self.assertEquals(
            jres,
            '{"connector": "AND", "negated": false, "children": [["test", '
            '1234]]}'
        )

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
