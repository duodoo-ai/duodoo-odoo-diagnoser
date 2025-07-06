odoo.define('oudu_maintenance.barcode', function (require) {
"use strict";

var core = require('web.core');
var Scanner = require('web_editor.field_scanner');

return Scanner.include({
    _onBarcodeScanned: function(barcode) {
        var self = this;
        this._rpc({
            route: '/barcode/inspection',
            params: {barcode: barcode}
        }).then(function(result) {
            if (result.error) {
                self.do_warn(result.error);
            } else {
                self.trigger_up('barcode_scanned', {
                    barcode: barcode,
                    res_id: result.barcode_id
                });
            }
        });
    }
});

});
