import unittest
from inspect import getmembers
from crowdflower.job import Job
from crowdflower.base import Attribute, RoAttribute, WoAttribute


data = {'minimum_requirements': None,
        'auto_order': False,
        'state': 'paused',
        'pages_per_assignment': 1,
        'worker_ui_remix': True,
        'judgments_per_unit': 1,
        'max_judgments_per_ip': None,
        'excluded_countries': [],
        'project_number': 'PN1415',
        'golds_count': 5,
        'cml': 'CML',
        'max_judgments_per_worker': None,
        'variable_judgments_mode': 'none',
        'units_count': 148,
        'instructions': 'INSTRUCTIONS',
        'desired_requirements': None,
        'css': '',
        'gold': {'sentiment': 'sentiment_gold'},
        'title': 'TITLE',
        'send_judgments_webhook': None,
        'min_unit_confidence': None,
        'created_at': '2015-06-24T12:44:51+00:00',
        'js': 'JS',
        'design_verified': True,
        'max_work_per_network': None,
        'included_countries': [{'name': 'Finland', 'code': 'FI'}],
        'judgments_count': 35,
        'minimum_account_age_seconds': None,
        'fields': {'sentiment': 'agg', 'relation': 'agg'},
        'confidence_fields': ['sentiment', 'relation'],
        'payment_cents': 25,
        'crowd_costs': 2.01,
        'execution_mode': 'worker_ui_remix',
        'completed': False,
        'auto_order_threshold': 4,
        'updated_at': '2015-06-27T09:06:16+00:00',
        'max_judgments_per_unit': None,
        'units_remain_finalized': False,
        'gold_per_assignment': 1,
        'secret': 'SECRET',
        'webhook_uri': None,
        'support_email': 'support@example.com',
        'units_per_assignment': 5,
        'completed_at': '2015-06-24T13:10:22+00:00',
        'auto_order_timeout': None,
        'require_worker_login': True,
        'alias': None,
        'language': 'en',
        'copied_from': 732585,
        'order_approved': True,
        'expected_judgments_per_unit': None,
        'public_data': False,
        'options': {'req_ttl_in_seconds': 1800,
                    'logical_aggregation': True,
                    'track_clones': True,
                    'mail_to': 'mail@example.com'},
        'id': 746777,
        'quiz_mode_enabled': False}


def _make_job():
    return Job(client=None, **data)


class TestJobAttributes(unittest.TestCase):

    def test_get_attributes(self):
        """
        Attributes provide correct values.
        """
        job = _make_job()
        for k, v in data.items():
            self.assertEqual(getattr(job, k), v)

    def test_rw_attributes(self):
        """
        RW attributes can be set.
        """
        job = _make_job()
        for name, _ in getmembers(
                Job, lambda x: type(x) is Attribute):
            v = object()
            setattr(job, name, v)
            self.assertEqual(getattr(job, name), v)

    def test_ro_attributes(self):
        """
        RO attributes cannot be set.
        """
        job = _make_job()
        for name, _ in getmembers(
                Job, lambda x: type(x) is RoAttribute):
            with self.assertRaises(AttributeError):
                setattr(job, name, "FAIL")

    def test_wo_attributes(self):
        """
        WO attributes cannot be read.
        """
        job = _make_job()
        for name, _ in getmembers(
                Job, lambda x: type(x) is WoAttribute):
            v = object()
            setattr(job, name, v)
            self.assertEqual(job._changes[name], v)
            with self.assertRaises(AttributeError):
                getattr(job, name)
