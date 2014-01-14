# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import contextlib
from crowdflower.crowdflower.job import Job
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

    def _call(self, path, data=None, headers=None, query={}, method=None):
        """
        @param data: Byte data for POST
        @type data: bytes
        @param headers: Additional headers
        @type headers: dict
        @param query: Additional query parameters
        @type query: dict
        @param method: GET, POST, PUT or DELETE
        @type method: str
        """
        # Send UTF-8 bytes only
        if data and not isinstance(data, bytes):
            data = data.encode('utf-8')

        if method is None:
            if data:
                method = 'post'

            else:
                method = 'get'

        method = method.lower()

        if method not in {'get', 'post', 'put', 'delete'}:
            raise ValueError("unknown method '{}'".format(method))

        # This does not mutate the default argument empty dictionary
        query = dict(key=self._key, **query)
        resp = getattr(requests, method)(
            self.API_URL.format(path=path),
            params=query,
            data=data,
            headers=headers,
            method=method)
        resp.raise_for_status()
        return resp.json()

    def update_job(self, job_id, data):
        """
        Update Job <job_id> with ``data``

        @param job_id: Id of crowdflower job to update
        @param data: JSON dictionary of attributes to update
        """

    def _upload_job(self, data, type_):
        headers = {'Content-Type': type_}
        return Job(self, self._call('jobs/upload.json', data, headers))

    def upload_job(self, data):
        """
        Upload given data as JSON.

        @param data: list of JSON serializable objects
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
        guess from. File data must be bytes, not text (unicode).

        If explicit ``type_`` is not provided and the ``file`` is a string
        containing a filename to open, will make a guess with mimetypes.
        Returns a new Job instance related to the uploaded data.

        If type information is not given and guessing did not work,
        will raise a ValueError.

        @param client: crowdflower.client.Client instance used for uploading
        @type client: crowdflower.client.Client
        @param file: A file like object or a filename string, contains UTF-8
                     encoded data
        @param type_: Explicit type, required for file like objects
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
            # It sucks to read the whole thing to memory here, but Request
            # data accepts strings/bytes only
            return self._upload_job(fp.read(), type_)
