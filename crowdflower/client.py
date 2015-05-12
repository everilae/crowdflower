# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from itertools import chain, count
from zipfile import ZipFile
from .order import Order
from .unit import Unit, UnitPromise
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
    """


class PathFactory:
    """
    Magic attribute/item syntax for making calls.
    """
    def __init__(self, client, name=()):
        """
        :type client: Client
        :type name: tuple
        """
        self._client = client
        self._name = name

    def __getattr__(self, name):
        return self.__class__(self._client, self._name + (name,))

    def __getitem__(self, name):
        return self.__class__(self._client, self._name + (str(name),))

    SUFFIX = '.json'

    def _path(self, suffix):
        return '/'.join(self._name) + (suffix if suffix else '')

    def __call__(self, *args, **kwgs):
        _suffix = kwgs.pop('_suffix', self.SUFFIX)
        return self._client.call(
            self._path(_suffix),
            *args,
            **kwgs
        )

    def pages(self, *args, **kwgs):
        _suffix = kwgs.pop('_suffix', self.SUFFIX)
        return self._client.paged_call(
            self._path(_suffix),
            *args,
            **kwgs
        )


class Client(object):
    """
    CrowdFlower API client. Requires API ``key`` for authentication.

    TODO: Trust data model types in order to provide general methods instead
    of specialized do_this and do_that methods.

    :param key: CrowdFlower API key. Required for authentication.
    """

    API_URL = 'https://api.crowdflower.com/v1/{path}'

    def __init__(self, key):
        self._key = key
        self.jobs = PathFactory(self, ('jobs',))

    def call(self, path,
             data=None,
             headers={},
             query={},
             method='get',
             files=None,
             as_json=True):
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
        :param as_json: Handle response as json, defaults to True
        :type as_json: bool
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
                headers=dict(accept='application/json', **headers),
                files=files
            )

        except Exception as e:
            raise ApiError("Api request failed: {}".format(e))

        try:
            # Raise an exception, if server responded with 50x or so
            resp.raise_for_status()

        except requests.exceptions.RequestException as re:
            raise ApiError("API request failed: {} (resp.content={})".format(
                re, resp.content))

        if not as_json:
            # Caller knows what to do, hopefully
            return resp

        try:
            resp_json = resp.json()

        except Exception:
            _log.exception(
                "CrowdFlower API request failed: response %r, data %r",
                resp.content, data
            )
            raise

        if 'error' in resp_json:
            raise ApiError(resp_json['error'])

        elif 'errors' in resp_json:
            raise ApiError(*resp_json['errors'])

        return resp_json

    def paged_call(self, *args, **kwgs):
        """
        Generate paged calls to API end points, wraps :meth:`_call`. Provide
        ``sentinel`` in order to stop paging at desired point. If ``sentinel``
        is a function, it should accept latest ``response`` as argument.

        This can not yield items from response, since some responses are
        dictionaries, while others are lists.

        :keyword page: Page to start at, defaults to 1.
        :keyword limit: Limit pages to ``limit`` items, defaults to 100.
        :keyword sentinel: Sentinel value for ``iter()``.
        """
        page = kwgs.pop('page', 1)
        limit = kwgs.pop('limit', 100)
        sentinel = kwgs.pop('sentinel', None)
        query = kwgs.pop('query', {})
        page = count(page)

        for response in iter(
            lambda: self.call(
                *args,
                query=dict(query, page=next(page), limit=limit),
                **kwgs
            ),
            sentinel
        ):
            yield response

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
        return Job(
            client=self,
            **self.jobs(data=self._make_cf_attrs('job', attrs),
                        method='post')
        )

    def update_job(self, job_id, attrs):
        """
        Update Job ``job_id`` with ``attrs``

        :param job_id: Id of crowdflower job to update
        :type job_id: int
        :param attrs: JSON dictionary of attributes to update
        :type attrs: dict
        """
        return self.jobs[job_id](self._make_cf_attrs('job', attrs),
                                 method='put')

    def get_job(self, job_id):
        """
        Get Job ``job_id``

        :param job_id: Id of crowdflower job to get
        :type job_id: int
        :returns: Crowdflower job
        :rtype: crowdflower.job.Job
        """
        return Job(client=self, **self.jobs[job_id]())

    def get_jobs(self):
        """
        Get Jobs connected to this client and key.

        :returns: an iterator of CrowdFlower jobs
        :rtype: iter of crowdflower.job.Job
        """
        for resp in self.jobs.pages(sentinel=[]):
            for data in resp:
                yield Job(client=self, **data)

    def _upload_job(self, data, type_, job_id, force=False):
        headers = {'Content-Type': type_}
        path = self.jobs

        if job_id is not None:
            path = path[job_id]

        path = path.upload

        return Job(
            client=self,
            **path(data=data, headers=headers, method='post',
                   query=dict(force='true') if force else {})
        )

    def upload_job(self, data, job_id=None, force=False):
        """
        Upload given data as JSON.

        :param data: Iterable of JSON serializable objects
        :type data: collections.abc.Iterable
        :param job_id: Id of a crowdflower job to update (optional)
        :type job_id: int
        :param force: If True force adding units even if the columns do not
                      match existing data
        :type force: bool
        :returns: crowdflower.job.Job instance
        :rtype: crowdflower.job.Job
        """
        return self._upload_job(
            '\n'.join(map(json.dumps, data)).encode('utf-8'),
            'application/json',
            job_id,
            force=force
        )

    def upload_job_file(self, file, type_=None, job_id=None, force=False):
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
        :param force: If True force adding units even if the columns do not
                      match existing data
        :type force: bool
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
            return self._upload_job(fp.read(), type_, job_id, force=force)

    def delete_job(self, job_id):
        """
        Delete job ``job_id`` from CrowdFlower.
        """
        self.jobs[job_id](method='delete')

    def get_judgmentaggregates(self, job):
        """
        Get JudgmentAggregates for ``job``.

        .. note::

           Return value from judgments.json seems to be a dictionary,
           where the keys are Unit ids and values an aggregate of a sort. The
           aggregate lacks documentation at https://crowdflower.com/docs-api ,
           so this code is very very likely to break in the future.
        """
        for resp in self.jobs[job.id].judgments.pages(sentinel={}):
            for data in resp.values():
                yield JudgmentAggregate(job, client=self, **data)

    def get_judgment(self, job, judgment_id):
        """
        Get Judgment ``judgment_id`` for ``job``.
        """
        return Judgment(
            job,
            client=self,
            **self.jobs[job.id].judgments[judgment_id]()
        )

    def get_unit(self, job, unit_id):
        """
        Get :class:`~.unit.Unit` ``unit_id`` for :class:`~.job.Job`.
        """
        return Unit(
            job, client=self,
            **self.jobs[job.id].units[unit_id]()
        )

    def get_units(self, job):
        """
        Get :class:`unit promises <crowdflower.unit.UnitPromise>`
        for :class:`~.job.Job`.
        """
        for resp in self.jobs[job.id].units.pages(sentinel={}):
            for unit_id, data in resp.items():
                yield UnitPromise(job, client=self, id=unit_id, data=data)

    def unit_from_json(self, data):
        """
        Create a new Unit instance from JSON ``data``.
        """
        return Unit(
            Job(id=data['job_id'], client=self),
            client=self,
            **data
        )

    def copy_job(self, job_id, all_units, gold):
        """
        Copy Job ``job_id`` to a new job.

        :param all_units: If true, all of this job's units will be copied to the new job.
        :param gold: If true, only golden units will be copied to the new job.
        :returns: crowdflower.job.Job
        """
        return Job(
            client=self,
            **self.jobs[job_id].copy(
                query=dict(all_units=all_units, gold=gold),
                method='post'
            )
        )

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
        # So... suddenly the API throws 404, if we add the '.json' at the
        # end. Nice.
        return self.jobs[job_id].channels(_suffix=None)

    def set_job_channels(self, job_id, channels):
        """
        Enable ``channels`` for ``job_id``.

        :param job_id: Id of job to set channels for
        :param channels: a list of channels to enable
        """
        # requests <3 <3 <3, handles multi value POST body like a charm
        return self.jobs[job_id].channels(
            _suffix=None, data={'channels[]': channels}, method='put')

    def debit_order(self, job, units_count, channels):
        """
        Create a debit :py:class:`order <crowdflower.order.Order>` for
        :py:class:`Job <crowdflower.job.Job>` with ``units_count``
        at ``channels``.
        """
        return self.jobs[job.id].orders(
            data={
                'channels[]': channels,
                'debit[units_count]': units_count
            }
        )

    def get_order(self, job, order_id):
        """
        Get :py:class:`Order <crowdflower.order.Order>` by ``order_id`` for
        :py:class:`Job <crowdflower.job.Job>` ``job``.
        """
        return Order(
            job, client=self,
            **self.jobs[job.id].orders[order_id]()
        )

    def get_report(self, job, type_='json'):
        """
        Download and uncompress reports.
        """
        resp = self.jobs[job.id](
            _suffix='.csv',
            as_json=False,
            query=dict(type=type_),
        )
        # The response content is a ZipFile (at least it should be)
        with ZipFile(six.io.BytesIO(resp.content)) as zf:
            return [
                Unit(job, client=self, **u)
                for u in map(json.loads, chain.from_iterable(
                    map(
                        lambda bs: (
                            line for line in bs.decode('utf-8').split('\n')
                            if line
                        ),
                        map(zf.read, zf.namelist())
                    )
                ))
            ]
