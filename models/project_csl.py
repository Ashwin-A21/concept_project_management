# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class ProjectCsl(models.Model):
    _name = 'project.csl'
    _description = 'Custom Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Project Title', required=True, tracking=True)
    project_reference = fields.Char(string='Project Reference', readonly=True, copy=False, tracking=True)

    # Customer field (Project Co-ordinator)
    partner_id = fields.Many2one(
        'res.partner',
        string='Project Co-ordinator',
        tracking=True,
        # domain=[('customer_rank', '>', 0)] # Domain removed as requested
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        # domain=[('customer_rank', '>', 0)], # Domain removed as requested
        tracking=True,
        required=True
    )


    date_start = fields.Date(string='Start Date', default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string='End Date', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft', copy=False, tracking=True)

    # --- Notebook fields ---

    # Page 1: Project Details
    scope_work_set_id = fields.Many2one('scope.work.set', string='Scope of Work')
    project_scope_line_ids = fields.One2many('project.scope.line', 'project_id', string='Project Scope Lines')

    # Page 2: Quotation
    project_quotation_line_ids = fields.One2many('project.quotation.line', 'project_id', string='Quotation Lines')
    quotation_count = fields.Integer(string='Quotation Count', compute='_compute_quotation_count')
    
    # Page 3: Invoice
    invoice_ids = fields.One2many(
        'account.move', 
        'project_csl_id', 
        string='Invoices', 
        domain=[('move_type', '=', 'out_invoice')]
    )
    invoice_count = fields.Integer(string='Number of Invoices', compute='_compute_invoice_count')

    # Page 4: Purchase Order
    project_purchase_line_ids = fields.One2many(
        'project.purchase.line',
        'project_id',
        string='Purchase Order Lines'
    )
    purchase_order_count = fields.Integer(string='Purchase Order Count', compute='_compute_purchase_order_count')


    # Page 5: Purchase (Vendor Bills)
    project_bill_ids = fields.One2many(
        'account.move',
        'project_csl_id',
        string='Vendor Bills',
        domain=[('move_type', '=', 'in_invoice')]
    )
    project_bill_count = fields.Integer(string='Vendor Bill Count', compute='_compute_project_bill_count')


    # Page 6: Employee
    employee_ids = fields.Many2many(
        'hr.employee',
        'project_csl_employee_rel',
        'project_id',
        'employee_id',
        string='Employees'
    )
    
    # --- NEW: Purchase Request Lines ---
    employee_requisition_line_ids = fields.One2many(
        'project.employee.requisition.line', 
        'project_id', 
        string='Employee Requisition Lines'
    )
    employee_requisition_count = fields.Integer(
        string='Purchase Request Count', 
        compute='_compute_employee_requisition_count'
    )
    
    # Other Notebook fields (moved to end)
    estimated_cost_details = fields.Text(string='Estimated Cost Details')
    budget_details = fields.Text(string='Budget Details')
    task_duties_details = fields.Text(string='Task & Duties Details')
    # This text field is now replaced by the One2many table
    # purchase_request_details = fields.Text(string='Purchase Request Details') 
    cost_details = fields.Text(string='Cost Details')
    
    # --- Compute & Onchange ---

    @api.depends('project_quotation_line_ids.quotation_id')
    def _compute_quotation_count(self):
        for rec in self:
            rec.quotation_count = len(rec.project_quotation_line_ids.quotation_id)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)
            
    @api.depends('project_purchase_line_ids.purchase_order_id')
    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = len(rec.project_purchase_line_ids.purchase_order_id)
            
    @api.depends('project_bill_ids')
    def _compute_project_bill_count(self):
        for rec in self:
            rec.project_bill_count = len(rec.project_bill_ids)

    @api.depends('employee_requisition_line_ids')
    def _compute_employee_requisition_count(self):
        for rec in self:
            rec.employee_requisition_count = len(rec.employee_requisition_line_ids)
            
    @api.onchange('scope_work_set_id')
    def _onchange_scope_work_set_id(self):
        """Populate project scope lines from the selected set."""
        if not self.scope_work_set_id:
            self.project_scope_line_ids = [(5, 0, 0)] # Remove all existing lines
            return

        lines_to_create = []
        for line in self.scope_work_set_id.work_line_ids:
            lines_to_create.append((0, 0, {
                'name': line.name,
                'sequence': line.sequence,
            }))
        
        # Replace existing lines with new ones
        self.project_scope_line_ids = [(5, 0, 0)] 
        self.project_scope_line_ids = lines_to_create

    
    # --- Sequence ---
    
    @api.model
    def create(self, vals):
        company_id = vals.get('company_id') or self.env.company.id
        if not vals.get('project_reference'):
            seq = self._get_or_create_company_sequence(company_id)
            vals['project_reference'] = seq.next_by_id() or '/'

        project = super(ProjectCsl, self).create(vals)
        # Note: Linking quotations is now handled by 'project.quotation.line' model
        return project

    def _get_or_create_company_sequence(self, company_id):
        """Ensure each company has its own independent sequence."""
        IrSequence = self.env['ir.sequence']
        company_seq = IrSequence.search([
            ('code', '=', 'project.csl.reference'),
            ('company_id', '=', company_id)
        ], limit=1)

        if not company_seq:
            base_seq = IrSequence.search([
                ('code', '=', 'project.csl.reference'),
                ('company_id', '=', False)
            ], limit=1)

            if base_seq:
                # Copy base sequence for this company
                company_seq = base_seq.copy({'company_id': company_id})
            else:
                # Create new if not found at all
                company_seq = IrSequence.create({
                    'name': f'Project Reference ({company_id})',
                    'code': 'project.csl.reference',
                    'prefix': 'PR/',
                    'padding': 2,
                    'number_next': 1,
                    'number_increment': 1,
                    'company_id': company_id,
                })
        return company_seq

    def write(self, vals):
        """Note: Linking quotations is now handled by 'project.quotation.line' model"""
        res = super().write(vals)
        return res
    
    # --- Actions ---

    def action_create_invoice(self):
        """Create one invoice per selected quotation after verifying they are confirmed."""
        self.ensure_one()

        if not self.project_quotation_line_ids:
            raise UserError("Please select at least one quotation to create invoices.")

        created_invoices = self.env['account.move']
        
        # Use quotations from the new lines
        quotations_to_invoice = self.project_quotation_line_ids.quotation_id

        for sale_order in quotations_to_invoice:
            # Check if an invoice already exists for this SO via this project
            existing_invoice = self.invoice_ids.filtered(lambda inv: inv.invoice_origin == sale_order.name)
            if existing_invoice:
                continue # Skip if already invoiced from this project

            if sale_order.state != 'sale':
                raise UserError(
                    f"The quotation '{sale_order.name}' is not confirmed.\n"
                    f"Please confirm the quotation before creating an invoice."
                )

            if not sale_order.order_line:
                raise UserError(f"The quotation '{sale_order.name}' has no products to invoice.")

            # Use standard Odoo method to prepare invoice values
            # This handles taxes, accounts, etc. correctly
            invoice_vals = sale_order._prepare_invoice_values()

            # Add project link
            invoice_vals['project_csl_id'] = self.id # ✅ Link invoice to this project
            
            invoice = self.env['account.move'].create(invoice_vals)

            # Link invoice back to SO (standard Odoo behavior)
            sale_order.invoice_ids = [(4, invoice.id)]

            created_invoices |= invoice

        # Return invoices action window
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', created_invoices.ids)]
        return action
        
    def action_view_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotations',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.project_quotation_line_ids.quotation_id.ids)],
            'context': {'create': False}
        }
        
    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'create': False, 'default_move_type': 'out_invoice'}
        }
        
    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.project_purchase_line_ids.purchase_order_id.ids)],
            'context': {'create': False}
        }

    def action_view_vendor_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bills',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.project_bill_ids.ids)],
            'context': {'create': False, 'default_move_type': 'in_invoice'}
        }

    def action_view_employee_requisitions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Requests',
            'res_model': 'employee.purchase.requisition',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.employee_requisition_line_ids.requisition_id.ids)],
            'context': {'create': False}
        }

    # Buttons
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_csl_id = fields.Many2one(
        'project.csl',
        string="Project",
        help="Linked Project",
        ondelete='set null',
        copy=False,
    )

    project_reference = fields.Char(
        string="Project Reference",
        related='project_csl_id.project_reference',
        store=True,
        readonly=True
    )

    def _prepare_invoice_values(self):
        """Pass the project ID to the invoice when created from the SO."""
        invoice_vals = super()._prepare_invoice_values()
        if self.project_csl_id:
            invoice_vals['project_csl_id'] = self.project_csl_id.id
        return invoice_vals

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