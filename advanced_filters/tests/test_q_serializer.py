from django.db.models import Q
from django.test import TestCase
import json
import datetime


from ..q_serializer import QSerializer


class QSerializerTest(TestCase):
    correct_query = {
        "children": [("test", 1234)],
        "connector": "AND",
        "negated": False,
    }
    datetime_query = {
        "children": [("date", datetime.datetime.now().isoformat())],
        "connector": "AND",
        "negated": False,
    }

    def setUp(self):
        self.s = QSerializer()
        self.query_a = Q(test=1234)
        self.date_query = Q(date=datetime.datetime.now().isoformat())

    def test_serialize_q(self):
        res = self.s.serialize(self.query_a)
        self.assertEqual(res, self.correct_query)

        date = self.s.serialize(self.date_query)
        self.assertEqual(date, self.datetime_query)

    def test_jsondump_q(self):
        jres = self.s.dumps(self.query_a)
        self.assertJSONEqual(jres, json.dumps(self.correct_query))

        jdate = self.s.serialize(self.date_query)
        self.assertEqual(jdate, json.dumps(self.datetime_query))

    def test_deserialize_q(self):
        qres = self.s.deserialize(
            {
                "children": [("test", 1234)],
                "connector": "AND",
                "negated": False,
                "subtree_parents": [],
            }
        )
        self.assertIsInstance(qres, Q)

        qres = self.s.loads(
            '{"connector": "AND", "negated": false, "children"'
            ' :[["test", 1234]], "subtree_parents": []}'
        )
        self.assertIsInstance(qres, Q)

        dres = self.s.deserialize(
            {
                "children": [("date", datetime.datetime.now().isoformat())],
                "connector": "AND",
                "negated": False,
            }
        )
        self.assertIsInstance(dres, Q)

        qres = self.s.loads(
            '{"connector": "AND", "negated": false, "children"'
            ' :[["date", 2024-06-11T13:02:16.568909]], "subtree_parents": []}'
        )
        self.assertIsInstance(qres, Q)
