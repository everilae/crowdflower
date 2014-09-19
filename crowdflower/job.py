# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
from .base import Base, Attribute, RoAttribute
from .worker import Worker
from functools import wraps

__author__ = u'Ilja Everilä <ilja.everila@liilak.com>'


def _command(f):
    """
    Helper function for creating repetitive :class:`Job` commands.
    """
    @wraps(f)
    def cmd(self):
        return self._client.send_job_command(self.id, f.__name__)

    return cmd


class Job(Base):
    """
    CrowdFlower Job.

    Documentation for attributes can be found at
    http://success.crowdflower.com/customer/portal/articles/1580923-jobs-resource-attributes .

    :param data: Job JSON dictionary
    :type data: dict
    :param client: :class:`~.client.Client` instance that created this job instance
    :type client: crowdflower.client.Client
    """

    # RO attributes
    completed = RoAttribute()
    completed_at = RoAttribute()
    created_at = RoAttribute()
    crowd_costs = RoAttribute()
    gold = RoAttribute()
    golds_count = RoAttribute()
    id = RoAttribute()
    judgments_count = RoAttribute()
    units_count = RoAttribute()
    updated_at = RoAttribute()

    # R/W attributes
    alias = Attribute()
    auto_order = Attribute()
    auto_order_threshold = Attribute()
    auto_order_timeout = Attribute()
    cml = Attribute()
    design_verified = Attribute()
    #: dict
    fields = Attribute()
    #: list
    confidence_fields = Attribute()
    css = Attribute()
    custom_key = Attribute()
    excluded_countries = Attribute()
    execution_mode = Attribute()
    expected_judgments_per_unit = Attribute()
    gold_per_assignment = Attribute()
    included_countries = Attribute()
    instructions = Attribute()
    js = Attribute()
    judgments_per_unit = Attribute()
    language = Attribute()
    max_judgments_per_unit = Attribute()
    max_judgments_per_contributor = Attribute()
    min_unit_confidence = Attribute()
    minimum_account_age_seconds = Attribute()
    #: dict
    minimum_requirements = Attribute()
    #: dict
    options = Attribute()
    pages_per_assignment = Attribute()
    problem = Attribute()
    public_data = Attribute()
    require_worker_login = Attribute()
    send_judgments_webhook = Attribute()
    state = Attribute()
    support_email = Attribute()
    title = Attribute()
    units_per_assignment = Attribute()
    units_remain_finalized = Attribute()
    variable_judgments_mode = Attribute()
    webhook_uri = Attribute()

    # Undocumented attributes, defaulted to RO
    copied_from = RoAttribute()
    desired_requirements = RoAttribute()
    order_approved = RoAttribute()
    project_number = RoAttribute()
    worker_ui_remix = RoAttribute()

    def __init__(self, client=None, **data):
        super(Job, self).__init__(data, client=client)

    def _send_changes(self, changes):
        """
        Update :class:`Job` instance changes to server and return resulting
        reply JSON data.

        Normally subclasses need not implement both :meth:`_send_changes` and
        :meth:`update` methods, but :class:`Job`s require special data inspections
        that must be documented clearly.
        """
        return self._client.update_job(self.id, changes)

    def update(self):
        """
        Send updates made to this instance to CrowdFlower. Note that :attr:`title`,
        :attr:`instructions` and :attr:`cml` attributes must exist (either in the
        update or in the job already) for any changes to really persist, and so this
        method raises a :exc:`RuntimeError`, if any of them is missing.

           "At minimum, your job must have a valid title, instructions, and one
           required CML form element to be saved successfully." [1]_

        .. warning::

           The API will happily return a "valid" response when sent only the
           'instructions', but nothing will change on the server side without
           all three. The caller is responsible for providing valid CML.

        .. [1] http://success.crowdflower.com/customer/portal/articles/1580923-jobs-resource-attributes#header_1
           (Fri Sep 5 11:38:42 UTC 2014)

        :raises: RuntimeError
        """
        for attr in {'title', 'instructions', 'cml'}:
            # Does a magic lookup to changes first, then the original json
            if not getattr(self, attr):
                raise RuntimeError(
                    "missing required attribute '{}'".format(attr))

        # calls Base.update, which calls _send_changes with changes dict
        super(Job, self).update()

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

        If type information is not given and guessing did not work,
        will raise a ValueError.

        Valid types are ``text/csv`` and ``application/json`` for ``.csv`` and
        ``.json`` respectively.

        :param file: A file like object or a filename string, contains UTF-8
                     encoded data
        :type file: str or file
        :param type_: Explicit type, required for file like objects
        :type type_: str
        """
        self._client.upload_job_file(file, type_, self.id)

    def delete(self):
        """
        Delete this job, removing it from CrowdFlower. Calling :class:`Job`
        instance will be invalid after deletion and must not be used anymore.
        """
        self._client.delete_job(self.id)

    @property
    def judgment_aggregates(self):
        """
        List of :class:`~.judgment.JudgmentAggregate` instances of this :class:`Job`.

        .. warning::

           Judgments are paged with a maximum of 100 items per page. If your
           job has a lot of judgments – thousands or more – this will take
           a very VERY long time to finish when accessed for the first time.
           This might produce some nasty surprises, if :class:`Job` instances
           are inspected with :func:`inspect.getmembers` or some such.

        """
        try:
            return self._judgments_aggregates

        except AttributeError:
            # noinspection PyAttributeOutsideInit
            self._judgments_aggregates = list(
                self._client.get_judgmentaggregates(self))
            return self._judgments_aggregates

    def get_judgment(self, judgment_id):
        """
        Get single :class:`~.judgment.Judgment` for this :class:`Job`.
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

    @property
    def channels(self):
        """
        List of enabled channels for this job.
        """
        return self._client.get_job_channels(self.id).get(
            'enabled_channels', [])

    @channels.setter
    def channels(self, channels):
        """
        Set enabled ``channels`` for this job.

        :type channels: list
        """
        self._client.set_job_channels(self.id, channels)

    @property
    def units(self):
        """
        List of :class:`~.unit.UnitPromise` instances of this :class:`Job`.
        """
        try:
            return self._units

        except AttributeError:
            # noinspection PyAttributeOutsideInit
            self._units = list(self._client.get_units(self))
            return self._units

    @_command
    def pause(self):
        """
        Temporarily stop judgments from coming in. A paused Job may
        ``resume``.
        """

    @_command
    def resume(self):
        """
        Resume a Job from ``pause`` at any time.
        """

    @_command
    def cancel(self):
        """
        Permanently ``cancel`` a Job, stopping any incoming judgments and
        refunding your account for unreceived judgments.
        """

    @_command
    def ping(self):
        """
        Check the status/progress of Job.
        """

    @_command
    def legend(self):
        """
        Display generated keys submitted with the form.
        """

    def get_worker(self, worker_id):
        """
        Get :class:`~.worker.Worker` ``worker_id`` bound to this :class:`Job`.
        """
        return Worker(self, client=self._client, id=worker_id)

    def launch(self, units_count, channels=('on_demand',)):
        """
        Order job with ``units_count`` at ``channels``.
        """
        return self._client.debit_order(self, units_count, channels)