document.addEventListener("DOMContentLoaded", function() {
    const loader = document.getElementById("loader");
    const content = document.getElementById("content");
    const combinedCtx = document.getElementById('combinedChart').getContext('2d');

    loader.style.display = "block";

    const fetchData = () => {
        return fetch('/chart/data')
            .then(response => response.json())
            .then(data => {
                localStorage.setItem('chartData', JSON.stringify(data));
                return data;
            });
    };

    const loadData = () => {
        const storedData = localStorage.getItem('chartData');
        if (storedData) {
            return Promise.resolve(JSON.parse(storedData));
        } else {
            return fetchData();
        }
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

    loadData()
        .then(data => {
            console.log(data); // Debugging the loaded data
            loader.style.display = "none";
            content.classList.remove("hidden");

            const inflowData = data.inflowData;
            const outflowData = data.outflowData;
            const timeLabels = data.timeLabels;
            const counterstandOfInflowAtStart = data.counterstandOfInflowAtStart;
            const counterstandOfOutflowAtStart = data.counterstandOfOutflowAtStart;

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
                        label: 'Einspeisung (Kumuliert)',
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
                        label: 'Bezug (Kumuliert)',
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

            const combinedChart = new Chart(combinedCtx, {
                type: 'line',
                data: combinedChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart',
                        onProgress: function(animation) {
                            if (animation.currentStep === 0) {
                                combinedChart.data.datasets.forEach(dataset => {
                                    if (!dataset._originalData) {
                                        dataset._originalData = dataset.data.slice();
                                    }
                                    dataset.data = dataset.data.map(() => inflowLimits.min);
                                });
                            }
                        },
                        onComplete: function(animation) {
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
                                text: 'Einspeisung (Kumuliert)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Bezug (Kumuliert)'
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
                            onClick: function(e, legendItem, legend) {
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
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    label += context.parsed.y.toFixed(1);
                                    return label;
                                }
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
        })
        .catch(error => {
            loader.style.display = "none";
            console.error('Error fetching data:', error);
        });
});

// Datepicker Modal
document.addEventListener("DOMContentLoaded", function() {
    const datePickerButton = document.getElementById('datePickerButton');
    const datePickerModal = document.getElementById('datePickerModal');
    const closeModal = document.getElementById('closeModal');
    const datePickerElement = document.getElementById('datePicker');

    datePickerButton.addEventListener('click', function() {
        datePickerModal.style.display = 'block';
    });

    closeModal.addEventListener('click', function() {
        datePickerModal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === datePickerModal) {
            datePickerModal.style.display = 'none';
        }
    });

    // Initialize the date picker
    flatpickr(datePickerElement, {
        mode: "range",
        dateFormat: "Y-m-d",
        onChange: function(selectedDates) {
            if (selectedDates.length === 2) {
                // Handle the date range selection
                console.log("Selected range: ", selectedDates);
                // Add your logic to update the chart data based on selected date range
            }
        }
    });
});
