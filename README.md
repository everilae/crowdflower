crowdflower
===========

.. code::

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
