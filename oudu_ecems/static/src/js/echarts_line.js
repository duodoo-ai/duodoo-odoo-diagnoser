odoo.define('ecems.EchartsLineWidget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var field_registry = require('web.field_registry');

    var EchartsLineWidget = AbstractField.extend({
        template: 'EchartsLineWidgetTemplate',

        init: function () {
            this._super.apply(this, arguments);
            // 初始化 ECharts 实例
            this.chartInstance = null;
        },

        start: function () {
            var self = this;
            return this._super().then(function () {
                self.renderChart();
            });
        },

        renderChart: function () {
            if (!this.chartInstance) {
                this.chartInstance = echarts.init(this.$el.get(0));
            }
            var option = JSON.parse(this.value);
            this.chartInstance.setOption(option);
        },
    });

    field_registry.add('echarts_line', EchartsLineWidget);

    return EchartsLineWidget;
});