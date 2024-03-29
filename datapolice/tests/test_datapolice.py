import arrow
import os
import pprint
import logging
import time
import uuid
from datetime import datetime, timedelta
from unittest import skipIf
from odoo import api
from odoo import fields
from odoo.tests.common import TransactionCase, Form
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, RedirectWarning, ValidationError, AccessError


class TestDatapolice(TransactionCase):
    def test_check_expr(self):
        partner1 = self.env["res.partner"].create({"name": "partner1"})
        group1 = self.env['datapolice.cronjob.group'].create({})
        police = self.env["data.police"].create(
            {
                "name": "police1",
                "model_id": self.env.ref("base.model_res_partner").id,
                "check_expr": ("obj.name != 'partner1'"),
                "user_ids": self.env.user.ids,
                'cronjob_group_id': group1.id,
            }
        )

        errors = police.run_single_instance(partner1)
        self.assertEqual(len(errors), 1)
        police._send_mail_for_single_instance(partner1, errors)
