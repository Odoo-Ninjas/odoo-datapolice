from odoo import api, models
from contextlib import contextmanager
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError
from .exceptions import RetryableJobError


class DatapoliceTools(models.Model):
    _name = "data.police.tools"

    @api.model
    def cursor_change_to_read_committed(self, cr=None):
        if self._is_testing():
            return
        cr = cr or self.env.cr
        level = self.pg_transaction_level(cr)
        if level != "read committed":
            cr.commit()
            cr.execute("SET TRANSACTION ISOLATION LEVEL read committed;")

    @api.model
    def pg_transaction_level(self, cr=None):
        cr = cr or self.env.cr
        cr.execute("SHOW transaction_isolation;")
        level = cr.fetchone()[0]
        return level

    @api.model
    def pg_assert_read_committed(self, cr=None):
        if self._is_testing():
            return
        level = self.pg_transaction_level(cr)
        if level != "read committed":
            raise ValidationError(
                f"Transaction isolation level is not read committed: {level}"
            )

    @api.model
    @contextmanager
    def pglock(self, name, hostwide=False, cr=None, wait=None):
        if not isinstance(name, (tuple, list)):
            name = [name]
        for item in name:
            self.env["zbs.tools"].pg_advisory_lock(
                item, hostwide=hostwide, wait=wait, cr=cr
            )
        yield

    @api.model
    def pg_advisory_lock(
        self, lock, ignore_retry=True, cr=None, wait=False, hostwide=False
    ):
        int_lock = self.pg_hash(lock)
        cr = cr or self.env.cr
        func = "pg_try_advisory_xact_lock"
        if wait:
            func = "pg_advisory_xact_lock"
        if hostwide:
            func = func.replace("_xact", "")
        cr.execute(f"SELECT {func}(%s);", (int_lock,))
        if wait:
            return

        excparams = {
            "msg": f"Could not acquire advisory lock on {lock} [{int_lock}]",
            "seconds": self._get_seconds(),
            "ignore_retry": ignore_retry,
        }

        try:
            acquired = cr.fetchone()[0]
            if not acquired:
                raise RetryableJobError(**excparams)
        except Exception as ex:
            raise RetryableJobError(**excparams) from ex
        return acquired
