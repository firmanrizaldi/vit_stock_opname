
from odoo import api, fields, models
import time
import datetime
import logging
_logger = logging.getLogger(__name__)


class workcenter(models.Model):
    _inherit = 'mrp.workcenter'

    storage_id = fields.Many2one(
        string='Storage',
        comodel_name='storage.proses'
    )
    
    
class storagee(models.Model):
    _name = 'storage.proses'

    name = fields.Char(string='Name')
