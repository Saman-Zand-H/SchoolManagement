//
// Bars chart
//

var BarsChart = (function() {

    //
    // Variables
    //

    var $chart = $('#chart-bars');


    //
    // Methods
    //

    // Init chart
    function initChart($chart) {

        // Create chart
        var ordersChart = new Chart($chart, {
            type: 'bar',
            data: {
                labels: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Ddec'],
                datasets: [{
                    label: 'Sales',
                    data: [25, 20, 30, 10, 10, 29]
                }]
            }
        });

        // Save to jQuery object
        $chart.data('chart', ordersChart);
    }


    // Init chart
    if ($chart.length) {
        initChart($chart);
    }

})();