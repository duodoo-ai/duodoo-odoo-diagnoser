odoo.define('ecems.dashboard', function (require) {
"use strict";

var KanbanController = require('web.KanbanController');
var core = require('web.core');
var QWeb = core.qweb;

// 加载ECharts
require('../lib/echarts/echarts.min');

KanbanController.include({
    willStart: function () {
        return $.when(
            this._super.apply(this, arguments),
            this._loadECharts()
        );
    },

    _loadECharts: function () {
        return $.getScript('/ecems/static/lib/echarts/echarts.min.js');
    },

    renderButtons: function ($node) {
        this._super.apply(this, arguments);
        this._renderChart();
    },

    _renderChart: function () {
        var self = this;
        this.model.query([]).then(function (records) {
            var data = records[0].data.hourly_trend_data;
            var chart = echarts.init(document.getElementById('hourly_trend_chart'));

            var option = {
                xAxis: { type: 'category', data: Object.keys(data) },
                yAxis: { type: 'value' },
                series: [{
                    data: Object.values(data).map(v => v.energy),
                    type: 'line'
                }]
            };
            chart.setOption(option);
        });
    }
});
});