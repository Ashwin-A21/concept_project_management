# -*- coding: utf-8 -*-
from odoo import models, fields

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')