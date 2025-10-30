# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    # 1. Define the new dropdown field
    csl_project_role = fields.Selection([
        ('none', 'None'),
        ('ceo', 'CEO'),
        ('project_manager', 'Project Manager'),
        ('purchase_manager', 'Purchase Manager'),
        ('hr_manager', 'HR Manager'),
        ('account_manager', 'Account Manager')
    ], string='Project (CSL) Role', 
       compute='_compute_csl_project_role', 
       inverse='_inverse_csl_project_role',
       store=False) # store=False is correct for compute/inverse on groups_id

    # 2. Helper method to get all role groups
    def _get_csl_role_groups(self):
        """Returns a dictionary mapping role key to the group record."""
        return {
            'ceo': self.env.ref('concept_project_management.group_project_csl_ceo', raise_if_not_found=False),
            'project_manager': self.env.ref('concept_project_management.group_project_csl_project_manager', raise_if_not_found=False),
            'purchase_manager': self.env.ref('concept_project_management.group_project_csl_purchase_manager', raise_if_not_found=False),
            'hr_manager': self.env.ref('concept_project_management.group_project_csl_hr_manager', raise_if_not_found=False),
            'account_manager': self.env.ref('concept_project_management.group_project_csl_account_manager', raise_if_not_found=False),
        }

    # 3. COMPUTE: Read the user's groups and set the dropdown
    @api.depends('groups_id')
    def _compute_csl_project_role(self):
        role_groups = self._get_csl_role_groups()
        # Create a reverse mapping {group_id: role_key}
        group_to_role = {group.id: role for role, group in role_groups.items() if group}
        
        for user in self:
            user.csl_project_role = 'none' # Default
            user_group_ids = user.groups_id.ids
            for group_id, role_key in group_to_role.items():
                if group_id in user_group_ids:
                    user.csl_project_role = role_key
                    break # Found the highest role, stop searching

    # 4. INVERSE: Read the dropdown and set the user's groups
    def _inverse_csl_project_role(self):
        role_groups = self._get_csl_role_groups()
        all_role_groups = self.env['res.groups'].concat(*[g for g in role_groups.values() if g])

        for user in self:
            if not user.csl_project_role or user.csl_project_role == 'none':
                # If 'None' is selected, remove user from all CSL roles
                user.groups_id -= all_role_groups
            else:
                # Get the group record for the selected role
                selected_group = role_groups.get(user.csl_project_role)
                if selected_group:
                    # Remove all roles, then add the selected one
                    # This ensures exclusivity
                    user.groups_id -= all_role_groups
                    user.groups_id += selected_group