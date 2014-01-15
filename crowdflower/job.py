# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


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
        self._changes = {}

    def __setattr__(self, key, value):
        if key in self._RO_ATTRS:
            raise AttributeError(
                "cannot change read only attribute '{}'".format(key))

        elif key in self._RW_ATTRS:
            self._changes[key] = value

        else:
            super(Job, self).__setattr__(key, value)

    def __getattr__(self, item):
        if item in self._RO_ATTRS:
            return self._json[item]

        elif item in self._RW_ATTRS:
            return self._changes.get(item, self._json[item])

        raise AttributeError("'{}' object has no attribute '{}'".format(
            self.__class__.__name__,
            item
        ))

    def update(self):
        """
        Send updates to CrowdFlower. Note that both 'instructions' and 'cml'
        attributes must be set or provided and valid for any changes to really
        persist.

        The API will happily return a "valid" response when sent only the
        'instructions', but nothing will change on the server side without
        both. The caller is responsible for providing valid CML.
        """
        cml = self._changes.get('cml', self._json['cml'])
        instructions = self._changes.get('instructions',
                                         self._json['instructions'])

        # CrowdFlower API will happily return a "valid" response, if
        # job[instructions] POST data is provided, but will not persist any
        # changes, if both cml and instructions are not provided and valid,
        # or already set on the job.
        if not (cml and instructions):
            raise RuntimeError("'instructions' and 'cml' required")

        self._json.update(self._client.update_job(self.id, self._changes))
        self._changes = {}

    def upload(self, data):
        """
        Upload given data as JSON.

        @param data: Iterable of JSON serializable objects
        @type data: collections.abc.Iterable
        """
        self._client.upload_job(data, self.id)

    def upload_file(self, file, type_=None):
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

        @param file: A file like object or a filename string, contains UTF-8
                     encoded data
        @type file: str or file
        @param type_: Explicit type, required for file like objects
        @type type_: str
        """
        self._client.upload_job_file(file, type_, self.id)

    def delete(self):
        """
        Delete this job, removing it from CrowdFlower. Calling Job instance
        will be invalid after deletion and must not be used anymore.
        """
        self._client.delete_job(self.id)
        self._json = None
        self._changes = None
