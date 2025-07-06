# -*- coding: utf-8 -*-
"""
@Time    : 2025/04/13 08:50
@Author  : Jason Zou
@Email   : zou.jason@qq.com
@Company: zou.jason@qq.com
"""
from odoo import fields, models, api

class MaintenanceEquipmentInspectionItem(models.Model):
    """Model for managing equipment inspection items.
    This model is used to record the details of equipment inspection items,
    including the inspection it belongs to, item name, description, result,
    notes, and the scanned barcode.
    """
    _name = 'maintenance.equipment.inspection.item'
    _description = 'Equipment Inspection Item'

    # Relationship field linking to the equipment inspection record
    inspection_id = fields.Many2one(
        'maintenance.equipment.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade',
        help='The inspection this item belongs to.'
    )
    # Field to store the name of the inspection item
    name = fields.Char(
        string='Item Name',
        required=True,
        help='Name of the inspection item.'
    )
    # Field to store the description of the inspection item
    description = fields.Text(
        string='Description',
        help='Description of the inspection item.'
    )
    # Selection field to store the result of the inspection item
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('na', 'Not Applicable')
    ], string='Result', help='Result of the inspection item.')
    # Field to store additional notes about the inspection item
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the inspection item.'
    )
    # Field to store the scanned barcode value
    barcode = fields.Char(
        string='Barcode',
        help='Scanned barcode value'
    )

    @api.model
    def create_inspection_from_barcode(self, barcode):
        """
        Create an equipment inspection record by scanning the equipment barcode.
        :param barcode: The scanned equipment barcode value.
        :return: The created inspection record.
        """
        # Search for the equipment based on the scanned barcode
        equipment = self.env['maintenance.equipment'].search([('barcode', '=', barcode)], limit=1)
        if not equipment:
            raise ValueError("No equipment found with the provided barcode.")

        # Create a new equipment inspection record
        inspection = self.env['maintenance.equipment.inspection'].create({
            'equipment_id': equipment.id,
            # You may need to adjust other fields according to your actual requirements
        })
        return inspection

    def scan_barcode(self):
        """
        Trigger the barcode scanning logic.
        This method will redirect to the barcode scanning interface or trigger the front - end scanning.
        After scanning, it will automatically create an inspection record.
        """
        # Example: Call the front - end scanning logic
        action = {
            'type': 'ir.actions.client',
            'tag': 'barcode_scanner',
            'params': {
                'model': self._name,
                'record_ids': self.ids,
                'callback': 'create_inspection_from_barcode'
            }
        }
        return action
