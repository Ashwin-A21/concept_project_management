# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

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

    @api.model_create_multi
    def create(self, vals_list):
        """Inherit project from Sale Order or Purchase Order when creating invoice/bill."""
        for vals in vals_list:
            # Skip if project is already set
            if vals.get('project_csl_id'):
                continue
                
            move_type = vals.get('move_type')
            
            # For Customer Invoices - get project from Sale Order
            if move_type in ('out_invoice', 'out_refund'):
                invoice_origin = vals.get('invoice_origin')
                if invoice_origin:
                    # Find the sale order by name
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', invoice_origin)
                    ], limit=1)
                    if sale_order and sale_order.project_csl_id:
                        vals['project_csl_id'] = sale_order.project_csl_id.id
            
            # For Vendor Bills - get project from Purchase Order
            elif move_type in ('in_invoice', 'in_refund'):
                # Check if there's a purchase order reference
                invoice_origin = vals.get('invoice_origin') or vals.get('ref')
                if invoice_origin:
                    # Find the purchase order by name
                    purchase_order = self.env['purchase.order'].search([
                        ('name', '=', invoice_origin)
                    ], limit=1)
                    if purchase_order and purchase_order.project_csl_id:
                        vals['project_csl_id'] = purchase_order.project_csl_id.id
        
        return super(AccountMove, self).create(vals_list)

    def write(self, vals):
        """Update project reference when invoice_origin changes."""
        res = super(AccountMove, self).write(vals)
        
        # If invoice_origin is updated, try to fetch project
        if 'invoice_origin' in vals or 'ref' in vals:
            for move in self:
                if move.project_csl_id:
                    continue  # Skip if already has project
                    
                # For Customer Invoices
                if move.move_type in ('out_invoice', 'out_refund') and move.invoice_origin:
                    sale_order = self.env['sale.order'].search([
                        ('name', '=', move.invoice_origin)
                    ], limit=1)
                    if sale_order and sale_order.project_csl_id:
                        move.project_csl_id = sale_order.project_csl_id.id
                
                # For Vendor Bills
                elif move.move_type in ('in_invoice', 'in_refund'):
                    ref = move.invoice_origin or move.ref
                    if ref:
                        purchase_order = self.env['purchase.order'].search([
                            ('name', '=', ref)
                        ], limit=1)
                        if purchase_order and purchase_order.project_csl_id:
                            move.project_csl_id = purchase_order.project_csl_id.id
        
        return res

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