import json
from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError, RedirectWarning, ValidationError
class DataPoliceNewInfos(models.Model):
    _name = 'data.police.queue'

    infopackage = fields.Text()
    datapolice_id = fields.Many2one('data.police')
    action = fields.Selection([('dump_errors', "Dump Errors")])

    @api.model
    def run(self, datapolice_id):
        assert isinstance(datapolice_id, int)
        
        idkey = f"datapolice-queue-{datapolice_id}"
        self_queued = self.with_delay(identity_key=idkey, priority=1) if hasattr(self, 'with_delay') else self
        self_queued.process(datapolice_id)

    @api.model
    def cron_process(self):
        self.env.cr.execute("select distinct datapolice_id from data_police_queue")
        for id in self.env.cr.fetchall():
            id = id[0]
            self.run(id)
            self.env.cr.commit()

    def process(self, datapolice_id):
        entries = self.search([('datapolice_id', '=', datapolice_id)])
        for entry in entries:
            self.env.cr.execute(f"select id from {self._table} where id = %s for update nowait;", (entry.id,))
            data = json.loads(entry.infopackage)
            if entry.action == 'dump_errors':
                entry.datapolice_id._dump_last_errors(data)
                entry.unlink()
                self.env.cr.commit()
