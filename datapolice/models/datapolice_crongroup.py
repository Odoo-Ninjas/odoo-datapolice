from odoo import _, api, fields, models, SUPERUSER_ID
import uuid
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class CronjobGroup(models.Model):
    _name = "datapolice.cronjob.group"
    _rec_name = "cronjob_id"

    cronjob_id = fields.Many2one("ir.cron", string="Cronjob", required=False)
    police_ids = fields.One2many("data.police", "cronjob_group_id", string="Polices")

    def _make_cron(self):
        self.ensure_one()
        if self.cronjob_id:
            return

        self.cronjob_id = self.env["ir.cron"].create(
            {
                "name": f"datapolice crongroup #{self.id}",
                "model_id": self.env.ref(
                    "datapolice.model_datapolice_cronjob_group"
                ).id,
                "code": f"model.browse({self.id}).run_by_cron()",
                "numbercall": -1,
            }
        )

    @api.model
    def create(self, vals):
        if isinstance(vals.get("cronjob_id"), str):
            vals.pop("cronjob_id")
        res = super().create(vals)
        res._make_cron()
        return res

    def run_by_cron(self):
        polices = self.police_ids.filtered(lambda x: x.enabled)
        identifier = str(uuid.uuid4())
        for police in polices:
            police._with_delay().run_async(identifier)
        polices._with_delay()._send_mails(identifier)
        return True