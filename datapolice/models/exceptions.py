try:
    from odoo.addons.queue_job.exception import RetryableJobError
except:

    class RetryableJobError(Exception):
        def __init__(self, *arsg, **kw):
            super().__init__(*args, **kw)
