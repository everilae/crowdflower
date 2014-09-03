CrowdFlower
===========

    "CrowdFlower offers scalable solutions that deliver fast and accurate
    results for business data problems. Find one that's best for you, and
    harness the power of the world's largest workforce." [1]_

    "The CrowdFlower API gives developers the ability to build applications
    that interact with and use all the features of CrowdFlower in an automated
    fashion. Tasks can be generated, work can be ordered, and your application
    can be notified as data is processed and judged by the CrowdFlower
    platform. The methods and practices described in this documentation are
    subject to change as the CrowdFlower API matures." [2]_

.. [1] http://crowdflower.com/overview
   (Fri Jan 17 11:27:23 UTC 2014)

.. [2] http://success.crowdflower.com/customer/portal/articles/1288323-api-documentation
   (Wed Sep 3 14:27:43 UTC 2014)

Python API
----------

This python implementation is an unofficial project not related, endorsed or
supported by CrowdFlower, Inc.

Examples
--------

.. code-block:: python

   >>> import crowdflower.client
   >>> client = crowdflower.client.Client('yourapikey')
   >>> job = client.get_job(123123)
   >>> job.title = 'New Title'
   >>> job.instructions = """
   ... <h1>Better instructions</h1>
   ... <p>You should read them</p>
   ... """
   >>> job.cml = """
   ... <cml:text label="Sample text field:" default="Enter text here" validates="required"/>
   ... """
   >>> # Send changes to server
   >>> job.update()

Status
------

Early alpha, things are going to change a lot still.

Contributors
------------

Ilja Everilä <ilja.everila@liilak.com>
