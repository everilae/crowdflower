# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import contextlib
from crowdflower.job import Job
import functools
import json
import mimetypes
import six
import requests

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


@contextlib.contextmanager
def _nopcontext(file):
    yield file


class Client(object):
    """
    CrowdFlower API client.
    """

    API_URL = 'https://api.crowdflower.com/v1/{path}'

    def __init__(self, key):
        """
        @param key: CrowdFlower API key. Required for authentication.
        """
        self._key = key

    def _call(self, path, data=None, headers=None, query={}, method='get'):
        """
        Data may be str (unicode) or bytes. Unicode strings will be
        encoded to UTF-8 bytes.

        @param data: Byte data for POST
        @type data: str, bytes or dict
        @param headers: Additional headers
        @type headers: dict
        @param query: Additional query parameters
        @type query: dict
        @param method: GET, POST, PUT or DELETE
        @type method: str
        """
        if data and isinstance(data, six.text_type):
            data = data.encode('utf-8')

        if method == 'get' and data:
            method = 'post'

        resp = requests.request(
            method=method,
            url=self.API_URL.format(path=path),
            params=dict(key=self._key, **query),
            data=data,
            headers=headers
        )
        resp.raise_for_status()
        resp_json = resp.json()

        if 'error' in resp_json or 'errors' in resp_json:
            raise RuntimeError(resp.text)

        return resp_json

    def _make_cf_attrs(self, type_, attrs):
        return {'{}[{}]'.format(type_, k): v for k, v in attrs.items()}

    def update_job(self, job_id, attrs):
        """
        Update Job <job_id> with ``data``

        @param job_id: Id of crowdflower job to update
        @type job_id: int
        @param attrs: JSON dictionary of attributes to update
        @type attrs: dict
        """
        return self._call(
            path='jobs/{}.json'.format(job_id),
            data=self._make_cf_attrs('job', attrs),
            method='put')

    def get_job(self, job_id):
        """
        Get Job <job_id>

        @param job_id: Id of crowdflower job to get
        @type job_id: int
        @return: Crowdflower job
        @rtype: crowdflower.job.Job
        """
        return Job(self, self._call('jobs/{}.json'.format(job_id)))

    def _upload_job(self, data, type_):
        headers = {'Content-Type': type_}
        return Job(self, self._call('jobs/upload.json', data, headers))

    def upload_job(self, data):
        """
        Upload given data as JSON.

        @param data: Collection of JSON serializable objects
        @return: crowdflower.job.Job instance
        @rtype: crowdflower.job.Job
        """
        return self._upload_job(
            '\n'.join(map(json.dumps, data)).encode('utf-8'),
            'application/json'
        )

    def upload_job_file(self, file, type_=None):
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

        @param client: crowdflower.client.Client instance used for uploading
        @type client: crowdflower.client.Client
        @param file: A file like object or a filename string, contains UTF-8
                     encoded data
        @type file: str or file
        @param type_: Explicit type, required for file like objects
        @type type_: str
        @return: crowdflower.job.Job instance
        @rtype: crowdflower.job.Job
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
            return self._upload_job(fp.read(), type_)
