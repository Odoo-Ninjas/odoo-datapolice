from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError, RedirectWarning, ValidationError
class IncChecked(models.Model):
    _name = 'datapolice.increment'

    ttype = fields.Selection([('fix', 'fix'), ('check', 'check')], index=True)
    run_id = fields.Char()
    model = fields.Char()
    dp_id = fields.Integer(index=True)
    value = fields.Integer(default=1, required=True)

    @api.autovacuum
    def _gc(self):
        records = self.search([('create_date', '<', fields.Datetime.subtract(fields.Datetime.now(), days=30))])
        for record in records:
            record.unlink()
            self.env.cr.commit()

    def _compress(self):
        env = self.env
        env.cr.execute("select distinct run_id from datapolice_increment")
        run_ids = env.cr.fetchall()
        for run_id in run_ids:
            env.cr.execute("""
                select 
                    sum(value), ttype, model, max(create_date), run_id, dp_id 
                from datapolice_increment 
                where run_id=%s
                group by run_id, ttype, model, dp_id
            """, (run_id,))
            for rec in env.cr.fetchall():
                value, ttype, model, create_date, run_id, dp_id = rec
                env.cr.execute("""
                    delete from datapolice_increment 
                    where run_id = %s and ttype = %s and model = %s
                """, (run_id, ttype, model))
                env.cr.execute(""""
                    insert into datapolice_increment(
                        run_id, ttype, model, value, create_date)
                    values (%s, %s, %s, 0, %s, %s)
                """, (run_id, ttype, model, value, create_date))
            env.cr.commit()