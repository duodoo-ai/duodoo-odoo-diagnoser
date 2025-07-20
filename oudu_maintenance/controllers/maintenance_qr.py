from odoo import http
from odoo.http import request


class MaintenanceQRController(http.Controller):

    @http.route('/maintenance/scan/<int:equipment_id>', auth='public', website=True)
    def scan_qr(self, equipment_id, **kwargs):
        equipment = request.env['maintenance.equipment'].sudo().browse(equipment_id)
        if not equipment.exists():
            return request.not_found()

        # 创建巡检记录
        inspection = request.env['equipment.inspection'].sudo().create({
            'equipment_id': equipment.id,
            'inspection_date': fields.Datetime.now(),
            'inspector_id': request.env.user.id
        })

        # 返回巡检表单
        return request.redirect(f'/web#id={inspection.id}&model=equipment.inspection&view_type=form')