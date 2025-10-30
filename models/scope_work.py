# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ScopeWorkSet(models.Model):
    _name = 'scope.work.set'
    _description = 'Scope of Work Set'

    name = fields.Char(string='Set Name', required=True)
    work_line_ids = fields.One2many('scope.work.line', 'set_id', string='Work Lines')

class ScopeWorkLine(models.Model):
    _name = 'scope.work.line'
    _description = 'Scope of Work Line'
    _order = 'sequence, id'

    name = fields.Char(string='Work Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    set_id = fields.Many2one('scope.work.set', string='Work Set', required=True, ondelete='cascade')

class ProjectScopeLine(models.Model):
    _name = 'project.scope.line'
    _description = 'Project Scope Line'
    _order = 'sequence, id'

    name = fields.Char(string='Work Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    project_id = fields.Many2one('project.csl', string='Project', required=True, ondelete='cascade')