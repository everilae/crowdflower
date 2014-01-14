# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'

# Example data:
#
# {'alias': None,
#  'auto_order': False,
#  'auto_order_threshold': None,
#  'auto_order_timeout': None,
#  'cml': None,
#  'completed': False,
#  'completed_at': None,
#  'confidence_fields': None,
#  'created_at': '2014-01-14T11:58:10+00:00',
#  'css': None,
#  'custom_key': None,
#  'design_verified': False,
#  'desired_requirements': None,
#  'excluded_countries': [],
#  'execution_mode': 'worker_ui_remix',
#  'expected_judgments_per_unit': None,
#  'fields': None,
#  'gold': {},
#  'gold_per_assignment': 0,
#  'golds_count': 0,
#  'id': 372685,
#  'included_countries': [],
#  'instructions': '',
#  'js': None,
#  'judgments_count': 0,
#  'judgments_per_unit': 3,
#  'language': 'en',
#  'max_judgments_per_ip': None,
#  'max_judgments_per_unit': None,
#  'max_judgments_per_worker': None,
#  'max_unit_confidence': None,
#  'min_unit_confidence': None,
#  'minimum_account_age_seconds': None,
#  'minimum_requirements': {'min_score': 1,
#   'priority': 1,
#   'skill_scores': {'level_1_contributors': 1}},
#  'options': {'after_gold': 4,
#   'front_load': False,
#   'ramuh2': True,
#   'ramuh2_url': 'http://ramuh2-001.cloud.doloreslabs.com:8080/ramuh/api/v2',
#   'track_clones': True},
#  'order_approved': True,
#  'pages_per_assignment': 1,
#  'problem': None,
#  'project_number': None,
#  'public_data': False,
#  'require_worker_login': None,
#  'send_judgments_webhook': None,
#  'state': 'unordered',
#  'support_email': 'selfservice_notifications@crowdflower.com',
#  'title': None,
#  'units_count': 0,
#  'units_per_assignment': 5,
#  'units_remain_finalized': None,
#  'updated_at': '2014-01-14T11:58:10+00:00',
#  'variable_judgments_mode': 'none',
#  'webhook_uri': None,
#  'worker_ui_remix': True}


class Job(object):
    """
    CrowdFlower Job.
    """

    _RO_ATTRS = frozenset("""
    completed
    completed_at
    created_at
    gold
    golds_count
    id
    judgments_count
    units_count
    updated_at
    """.strip().split())

    _RW_ATTRS = frozenset("""
    auto_order
    auto_order_threshold
    auto_order_timeout
    cml
    cml_fields
    confidence_fields
    css
    custom_key
    excluded_countries
    gold_per_assignment
    included_countries
    instructions
    js
    judgments_per_unit
    language
    max_judgments_per_unit
    max_judgments_per_contributor
    min_unit_confidence
    options
    pages_per_assignment
    problem
    send_judgments_webhook
    state
    title
    units_per_assignment
    webhook_uri
    """.strip().split())

    def __init__(self, client, data):
        """
        Initialize from given (possibly empty) JSON dictionary.
        @param client: Client instance that created this job instance
        @type client: crowdflower.client.Client
        @param data: Job JSON dictionary
        @type data: dict
        """
        self._client = client
        self._json = data

    def __setattr__(self, key, value):
        if key in self._RW_ATTRS:
            self._json[key] = value
            self._client.update_job()

    def __getattr__(self, item):
        if item in self._RO_ATTRS or item in self._RW_ATTRS:
            return self._json[item]

        raise AttributeError("'{}' object has no attribute '{}'".format(
            self.__class__.__name__,
            item
        ))
