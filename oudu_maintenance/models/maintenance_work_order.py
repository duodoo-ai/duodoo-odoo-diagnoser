# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/13 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
from odoo import fields, models, api

class MaintenanceWorkOrder(models.Model):
    """Model for managing maintenance work orders."""
    _name = 'maintenance.work.order'
    _inherit = 'maintenance.request'
    _description = 'Maintenance Work Order'

    order_number = fields.Char(string='Order Number', required=True, copy=False, readonly=True,
                               default=lambda self: self.env['ir.sequence'].next_by_code('maintenance.work.order'))
    assigned_to = fields.Many2one('res.users', string='Assigned To', required=True)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    work_order_status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    history_ids = fields.One2many('maintenance.work.order.history', 'work_order_id', string='Work Order History')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._create_history_record('created', 'Work order created.')
        return res

    def write(self, vals):
        old_status = self.work_order_status
        res = super().write(vals)
        if 'work_order_status' in vals and old_status != vals['work_order_status']:
            self._create_history_record('status_changed', f'Status changed from {old_status} to {vals["work_order_status"]}.')
        return res

    def _create_history_record(self, event_type, description):
        self.ensure_one()
        self.env['maintenance.work.order.history'].create({
            'work_order_id': self.id,
            'event_type': event_type,
            'description': description,
            'event_date': fields.Datetime.now()
        })