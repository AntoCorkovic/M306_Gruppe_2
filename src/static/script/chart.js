document.addEventListener("DOMContentLoaded", function() {
    const loader = document.getElementById("loader");
    const content = document.getElementById("content");
    const inflowCtx = document.getElementById('inflowChart').getContext('2d');
    const outflowCtx = document.getElementById('outflowChart').getContext('2d');

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

    loadData()
        .then(data => {
            loader.style.display = "none";
            content.classList.remove("hidden");

            const inflowData = data.inflowData;
            const outflowData = data.outflowData;
            const timeLabels = data.timeLabels;
            const counterstandOfInflowAtStart = data.counterstandOfInflowAtStart;

            let cumulativeInflowData = [];
            let cumulativeValue = counterstandOfInflowAtStart;
            inflowData.forEach(volume => {
                cumulativeValue += volume;
                cumulativeInflowData.push(cumulativeValue);
            });

            const inflowChartData = {
                labels: timeLabels,
                datasets: [{
                    label: 'Inflow (Cumulative)',
                    data: cumulativeInflowData,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    showLine: true
                }]
            };

            const outflowChartData = {
                labels: timeLabels,
                datasets: [{
                    label: 'Outflow',
                    data: outflowData,
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            };

            new Chart(inflowCtx, {
                type: 'line',
                data: inflowChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { type: 'category' },
                        y: { beginAtZero: false }
                    }
                }
            });

            new Chart(outflowCtx, {
                type: 'bar',
                data: outflowChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { type: 'category' },
                        y: { beginAtZero: true }
                    }
                }
            });

            new Swiper('.swiper-container', {
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                slidesPerView: 1,
                spaceBetween: 0,
            });
        })
        .catch(error => {
            loader.style.display = "none";
            console.error('Error fetching data:', error);
        });
});
