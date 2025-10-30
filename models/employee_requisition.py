# -*- coding: utf-8 -*-
from odoo import models, fields

class EmployeePurchaseRequisition(models.Model):
    _inherit = 'employee.purchase.requisition'

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
            'context': {'active_id': self.project_csl_id.id}
        }