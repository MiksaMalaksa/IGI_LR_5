function seriesApproximation(x, n_terms) {
    let sum = 0;
    for (let n = 0; n < n_terms; n++) {
        sum += Math.pow(x, n);
    }
    return sum;
}

function prepareData(n_terms) {
    const xValues = [];
    const seriesValues = [];
    const mathValues = [];
    const step = 0.02;
    for (let x = -0.9; x <= 0.9; x += step) {
        x = parseFloat(x.toFixed(2));
        xValues.push(x);
        seriesValues.push(seriesApproximation(x, n_terms));
        mathValues.push(1 / (1 - x));
    }
    return { xValues, seriesValues, mathValues };
}

function createChart(data) {
    const ctx = document.getElementById('myChart').getContext('2d');

    const totalDuration = 4000;
    const delayBetweenPoints = totalDuration / data.seriesValues.length;
    const animation = {
        x: {
            type: 'number',
            easing: 'linear',
            duration: delayBetweenPoints,
            from: NaN, // начальная точка пропускается
            delay(ctx) {
                if (ctx.type !== 'data' || ctx.xStarted) {
                    return 0;
                }
                ctx.xStarted = true;
                return ctx.index * delayBetweenPoints;
            }
        },
        y: {
            type: 'number',
            easing: 'linear',
            duration: delayBetweenPoints,
            from: (ctx) => ctx.index === 0 ? ctx.chart.scales.y.getPixelForValue(0) : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index - 1].getProps(['y'], true).y,
            delay(ctx) {
                if (ctx.type !== 'data' || ctx.yStarted) {
                    return 0;
                }
                ctx.yStarted = true;
                return ctx.index * delayBetweenPoints;
            }
        }
    };
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.xValues,
            datasets: [{
                    label: `Разложение в ряд (n = ${data.seriesValues.length - 1})`,
                    data: data.seriesValues,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Функция 1/(1-x)',
                    data: data.mathValues,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            animation: animation,
            plugins: {
                title: {
                    display: true,
                    text: 'Графики функции и её разложения в ряд',
                    font: {
                        size: 20,
                    }
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'x',
                        font: {
                            size: 14
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'F(x)',
                        font: {
                            size: 14
                        }
                    },
                    beginAtZero: false
                }
            }
        }
    });
    return chart;
}

function saveChart(chart) {
    const link = document.createElement('a');
    link.href = chart.toBase64Image();
    link.download = 'chart.png';
    link.click();
}

function main() {
    const n_terms = 10;
    const data = prepareData(n_terms);
    const chart = createChart(data);
    const saveButton = document.getElementById('saveChart');
    saveButton.addEventListener('click', () => saveChart(chart));
}

window.onload = main;