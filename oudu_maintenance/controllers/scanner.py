from odoo import http
from odoo.http import request

class InspectionScannerController(http.Controller):

    @http.route('/barcode/inspection', type='json', auth='user')
    def handle_barcode(self, barcode, **kwargs):
        """ 处理扫码结果 """
        equipment = request.env['maintenance.equipment.barcode'].search([
            '|', ('equipment_id.name', '=', barcode),
                 ('equipment_id.serial_no', '=', barcode)
        ], limit=1)

        if not equipment:
            return {'error': '未找到匹配设备'}

        return {
            'equipment_id': equipment.equipment_id.id,
            'barcode_id': equipment.id
        }
