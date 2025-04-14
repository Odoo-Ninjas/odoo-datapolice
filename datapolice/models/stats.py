from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class Stats(models.Model):
    _name = "data.police.stats"
    _order = "date_start desc"

    datapolice_id = fields.Many2one(
        "data.police", string="Datapolice", required=True, ondelete="cascade"
    )
    count_checked = fields.Integer(string="Count checked")
    count_errors = fields.Integer(string="Count Errors")
    percent_ok = fields.Float(string="Percent OK")
    date_start = fields.Datetime(
        "Date Start", default=lambda self: fields.Datetime.now()
    )
    date_stop = fields.Datetime("Date Stop")
    run_id = fields.Char()

    _sql_constraints = [
        ('unique_run', "unique(run_id)", _("Only one unique entry allowed.")),
    ]
