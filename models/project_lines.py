# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProjectQuotationLine(models.Model):
    _name = 'project.quotation.line'
    _description = 'Project Quotation Line'

    project_id = fields.Many2one('project.csl', string='Project', required=True, ondelete='cascade')
    quotation_id = fields.Many2one(
        'sale.order', 
        string='Quotation', 
        required=True,
        domain="[('state', 'in', ['draft', 'sent', 'sale']), ('partner_id', '=', parent.customer_id)]"
    )
    
    # Related fields for display in the tree view
    amount_untaxed = fields.Monetary(
        string='Tax Excluded', 
        related='quotation_id.amount_untaxed', 
        readonly=True
    )
    amount_tax = fields.Monetary(
        string='Tax', 
        related='quotation_id.amount_tax', 
        readonly=True
    )
    amount_total = fields.Monetary(
        string='Total Amount', 
        related='quotation_id.amount_total', 
        readonly=True
    )
    currency_id = fields.Many2one(
        related='quotation_id.currency_id', 
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Link the quotation and its invoices back to the project on creation."""
        lines = super().create(vals_list)
        for line in lines:
            if line.quotation_id and line.project_id:
                # Link quotation to project
                line.quotation_id.project_csl_id = line.project_id
                
                # Link existing invoices from this quotation to the project
                if line.quotation_id.invoice_ids:
                    line.quotation_id.invoice_ids.write({
                        'project_csl_id': line.project_id.id
                    })
        return lines

    def write(self, vals):
        """Update the quotation link and its invoices if it changes."""
        res = super().write(vals)
        if 'quotation_id' in vals or 'project_id' in vals:
            for line in self:
                if line.quotation_id and line.project_id:
                    # Link quotation to project
                    line.quotation_id.project_csl_id = line.project_id
                    
                    # Link existing invoices from this quotation to the project
                    if line.quotation_id.invoice_ids:
                        line.quotation_id.invoice_ids.write({
                            'project_csl_id': line.project_id.id
                        })
        return res

# --- MODEL FOR PURCHASE ORDER LINES ---

class ProjectPurchaseLine(models.Model):
    _name = 'project.purchase.line'
    _description = 'Project Purchase Line'

    project_id = fields.Many2one('project.csl', string='Project', required=True, ondelete='cascade')
    purchase_order_id = fields.Many2one(
        'purchase.order', 
        string='Purchase Order', 
        required=True,
        domain="[('state', 'in', ['draft', 'sent', 'to approve', 'purchase'])]"
    )
    
    # Related fields for display in the tree view
    partner_id = fields.Many2one(
        string='Vendor',
        related='purchase_order_id.partner_id',
        readonly=True
    )
    amount_untaxed = fields.Monetary(
        string='Tax Excluded', 
        related='purchase_order_id.amount_untaxed', 
        readonly=True
    )
    amount_tax = fields.Monetary(
        string='Tax', 
        related='purchase_order_id.amount_tax', 
        readonly=True
    )
    amount_total = fields.Monetary(
        string='Total Amount', 
        related='purchase_order_id.amount_total', 
        readonly=True
    )
    currency_id = fields.Many2one(
        related='purchase_order_id.currency_id', 
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Link the purchase order and its bills back to the project on creation."""
        lines = super().create(vals_list)
        for line in lines:
            if line.purchase_order_id and line.project_id:
                # Link PO to project
                line.purchase_order_id.project_csl_id = line.project_id
                
                # Link existing vendor bills from this PO to the project
                if line.purchase_order_id.invoice_ids:
                    line.purchase_order_id.invoice_ids.write({
                        'project_csl_id': line.project_id.id
                    })
        return lines

    def write(self, vals):
        """Update the purchase order link and its bills if it changes."""
        res = super().write(vals)
        if 'purchase_order_id' in vals or 'project_id' in vals:
            for line in self:
                if line.purchase_order_id and line.project_id:
                    # Link PO to project
                    line.purchase_order_id.project_csl_id = line.project_id
                    
                    # Link existing vendor bills from this PO to the project
                    if line.purchase_order_id.invoice_ids:
                        line.purchase_order_id.invoice_ids.write({
                            'project_csl_id': line.project_id.id
                        })
        return res

# --- MODEL FOR EMPLOYEE PURCHASE REQUISITION LINES ---

class ProjectEmployeeRequisitionLine(models.Model):
    _name = 'project.employee.requisition.line'
    _description = 'Project Employee Requisition Line'

    project_id = fields.Many2one('project.csl', string='Project', required=True, ondelete='cascade')
    requisition_id = fields.Many2one(
        'employee.purchase.requisition', 
        string='Purchase Requisition', 
        required=True
    )
    
    # Related fields for display
    name = fields.Char(related='requisition_id.name', string="Reference", readonly=True)
    employee_id = fields.Many2one(related='requisition_id.employee_id', readonly=True)
    dept_id = fields.Many2one(related='requisition_id.dept_id', readonly=True)
    requisition_date = fields.Date(related='requisition_id.requisition_date', readonly=True)
    state = fields.Selection(related='requisition_id.state', readonly=True)