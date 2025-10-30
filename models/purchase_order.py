# -*- coding: utf-8 -*-
from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_csl_id = fields.Many2one(
        'project.csl', 
        string="Project (CSL)",
        help="Linked Project",
        ondelete='set null',
        copy=False,
        tracking=True
    )
    project_reference = fields.Char(
        string="Project Reference",
        related='project_csl_id.project_reference',
        store=True,
        readonly=True
    )

    def action_view_project(self):
        """Smart button action to view the related project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Project',
            'res_model': 'project.csl',
            'view_mode': 'form',
            'res_id': self.project_csl_id.id,
            'target': 'current',
            'context': {
                'active_id': self.project_csl_id.id,
                'default_notebook_page': 'Purchase Order'  # <-- Tell JS to open this page
            }
        }

    def _prepare_invoice(self):
        """Pass the project ID to the vendor bill when created."""
        invoice_vals = super()._prepare_invoice()
        if self.project_csl_id:
            invoice_vals['project_csl_id'] = self.project_csl_id.id
        return invoice_vals