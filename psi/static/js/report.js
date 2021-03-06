var GetDataForLineGraph = function (report_type, report_period) {
    $.ajax({
        url: '/api/reports/' + report_type + "/" + report_period,
        type: 'GET',
        success: function (response) {
            response = $.parseJSON(response);
            if (response.status === 'success') {
                var ctx1 = $("#" + report_type + "_" + report_period);
                var data = response.data;
                var options = {};
                new Chart(ctx1, {
                    type: 'line',
                    fill: true,
                    data: {
                        "labels": data.labels,
                        "datasets": [{
                            fill: true,
                            backgroundColor: "rgba(75,192,192,0.1)",
                            borderColor: "rgba(75,192,192,1)",
                            borderCapStyle: 'butt',
                            borderDash: [],
                            borderDashOffset: 0.0,
                            pointBorderColor: "rgba(75,192,192,1)",
                            pointBackgroundColor: "#fff",
                            pointBorderWidth: 1,
                            pointHoverRadius: 5,
                            pointHoverBackgroundColor: "rgba(75,192,192,1)",
                            pointHoverBorderColor: "rgba(220,220,220,1)",
                            pointHoverBorderWidth: 2,
                            pointRadius: 5,
                            pointHitRadius: 10,
                            "label": data.label,
                            "data": data.data
                        }, {
                            "label": data.label_average,
                            "data": data.data_average,
                            "fill": false,
                            "pointRadius": 0,
                            "borderColor": "rgba(192,192,75,1)"
                        }]
                    },
                    options: options
                });
            } else if (response.status === 'error') {
                var error_panel = $("#" + report_type + "_" + report_period + "_error_info");
                error_panel.html(response.data.message);
                error_panel.addClass('small-error-text');
            }
        },
        error: function (response) {
        }
    });
};

var getCompareData = function (report_type, report_period) {
    $.ajax({
        url: '/api/reports/' + report_type + "/" + report_period,
        type: 'GET',
        success: function(response) {
            response = $.parseJSON(response);
            var display_panel = $("#" + report_type + '_' + report_period);
            if (response.status === 'success') {
                var data = response.data, icon = "";
                if (data.change === 'decrease') {
                    icon = '<span class="glyphicon glyphicon-arrow-down"></span>';
                    display_panel.parent().parent().addClass('down-cell');
                } else if (data.change === 'increase') {
                    icon = '<span class="glyphicon glyphicon-arrow-up"></span>';
                    display_panel.parent().parent().addClass('up-cell');
                } else {
                    display_panel.parent().parent().addClass('gray-cell');
                }
                display_panel.html(data.data + icon);
            } else if (response.status === 'error'){
                icon = '<span class="glyphicon glyphicon-warning-sign"></span> &nbsp;&nbsp;';
                var error_panel = $("#" + report_type + '_' + report_period + "_error_info");
                error_panel.addClass('small-error-text');
                error_panel.html(icon + response.data.message);
            }
        },
        error: function (response) {
        }
    });
};