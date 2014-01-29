# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base, Attribute, RoAttribute
from functools import partial

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


class Job(Base):
    """
    CrowdFlower Job.

    :param data: Job JSON dictionary
    :type data: dict
    :param client: Client instance that created this job instance
    :type client: crowdflower.client.Client
    """

    completed = RoAttribute()
    completed_at = RoAttribute()
    created_at = RoAttribute()
    gold = RoAttribute()
    golds_count = RoAttribute()
    id = RoAttribute()
    judgments_count = RoAttribute()
    units_count = RoAttribute()
    updated_at = RoAttribute()

    auto_order = Attribute()
    auto_order_threshold = Attribute()
    auto_order_timeout = Attribute()
    cml = Attribute()
    fields = Attribute()
    confidence_fields = Attribute()
    css = Attribute()
    custom_key = Attribute()
    excluded_countries = Attribute()
    gold_per_assignment = Attribute()
    included_countries = Attribute()
    instructions = Attribute()
    js = Attribute()
    judgments_per_unit = Attribute()
    language = Attribute()
    max_judgments_per_unit = Attribute()
    max_judgments_per_contributor = Attribute()
    min_unit_confidence = Attribute()
    options = Attribute()
    pages_per_assignment = Attribute()
    problem = Attribute()
    send_judgments_webhook = Attribute()
    state = Attribute()
    title = Attribute()
    units_per_assignment = Attribute()
    webhook_uri = Attribute()

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
            # Does a magic lookup to changes first, then the original json
            if not getattr(self, attr):
                raise RuntimeError(
                    "missing required attribute '{}'".format(attr))

        # calls Base._update, which calls the provided method with a
        # changes dict
        self._update(partial(self._client.update_job, self.id))

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

    def copy(self, all_units=False, gold=False):
        """
        Create a new job that is a copy of this job.

        :param all_units: If true, all of this job's units will be copied to the new job.
        :param gold: If true, only golden units will be copied to the new job.
        :returns: crowdflower.job.Job
        """
        return self._client.copy_job(self.id, all_units, gold)