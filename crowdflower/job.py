# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Job(Base):
    """
    CrowdFlower Job.

    :param client: Client instance that created this job instance
    :type client: crowdflower.client.Client
    :param data: Job JSON dictionary
    :type data: dict
    """

    #: Read only attributes
    RO_ATTRS = frozenset("""
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

    #: Read/write attributes
    RW_ATTRS = frozenset("""
        auto_order
        auto_order_threshold
        auto_order_timeout
        cml
        fields
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
        self._client = client
        super(Job, self).__init__(data)

    def update(self):
        """
        Send updates made to this instance to CrowdFlower. Note that 'title',
        'instructions' and 'cml' attributes must exist (either in the update or
        in the job already) for any changes to really persist, and so this
        method raises a RuntimeError, if any of them is missing.

        .. warning::

           The API will happily return a "valid" response when sent only the
           'instructions', but nothing will change on the server side without
           all three. The caller is responsible for providing valid CML.

        :raises: RuntimeError
        """
        for attr in {'title', 'instructions', 'cml'}:
            if not self._changes.get(attr, self._json[attr]):
                raise RuntimeError(
                    "missing required attribute '{}'".format(attr))

        super(Job, self)._update(self._client.update_job(
            self.id, self._changes))

    def upload(self, data):
        """
        Upload given data as JSON.

        :param data: Iterable of JSON serializable objects
        :type data: collections.abc.Iterable
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

        :param file: A file like object or a filename string, contains UTF-8
                     encoded data
        :type file: str or file
        :param type_: Explicit type, required for file like objects
        :type type_: str
        """
        self._client.upload_job_file(file, type_, self.id)

    def delete(self):
        """
        Delete this job, removing it from CrowdFlower. Calling Job instance
        will be invalid after deletion and must not be used anymore.
        """
        self._client.delete_job(self.id)

    @property
    def judgments(self):
        """
        List of aggregated judgments for this job.
        """
        return self._client.get_judgmentaggregates(self)

    def get_judgment(self, judgment_id):
        """
        Get single Judgment for this job.
        """
        return self._client.get_judgment(self, judgment_id)
