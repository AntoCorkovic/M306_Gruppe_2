document.addEventListener("DOMContentLoaded", function () {
    const loader = document.getElementById("loader");
    const content = document.getElementById("content");
    const combinedCtx = document.getElementById('combinedChart').getContext('2d');
    const barCtx = document.getElementById('barChart').getContext('2d');
    const counterCtx = document.getElementById('counterChart').getContext('2d');
    const lineCtx = document.getElementById('lineChart').getContext('2d');
    const downloadButton = document.getElementById('downloadButton');
    const downloadCSV = document.getElementById('downloadCSV');
    const downloadJSON = document.getElementById('downloadJSON');
    const daterange = document.getElementById('daterange');
    const dropdownContent = document.querySelector('.dropdown-content');

    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const pageIndicator = document.getElementById('pageIndicator');

    let currentPage = 1;
    const rowsPerPage = 10;

    let combinedChart = null;
    let barChart = null;
    let counterChart = null;
    let lineChart = null;

    loader.style.display = "block";

    $(function () {
        $('input[name="daterange"]').daterangepicker({
            timePicker: true,
            timePicker24Hour: true,
            timePickerSeconds: false,
            locale: {
                format: 'DD-MM-YYYY HH:mm'
            },
            opens: 'left'
        }, function (start, end, label) {;
            console.log("A new date selection was made: " + start.format('YYYY-MM-DD HH:mm') + ' to ' + end.format('YYYY-MM-DD HH:mm'));
            showData(start.format('DD-MM-YYYY HH:mm'), end.format('DD-MM-YYYY HH:mm'))
        });
    });

    const fetchChartData = (startdatetime, enddatetime) => {
        const url = new URL('/chart/data', window.location.origin);
        const params = {
            startdatetime: startdatetime,
            enddatetime: enddatetime
        };

        url.search = new URLSearchParams(params).toString();

        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    alert('Leider haben wir keine Daten für diesen Zeitraum. Bitte wählen Sie einen anderen Zeitraum.');
                    throw new Error('Network response was not ok');
                }
                return response.json();
            });
    };

    const fetchData = () => {
        return fetch('/chart/data')
            .then(response => response.json())
            .then(data => {
                return data;
            });
    };

    downloadButton.addEventListener('click', function () {
        dropdownContent.classList.toggle('show');
    });

    function downloadData(format) {
        const data = JSON.parse(localStorage.getItem('chartData'));
        let content;
        if (format === 'csv') {
            content = convertToCSV(data);
        } else if (format === 'json') {
            content = JSON.stringify(data, null, 2);
        }
        const blob = new Blob([content], {type: 'text/plain;charset=utf-8'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chart_data.${format}`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function convertToCSV(objArray) {
        const array = typeof objArray !== 'object' ? JSON.parse(objArray) : objArray;
        let str = '';
        for (let i = 0; i < array.length; i++) {
            let line = '';
            for (let index in array[i]) {
                if (line !== '') line += ',';
                line += array[i][index];
            }
            str += line + '\r\n';
        }
        return str;
    }

    downloadCSV.addEventListener('click', () => downloadData('csv'));
    downloadJSON.addEventListener('click', () => downloadData('json'));

    const loadData = (start, end) => {
        return fetchChartData(start, end);
    };

    const calculateAxisLimits = (data) => {
        const minValue = Math.min(...data);
        const maxValue = Math.max(...data);
        const range = maxValue - minValue;
        const buffer = Math.ceil((range * 0.1) / 10) * 10; // 10% Puffer basierend auf dem Bereich, gerundet auf den nächsten Zehner
        return {min: Math.floor((minValue - buffer) / 10) * 10, max: Math.ceil((maxValue + buffer) / 10) * 10};
    };

    const updateAxes = (chart, inflowLimits, outflowLimits) => {
        chart.options.scales.y.min = outflowLimits.min -2000;
        chart.options.scales.y.max = inflowLimits.max + 2000;

    };

    showData("01-01-2019 00:00", "02-01-2019 23:00");

    function showData(start, end) {
        loadData(start, end)
            .then(data => {
                console.log(data); // Debugging the loaded data
                loader.style.display = "none";
                content.classList.remove("hidden");

                const compactData = (data, labels, maxPoints) => {
                    const interval = Math.max(1, Math.floor(data.length / maxPoints));
                    const compactedData = [];
                    const compactedLabels = [];

                    for (let i = 0; i < data.length; i += interval) {
                        compactedData.push(data[i]);
                        compactedLabels.push(labels[i]);
                    }

                    return {data: compactedData, labels: compactedLabels};
                };

                const inflowData = data.inflowData;
                const outflowData = data.outflowData;
                const timeLabels = data.timeLabels;
                const counterstandOfInflowAtStart = data.counterstandOfInflowAtStart;
                const counterstandOfOutflowAtStart = data.counterstandOfOutflowAtStart;
                const totalInflow = data.totalInflow;
                const totalOutflow = data.totalOutflow;
                const procentInflow = data.procentInflow;
                const procentOutflow = data.procentOutflow;

                let cumulativeInflowData = [];
                let cumulativeValueInflow = counterstandOfInflowAtStart;
                inflowData.forEach(volume => {
                    cumulativeValueInflow += volume;
                    cumulativeInflowData.push(cumulativeValueInflow);
                });

                let cumulativeOutflowData = [];
                let cumulativeValueOutflow = counterstandOfOutflowAtStart || 0; // Ensure there's a default value
                outflowData.forEach(volume => {
                    cumulativeValueOutflow += volume;
                    cumulativeOutflowData.push(cumulativeValueOutflow);
                });

                const inflowLimits = calculateAxisLimits(cumulativeInflowData);
                const outflowLimits = calculateAxisLimits(cumulativeOutflowData);


                const maxPointssum = 75;
                const compactedCombinedInflow = compactData(cumulativeInflowData, timeLabels, maxPointssum);
                const compactedCombinedOutflow = compactData(cumulativeOutflowData, timeLabels, maxPointssum);

                const combinedChartData = {
                    labels: compactedCombinedInflow.labels,
                    datasets: [
                        {
                            label: 'Bezug (kWh)',
                            data: compactedCombinedInflow.data,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 10,
                        },
                        {
                            label: 'Einspeisung (kWh)',
                            data: compactedCombinedOutflow.data,
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 0,
                            pointHoverRadius: 10,
                        }
                    ]
                };

                // Destroy existing chart instances if they exist
                if (combinedChart) {
                    combinedChart.destroy();
                }
                if (barChart) {
                    barChart.destroy();
                }
                if (counterChart) {
                    counterChart.destroy();
                }
                if (lineChart) {
                    lineChart.destroy();
                }

                combinedChart = new Chart(combinedCtx, {
                    type: 'line',
                    data: combinedChartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            duration: 2000,
                            easing: 'easeInOutQuart',
                            onProgress: function (animation) {
                                if (animation.currentStep === 0) {
                                    combinedChart.data.datasets.forEach(dataset => {
                                        if (!dataset._originalData) {
                                            dataset._originalData = dataset.data.slice();
                                        }
                                        dataset.data = dataset.data.map(() => inflowLimits.min);
                                    });
                                }
                            },
                            onComplete: function (animation) {
                                combinedChart.data.datasets.forEach(dataset => {
                                    dataset.data = dataset._originalData;
                                });
                                combinedChart.update();
                            }
                        },
                        scales: {
                            x: {
                                type: 'category'
                            },
                            y: {
                                type: 'linear',
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Bezug / Einspeisung (kWh)'
                                }
                            },

                        },
                        interaction: {
                            mode: 'index',
                            intersect: false
                        },
                        plugins: {
                            legend: {
                                onClick: function (e, legendItem, legend) {
                                    const index = legendItem.datasetIndex;
                                    const ci = legend.chart;
                                    const meta = ci.getDatasetMeta(index);

                                    meta.hidden = !meta.hidden;

                                    if (!meta.hidden) {
                                        let startValues = ci.data.datasets[index].data.map(() => inflowLimits.min);
                                        let endValues = ci.data.datasets[index]._originalData.slice();

                                        let animationDuration = 2000;
                                        let steps = 60;
                                        let stepIncrement = endValues.map((end, i) => (end - startValues[i]) / steps);

                                        let currentStep = 0;

                                        const animate = () => {
                                            currentStep++;
                                            ci.data.datasets[index].data = startValues.map((start, i) => start + stepIncrement[i] * currentStep);
                                            ci.update();

                                            if (currentStep < steps) {
                                                requestAnimationFrame(animate);
                                            }
                                        };

                                        requestAnimationFrame(animate);
                                    } else {
                                        ci.update();
                                    }

                                    updateAxes(ci, inflowLimits, outflowLimits);
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        label += context.parsed.y.toFixed(1);
                                        return label;
                                    }
                                }
                            },
                            zoom: {
                                zoom: {
                                    wheel: {
                                        enabled: true, // Enable zooming with the mouse wheel
                                        modifierKey: 'ctrl',
                                    },
                                    pinch: {
                                        enabled: true // Enable zooming with pinch gestures
                                    },

                                    mode: 'xy' // Allow zooming on both axes
                                },
                                pan: {
                                    enabled: true,
                                    mode: 'xy' // Allow panning on both axes
                                }
                            }
                        },
                        elements: {
            point: {
                radius: 0, // Remove the visualized points
                hoverRadius: 10 // Significantly increase hover radius
            }
        },
        interaction: {
            mode: 'nearest', // Display tooltip for the nearest point
            axis: 'x', // Only consider x-axis for nearest mode
            intersect: false // Trigger tooltip even when not intersecting a point
        },
        plugins: {
            tooltip: {
                enabled: true,
                mode: 'nearest',
                intersect: false // Ensure tooltips are shown when hovering near points
            }
        }
                    }
                });

                combinedChart.data.datasets.forEach(dataset => {
                    dataset._originalData = dataset.data.slice();
                });

                updateAxes(combinedChart, inflowLimits, outflowLimits);
                combinedChart.update();

const timeBlocks = [
    { label: '00:00 - 04:59', start: 0, end: 4 },
    { label: '05:00 - 08:59', start: 5, end: 8 },
    { label: '09:00 - 12:59', start: 9, end: 12 },
    { label: '13:00 - 16:59', start: 13, end: 16 },
    { label: '17:00 - 20:59', start: 17, end: 20 },
    { label: '21:00 - 23:59', start: 21, end: 23 }
];

const inflowBarData = Array(timeBlocks.length).fill(0);
const outflowBarData = Array(timeBlocks.length).fill(0);

// Aggregate data into time blocks
timeLabels.forEach((label, index) => {
    const hour = moment(label, 'YYYY-MM-DD HH:mm').hour(); // Parse the label correctly
    timeBlocks.forEach((block, blockIndex) => {
        if (hour >= block.start && hour <= block.end) {
            inflowBarData[blockIndex] += inflowData[index];
            outflowBarData[blockIndex] += outflowData[index];
        }
    });
});

const barLabels = timeBlocks.map(block => block.label);

const barChartData = {
    labels: barLabels,
    datasets: [
        {
            label: 'Bezug (kWh)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            data: inflowBarData
        },
        {
            label: 'Einspeisung (kWh)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1,
            data: outflowBarData
        }
    ]
};

barChart = new Chart(barCtx, {
    type: 'bar',
    data: barChartData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                beginAtZero: true
            },
            y: {
                beginAtZero: true
            }
        }
    }
});


                const maxPoints = 25;
                const compactedInflow = compactData(cumulativeInflowData, timeLabels, maxPoints);
                const compactedOutflow = compactData(cumulativeOutflowData, timeLabels, maxPoints);

                const counterChartData = {
                    labels: compactedInflow.labels,
                    datasets: [
                        {
                            label: 'Zählerstand Verbrauch (kWh)',
                            data: compactedInflow.data,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 5,
                            pointHoverRadius: 10,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Zählerstand Einspeisung (kWh)',
                            data: compactedOutflow.data,
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 5,
                            pointHoverRadius: 10,
                            yAxisID: 'y'
                        }
                    ]
                };

                counterChart = new Chart(counterCtx, {
                    type: 'bar',
                    data: counterChartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                type: 'category'
                            },
                            y: {
                                type: 'linear',
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Zählerstände Verbrauch / Einspeisung (kWh)'
                                }
                            },

                        },
                        plugins: {
                            zoom: {
                                zoom: {
                                    wheel: {
                                        enabled: true, // Enable zooming with the mouse wheel
                                        modifierKey: 'ctrl',
                                    },
                                    pinch: {
                                        enabled: true // Enable zooming with pinch gestures
                                    },
                                    mode: 'xy' // Allow zooming on both axes
                                },
                                pan: {
                                    enabled: true,
                                    mode: 'xy' // Allow panning on both axes
                                }
                            }
                        }
                    }
                });


                const maxPointsline = 75;
                const compactedInflowLine = compactData(inflowData, timeLabels, maxPointsline);
                const compactedOutflowLine = compactData(outflowData, timeLabels, maxPointsline);

                const lineChartData = {
    labels: compactedInflowLine.labels,
    datasets: [
        {
            label: 'Verbrauch (kWh)',
            data: compactedInflowLine.data,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2, // Make the line more bold
            fill: false,
            tension: 0.1,
            pointRadius: 0, // Remove visualized points
            pointHoverRadius: 10 // Significantly increase hover radius
        },
        {
            label: 'Einspeisung (kWh)',
            data: compactedOutflowLine.data,
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 2, // Make the line more bold
            fill: false,
            tension: 0.1,
            pointRadius: 0, // Remove visualized points
            pointHoverRadius: 10 // Significantly increase hover radius
        }
    ]
};

lineChart = new Chart(lineCtx, {
    type: 'line',
    data: lineChartData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: 'category'
            },
            y: {
                type: 'linear',
                position: 'left',
                title: {
                    display: true,
                    text: 'Verbrauch & Einspeisung (kWh)'
                }
            }
        },
        plugins: {
            zoom: {
                zoom: {
                    wheel: {
                        enabled: true,
                        modifierKey: 'ctrl' // Enable zooming only when Ctrl is pressed
                    },
                    pinch: {
                        enabled: true // Enable zooming with pinch gestures
                    },
                    mode: 'xy' // Allow zooming on both axes
                },
                pan: {
                    enabled: true,
                    mode: 'xy' // Allow panning on both axes
                }
            }
        },
        elements: {
            point: {
                radius: 0, // Remove the visualized points
                hoverRadius: 10 // Significantly increase hover radius
            }
        },
        interaction: {
            mode: 'nearest', // Display tooltip for the nearest point
            axis: 'x', // Only consider x-axis for nearest mode
            intersect: false // Trigger tooltip even when not intersecting a point
        },
        plugins: {
            tooltip: {
                enabled: true,
                mode: 'nearest',
                intersect: false // Ensure tooltips are shown when hovering near points
            }
        }
    }
});




                const total_inflow = document.getElementById('total-inflow-value');
                const total_outflow = document.getElementById('total-outflow-value');
                const average_inflow = document.getElementById('average-inflow');
                const average_outflow = document.getElementById('average-outflow');
                const time_difference = document.getElementById('time-differnce-value');

                total_inflow.innerText = `${totalInflow} kWh`;
                total_outflow.innerText = `${totalOutflow} kWh`;
                average_inflow.innerText = `${procentInflow} %`;
                average_outflow.innerText = `${procentOutflow} %`;

                // Assuming startMoment and endMoment are DateTime values
                const startMoment = moment(data.startdatetime);
                const endMoment = moment(data.enddatetime);

// Calculate the total duration
                const duration = moment.duration(endMoment.diff(startMoment));

// Calculate the total days and remaining hours
                const totalDays = Math.floor(duration.asDays());
                const remainingHours = duration.hours(); // Get the remaining hours after extracting days

// Display the time difference
                time_difference.innerText = `${totalDays} d ${remainingHours} h`;

            })
            .catch(error => {
                loader.style.display = "none";
                console.error('Error fetching data:', error);
            });
        document.addEventListener('keydown', (event) => {
        if (event.ctrlKey && event.key === 'd') {
            event.preventDefault();
            document.body.classList.toggle('dark-mode');
        }
    });
    }
});


