document.addEventListener("DOMContentLoaded", function() {
    const loader = document.getElementById("loader");
    const content = document.getElementById("content");
    const combinedCtx = document.getElementById('combinedChart').getContext('2d');
    const barCtx = document.getElementById('barChart').getContext('2d');
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

    loader.style.display = "block";

    $(function() {
        $('input[name="daterange"]').daterangepicker({
            timePicker: true,
            timePicker24Hour: true,
            timePickerSeconds: false,
            locale: {
                format: 'DD-MM-YYYY HH:mm'
            },
            opens: 'left'
        }, function(start, end, label) {
            console.log("A new date selection was made: " + start.format('YYYY-MM-DD HH:mm') + ' to ' + end.format('YYYY-MM-DD HH:mm'));
            showData(start.format('DD-MM-YYYY HH:mm'), end.format('DD-MM-YYYY HH:mm'));
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

    downloadButton.addEventListener('click', function() {
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
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
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
        return { min: Math.floor((minValue - buffer) / 10) * 10, max: Math.ceil((maxValue + buffer) / 10) * 10 };
    };

    const updateAxes = (chart, inflowLimits, outflowLimits) => {
        chart.options.scales.y.min = inflowLimits.min;
        chart.options.scales.y.max = inflowLimits.max;
        chart.options.scales.y1.min = outflowLimits.min;
        chart.options.scales.y1.max = outflowLimits.max;
    };

    showData("01-01-2019 00:00", "02-01-2019 23:00");

    function showData(start, end) {
        loadData(start, end)
            .then(data => {
                console.log(data); // Debugging the loaded data
                loader.style.display = "none";
                content.classList.remove("hidden");

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

                const combinedChartData = {
                    labels: timeLabels,
                    datasets: [
                        {
                            label: 'Bezug (kWh)',
                            data: cumulativeInflowData,
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
                            label: 'Einspeisung (kWh)',
                            data: cumulativeOutflowData,
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1,
                            fill: false,
                            tension: 0.1,
                            pointRadius: 5,
                            pointHoverRadius: 10,
                            yAxisID: 'y1'
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
                                    text: 'Bezug (kWh)'
                                }
                            },
                            y1: {
                                type: 'linear',
                                position: 'right',
                                title: {
                                    display: true,
                                    text: 'Einspeisung (kWh)'
                                },
                                grid: {
                                    drawOnChartArea: false
                                }
                            }
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

                combinedChart.data.datasets.forEach(dataset => {
                    dataset._originalData = dataset.data.slice();
                });

                updateAxes(combinedChart, inflowLimits, outflowLimits);
                combinedChart.update();

                // Adding the bar chart initialization
                const numberOfBars = 6;
                const inflowBarData = [];
                const outflowBarData = [];
                const barLabels = [];
                const inflowInterval = Math.floor(inflowData.length / numberOfBars);
                const outflowInterval = Math.floor(outflowData.length / numberOfBars);

                for (let i = 0; i < numberOfBars; i++) {
                    const inflowSlice = inflowData.slice(i * inflowInterval, (i + 1) * inflowInterval);
                    const outflowSlice = outflowData.slice(i * outflowInterval, (i + 1) * outflowInterval);
                    inflowBarData.push(inflowSlice.reduce((a, b) => a + b, 0));
                    outflowBarData.push(outflowSlice.reduce((a, b) => a + b, 0));
                    const startTime = moment(timeLabels[i * inflowInterval]);
                    const endTime = moment(timeLabels[Math.min((i + 1) * inflowInterval, timeLabels.length - 1)]);
                    barLabels.push(`${startTime.format('HH:mm')} - ${endTime.format('HH:mm')}`);
                }

                if (inflowData.length % numberOfBars !== 0) {
                    inflowBarData.push(inflowData.slice(numberOfBars * inflowInterval).reduce((a, b) => a + b, 0));
                    outflowBarData.push(outflowData.slice(numberOfBars * outflowInterval).reduce((a, b) => a + b, 0));
                    const startTime = moment(timeLabels[numberOfBars * inflowInterval]);
                    const endTime = moment(timeLabels[timeLabels.length - 1]);
                    barLabels.push(`${startTime.format('HH:mm')} - ${endTime.format('HH:mm')}`);
                }

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

                // Fake data for files
                const fileTableBody = document.getElementById('fileTableBody');
                const fakeFiles = [
                    {filename: 'file1.txt', status: 'Bezug'},
                    {filename: 'file2.txt', status: 'Einspeisung'},
                    {filename: 'file3.txt', status: 'Bezug'},
                    {filename: 'file4.txt', status: 'Einspeisung'},
                    {filename: 'file5.txt', status: 'Bezug'},
                    {filename: 'file6.txt', status: 'Einspeisung'},
                    {filename: 'file7.txt', status: 'Bezug'},
                    {filename: 'file8.txt', status: 'Einspeisung'},
                    {filename: 'file9.txt', status: 'Bezug'},
                    {filename: 'file10.txt', status: 'Einspeisung'},
                    {filename: 'file11.txt', status: 'Bezug'},
                    {filename: 'file12.txt', status: 'Einspeisung'},
                    {filename: 'file13.txt', status: 'Bezug'},
                    {filename: 'file14.txt', status: 'Einspeisung'},
                    {filename: 'file15.txt', status: 'Bezug'},
                    {filename: 'file16.txt', status: 'Einspeisung'},
                    {filename: 'file17.txt', status: 'Bezug'},
                    {filename: 'file18.txt', status: 'Einspeisung'},
                    {filename: 'file19.txt', status: 'Bezug'},
                    {filename: 'file20.txt', status: 'Einspeisung'}
                ];
                const total_inflow = document.getElementById('total-inflow');
                const total_outflow = document.getElementById('total-outflow');
                const average = document.getElementById('average');

                total_inflow.innerText = `Total Bezug: ${totalInflow} kWh`;
                total_outflow.innerText = `Total Einspeisung: ${totalOutflow} kWh`;
                average.innerText = ` Bezug: ${procentInflow} %,  Einspeisung: ${procentOutflow} %`;

                const renderTable = (page = 1) => {
                    const start = (page - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const filesToDisplay = fakeFiles.slice(start, end);

                    fileTableBody.innerHTML = '';
                    filesToDisplay.forEach(file => {
                        const row = document.createElement('tr');
                        const filenameCell = document.createElement('td');
                        const statusCell = document.createElement('td');
                        const actionCell = document.createElement('td');
                        const downloadButton = document.createElement('button');
                        const icon = document.createElement('i');
                        const statusIcon = document.createElement('i');

                        filenameCell.textContent = file.filename;

                        statusIcon.className = 'fas fa-bolt';
                        statusIcon.style.color = file.status === 'Bezug' ? 'rgba(153, 102, 255, 1)' : 'rgba(75, 192, 192, 1)';

                        statusCell.className = 'file-status';
                        statusCell.appendChild(statusIcon);
                        statusCell.appendChild(document.createTextNode(file.status));

                        downloadButton.className = 'download-button';
                        downloadButton.textContent = 'Download';
                        icon.className = 'fas fa-download download-icon';
                        downloadButton.appendChild(icon);
                        actionCell.appendChild(downloadButton);

                        row.appendChild(filenameCell);
                        row.appendChild(statusCell);
                        row.appendChild(actionCell);

                        fileTableBody.appendChild(row);
                    });

                    pageIndicator.textContent = `Page ${page} of ${Math.ceil(fakeFiles.length / rowsPerPage)}`;
                    prevPageBtn.disabled = page === 1;
                    nextPageBtn.disabled = page === Math.ceil(fakeFiles.length / rowsPerPage);
                };

                renderTable(currentPage);

                prevPageBtn.addEventListener('click', () => {
                    if (currentPage > 1) {
                        currentPage--;
                        renderTable(currentPage);
                    }
                });

                nextPageBtn.addEventListener('click', () => {
                    if (currentPage < Math.ceil(fakeFiles.length / rowsPerPage)) {
                        currentPage++;
                        renderTable(currentPage);
                    }
                });
            })
            .catch(error => {
                loader.style.display = "none";
                console.error('Error fetching data:', error);
            });
    }
});
