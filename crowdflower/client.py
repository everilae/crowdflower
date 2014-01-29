# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .unit import Unit

from .job import Job
from .judgment import JudgmentAggregate, Judgment
import contextlib
import functools
import json
import mimetypes
import requests
import requests.exceptions
import six
import logging

_log = logging.getLogger(__name__)
__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


@contextlib.contextmanager
def _nopcontext(file):
    yield file


class ApiError(Exception):
    """
    Base class for API errors.

    :param from_: For python 2 exception chaining.
    """

    def __init__(self, *args, **kwgs):
        #: Python 2 backwards compatible exception chain
        self.from_ = kwgs.pop('from_', None)
        super(ApiError, self).__init__(*args, **kwgs)


class Client(object):
    """
    CrowdFlower API client. Requires API ``key`` for authentication.

    :param key: CrowdFlower API key. Required for authentication.
    """

    API_URL = 'https://api.crowdflower.com/v1/{path}'

    def __init__(self, key):
        self._key = key

    def _call(self, path,
              data=None,
              headers=None,
              query={},
              method='get',
              files=None):
        """
        Data may be str (unicode) or bytes. Unicode strings will be
        encoded to UTF-8 bytes.

        :param data: Byte data for POST
        :type data: str, bytes or dict
        :param headers: Additional headers
        :type headers: dict
        :param query: Additional query parameters
        :type query: dict
        :param method: GET, POST, PUT or DELETE
        :type method: str
        :param files: Files to upload
        :type files: dict
        :returns: JSON dictionary
        :rtype: dict
        """
        if data and isinstance(data, six.text_type):
            data = data.encode('utf-8')

        if method == 'get' and (data or files):
            method = 'post'

        try:
            resp = requests.request(
                method=method,
                url=self.API_URL.format(path=path),
                params=dict(key=self._key, **query),
                data=data,
                headers=headers,
                files=files
            )
            # Raise an exception, if server responded with 50x or so
            resp.raise_for_status()

        except requests.exceptions.RequestException as re:
            msg = "API request failed: {}"

            if six.PY3:
                raise ApiError(msg.format(re)) from re

            else:
                raise ApiError(msg.format(re), from_=re)

        resp_json = resp.json()

        if 'error' in resp_json:
            raise ApiError(resp_json['error'])

        elif 'errors' in resp_json:
            raise ApiError(*resp_json['errors'])

        return resp_json

    def _recursive_items(self, dict_, path=()):
        """
        Recursive generator for producing a flat list from nested dictionaries.
        Generates potentially lot of tuples for paths, but fix if it turns out
        broken.

        Don't provide too deeply nested dicts, as you will hit the python
        recursion level limit.
        """
        for k, v in dict_.items():
            if isinstance(v, dict):
                # If this was python3.3 only, could use yield from :(.
                # Path is provided in subkey, no need to concatenate.
                for sk, sv in self._recursive_items(v, path + (k,)):
                    yield sk, sv

            else:
                yield path + (k,), v

    def _make_cf_attrs(self, type_, attrs):
        """
        .. code-block:: python

           >>> client = Client('fakekey')
           >>> client._make_cf_attrs('job', {'a': 'foo', 'options': {'b': 1, 'c': 2}})
           {'job[a]': 'foo', 'job[options][b]': 1, 'job[options][c]': 2}
        """
        fmt = '{}[{{}}]'.format(type_)
        return {fmt.format(']['.join(p)): v for p, v in
                self._recursive_items(attrs)}

    def create_job(self, attrs):
        """
        Create new job with ``attrs``, where attributes of most interest are:

        - title
        - instructions
        - cml
        - js
        - css

        Other R/W attributes:

        - auto_order
        - auto_order_threshold
        - auto_order_timeout
        - fields
        - confidence_fields
        - custom_key
        - excluded_countries
        - gold_per_assignment
        - included_countries
        - judgments_per_unit
        - language
        - max_judgments_per_unit
        - max_judgments_per_contributor
        - min_unit_confidence
        - options
        - pages_per_assignment
        - problem
        - send_judgments_webhook
        - state
        - units_per_assignment
        - webhook_uri

        :param attrs: JSON dictionary of attributes for new job
        :type attrs: dict
        :returns: Newly created Job
        :rtype: crowdflower.job.Job
        """
        return Job(self._call('jobs.json', self._make_cf_attrs('job', attrs)),
                   client=self)

    def update_job(self, job_id, attrs):
        """
        Update Job ``job_id`` with ``attrs``

        :param job_id: Id of crowdflower job to update
        :type job_id: int
        :param attrs: JSON dictionary of attributes to update
        :type attrs: dict
        """
        return self._call(
            path='jobs/{}.json'.format(job_id),
            data=self._make_cf_attrs('job', attrs),
            method='put')

    def get_job(self, job_id):
        """
        Get Job ``job_id``

        :param job_id: Id of crowdflower job to get
        :type job_id: int
        :returns: Crowdflower job
        :rtype: crowdflower.job.Job
        """
        return Job(self._call('jobs/{}.json'.format(job_id)), client=self)

    def _upload_job(self, data, type_, job_id):
        headers = {'Content-Type': type_}

        if job_id is not None:
            path = 'jobs/{}/upload.json'.format(job_id)

        else:
            path = 'jobs/upload.json'

        return Job(self._call(path, data=data, headers=headers), client=self)

    def upload_job(self, data, job_id=None):
        """
        Upload given data as JSON.

        :param data: Iterable of JSON serializable objects
        :type data: collections.abc.Iterable
        :param job_id: Id of a crowdflower job to update (optional)
        :type job_id: int
        :returns: crowdflower.job.Job instance
        :rtype: crowdflower.job.Job
        """
        return self._upload_job(
            '\n'.join(map(json.dumps, data)).encode('utf-8'),
            'application/json',
            job_id
        )

    def upload_job_file(self, file, type_=None, job_id=None):
        """
        Upload a file like object or open a file for reading and upload.

        Caller is responsible for handling context on file like objects.
        Type must be provided with data as there is no information to make a
        guess from. If file like object provides text (unicode) data, it
        will be encoded to UTF-8 bytes.

        If explicit ``type_`` is not provided and the ``file`` is a string
        containing a filename to open, will make a guess with mimetypes.
        Returns a new Job instance related to the uploaded data.

        If type information is not given and guessing did not work,
        will raise a ValueError.

        :param file: A file like object or a filename string, contains UTF-8
                     encoded data
        :type file: str or file
        :param type_: Explicit type, required for file like objects
        :type type_: str
        :param job_id: Id of a crowdflower job to update (optional)
        :type job_id: int
        :returns: crowdflower.job.Job instance
        :rtype: crowdflower.job.Job
        """
        # Default to expecting a file like object, which caller must handle
        context = _nopcontext

        # Be lenient about filename type for python2
        if isinstance(file, six.string_types):
            # Read as bytes, send as bytes.
            context = functools.partial(open, mode='rb')

            if type_ is None:
                type_, encoding = mimetypes.guess_type(file)

        if type_ is None:
            raise ValueError("Type not set or could not guess type")

        with context(file) as fp:
            return self._upload_job(fp.read(), type_, job_id)

    def delete_job(self, job_id):
        """
        Delete job ``job_id`` from CrowdFlower.
        """
        self._call('jobs/{}.json'.format(job_id), method='delete')

    def get_judgmentaggregates(self, job):
        """
        Get JudgmentAggregates for ``job``.

        .. note::

           Return value from judgments.json seems to be a dictionary,
           where the keys are Unit ids and values an aggregate of a sort. The
           aggregate lacks documentation at https://crowdflower.com/docs-api ,
           so this code is very very likely to break in the future.
        """
        return list(
            map(functools.partial(JudgmentAggregate, job, client=self),
                self._call('jobs/{}/judgments.json'.format(job.id)).values())
        )

    def get_judgment(self, job, judgment_id):
        """
        Get Judgment ``judgment_id`` for ``job``.
        """
        return Judgment(
            job,
            self._call('jobs/{}/judgments/{}.json'.format(job.id,
                                                          judgment_id)),
            client=self
        )

    def get_units(self, job):
        """
        Get Units for ``job``.
        """
        return list(
            map(functools.partial(Unit, job, client=self),
                self._call('jobs/{}/units.json'.format(job.id)))
        )

    def unit_from_json(self, data):
        """
        Create a new Unit instance from JSON ``data``.
        """
        return Unit(Job({'id': data['job_id']}, client=self), data,
                    client=self)

    def copy_job(self, job_id, all_units, gold):
        """
        Copy Job ``job_id`` to a new job.

        :param all_units: If true, all of this job's units will be copied to the new job.
        :param gold: If true, only golden units will be copied to the new job.
        :returns: crowdflower.job.Job
        """
        return Job(self._call('jobs/{}/copy.json'.format(job_id),
                              dict(all_units=all_units, gold=gold)),
                   client=self)

    def get_job_channels(self, job_id):
        """
        Get available and enabled channels for ``job_id``.

        .. code-block:: python

            # A response JSON dictionary
            {
                "enabled_channels": [
                    "amt"
                ],
                "available_channels": [
                    "amt",
                    "sama",
                    "gambit",
                    "mob",
                    "iphone"
                ]
            }

        """
        return self._call('jobs/{}/channels.json'.format(job_id))

    def set_job_channels(self, job_id, channels):
        """
        Enable ``channels`` for ``job_id``.

        :param job_id: Id of job to set channels for
        :param channels: a list of channels to enable
        """
        # requests <3 <3 <3, handles multi value POST body like a charm
        return self._call('jobs/{}/channels.json'.format(job_id),
                          data={'channels[]': channels},
                          method='put')
