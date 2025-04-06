/**
 * Financial Charts Library
 * Provides helper functions for creating financial charts.
 */

/**
 * Create a price chart with optional indicators
 * @param {string} elementId - Canvas element ID
 * @param {array} marketData - Array of market data objects
 * @param {string} symbol - Stock symbol
 * @param {object} options - Additional chart options
 */
function createPriceChart(elementId, marketData, symbol, options = {}) {
    if (!marketData || !marketData.length) {
        console.error('No market data provided for price chart');
        return;
    }
    
    // Format dates for display
    const dates = marketData.map(d => {
        const date = new Date(d.timestamp);
        return date.toLocaleDateString();
    });
    
    // Extract price data
    const prices = marketData.map(d => d.close);
    
    // Get canvas context
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: `${symbol} Price`,
                data: prices,
                backgroundColor: options.backgroundColor || 'rgba(54, 162, 235, 0.2)',
                borderColor: options.borderColor || 'rgba(54, 162, 235, 1)',
                borderWidth: options.borderWidth || 2,
                tension: options.tension || 0.1,
                pointRadius: options.pointRadius || 1,
                pointHoverRadius: options.pointHoverRadius || 5,
                yAxisID: 'y'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: options.title || `${symbol} Price History`
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: false
                }
            }
        }
    });
    
    return chart;
}

/**
 * Create an RSI chart
 * @param {string} elementId - Canvas element ID
 * @param {array} rsiData - Array of RSI data objects
 * @param {array} dates - Array of date labels
 * @param {object} options - Additional chart options
 */
function createRSIChart(elementId, rsiData, dates, options = {}) {
    if (!rsiData || !rsiData.length) {
        console.error('No RSI data provided for chart');
        return;
    }
    
    // Extract RSI values
    const rsiValues = rsiData.map(d => d.value);
    
    // Use provided dates or extract from RSI data
    const chartDates = dates || rsiData.map(d => {
        const date = new Date(d.timestamp);
        return date.toLocaleDateString();
    });
    
    // Get canvas context
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartDates.slice(-rsiValues.length),
            datasets: [{
                label: 'RSI',
                data: rsiValues,
                backgroundColor: options.backgroundColor || 'rgba(255, 99, 132, 0.2)',
                borderColor: options.borderColor || 'rgba(255, 99, 132, 1)',
                borderWidth: options.borderWidth || 2,
                tension: options.tension || 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: options.title || 'Relative Strength Index (RSI)'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 10
                    }
                }
            }
        }
    });
    
    // Add horizontal lines for overbought/oversold levels
    const overboughtLevel = options.overboughtLevel || 70;
    const oversoldLevel = options.oversoldLevel || 30;
    
    chart.options.plugins.annotation = {
        annotations: {
            overbought: {
                type: 'line',
                yMin: overboughtLevel,
                yMax: overboughtLevel,
                borderColor: 'rgba(255, 99, 132, 0.7)',
                borderWidth: 1,
                borderDash: [5, 5],
                label: {
                    content: 'Overbought',
                    enabled: true,
                    position: 'left'
                }
            },
            oversold: {
                type: 'line',
                yMin: oversoldLevel,
                yMax: oversoldLevel,
                borderColor: 'rgba(75, 192, 192, 0.7)',
                borderWidth: 1,
                borderDash: [5, 5],
                label: {
                    content: 'Oversold',
                    enabled: true,
                    position: 'left'
                }
            },
            midline: {
                type: 'line',
                yMin: 50,
                yMax: 50,
                borderColor: 'rgba(128, 128, 128, 0.3)',
                borderWidth: 1,
                borderDash: [2, 2]
            }
        }
    };
    
    chart.update();
    return chart;
}

/**
 * Create a MACD chart
 * @param {string} elementId - Canvas element ID
 * @param {array} macdData - Array of MACD data objects
 * @param {array} dates - Array of date labels
 * @param {object} options - Additional chart options
 */
function createMACDChart(elementId, macdData, dates, options = {}) {
    if (!macdData || !macdData.length) {
        console.error('No MACD data provided for chart');
        return;
    }
    
    // Extract MACD values
    const macdLine = macdData.map(d => d.value);
    const signalLine = macdData.map(d => d.signal);
    const histogram = macdData.map(d => d.histogram);
    
    // Use provided dates or extract from MACD data
    const chartDates = dates || macdData.map(d => {
        const date = new Date(d.timestamp);
        return date.toLocaleDateString();
    });
    
    // Get canvas context
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartDates.slice(-macdLine.length),
            datasets: [
                {
                    label: 'MACD',
                    data: macdLine,
                    borderColor: options.macdColor || 'rgba(54, 162, 235, 1)',
                    borderWidth: options.borderWidth || 2,
                    tension: options.tension || 0.1,
                    pointRadius: 0,
                    fill: false,
                    order: 1
                },
                {
                    label: 'Signal Line',
                    data: signalLine,
                    borderColor: options.signalColor || 'rgba(255, 99, 132, 1)',
                    borderWidth: options.borderWidth || 2,
                    tension: options.tension || 0.1,
                    pointRadius: 0,
                    fill: false,
                    order: 0
                },
                {
                    label: 'Histogram',
                    data: histogram,
                    type: 'bar',
                    backgroundColor: histogram.map(v => v >= 0 ? 'rgba(75, 192, 192, 0.5)' : 'rgba(255, 99, 132, 0.5)'),
                    borderColor: histogram.map(v => v >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)'),
                    borderWidth: 1,
                    order: 2
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: options.title || 'MACD'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
    
    return chart;
}

/**
 * Create a Bollinger Bands chart
 * @param {string} elementId - Canvas element ID
 * @param {array} bbandsData - Array of Bollinger Bands data objects
 * @param {array} marketData - Array of market data objects
 * @param {array} dates - Array of date labels
 * @param {object} options - Additional chart options
 */
function createBollingerBandsChart(elementId, bbandsData, marketData, dates, options = {}) {
    if (!bbandsData || !bbandsData.length) {
        console.error('No Bollinger Bands data provided for chart');
        return;
    }
    
    // Extract Bollinger Bands values
    const upperBand = bbandsData.map(d => d.upper);
    const middleBand = bbandsData.map(d => d.middle);
    const lowerBand = bbandsData.map(d => d.lower);
    
    // Use provided dates or extract from data
    const chartDates = dates || bbandsData.map(d => {
        const date = new Date(d.timestamp);
        return date.toLocaleDateString();
    });
    
    // Extract price data if available
    let priceData = [];
    if (marketData && marketData.length) {
        priceData = marketData.map(d => d.close).slice(-upperBand.length);
    }
    
    // Get canvas context
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Prepare datasets
    const datasets = [
        {
            label: 'Upper Band',
            data: upperBand,
            borderColor: options.upperColor || 'rgba(255, 99, 132, 1)',
            backgroundColor: 'transparent',
            borderWidth: options.borderWidth || 2,
            borderDash: [5, 5],
            tension: options.tension || 0.1,
            pointRadius: 0,
            fill: false
        },
        {
            label: 'Middle Band (SMA)',
            data: middleBand,
            borderColor: options.middleColor || 'rgba(54, 162, 235, 1)',
            backgroundColor: 'transparent',
            borderWidth: options.borderWidth || 2,
            tension: options.tension || 0.1,
            pointRadius: 0,
            fill: false
        },
        {
            label: 'Lower Band',
            data: lowerBand,
            borderColor: options.lowerColor || 'rgba(75, 192, 192, 1)',
            backgroundColor: 'transparent',
            borderWidth: options.borderWidth || 2,
            borderDash: [5, 5],
            tension: options.tension || 0.1,
            pointRadius: 0,
            fill: false
        }
    ];
    
    // Add price data if available
    if (priceData.length) {
        datasets.push({
            label: 'Price',
            data: priceData,
            borderColor: options.priceColor || 'rgba(255, 159, 64, 1)',
            backgroundColor: 'transparent',
            borderWidth: options.priceBorderWidth || 2,
            tension: options.tension || 0.1,
            pointRadius: 0,
            fill: false
        });
    }
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartDates.slice(-upperBand.length),
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: options.title || 'Bollinger Bands'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
    
    return chart;
}

/**
 * Create a sentiment analysis chart
 * @param {string} elementId - Canvas element ID
 * @param {array} sentimentData - Array of sentiment data objects
 * @param {object} options - Additional chart options
 */
function createSentimentChart(elementId, sentimentData, options = {}) {
    if (!sentimentData || !sentimentData.length) {
        console.error('No sentiment data provided for chart');
        return;
    }
    
    // Extract sentiment scores and labels
    const scores = sentimentData.map(d => d.sentiment_score);
    const labels = sentimentData.map((d, i) => options.labels ? options.labels[i] : `Article ${i+1}`);
    
    // Create colors based on sentiment
    const colors = scores.map(score => {
        if (score >= 0.05) return options.positiveColor || 'rgba(75, 192, 192, 0.7)';
        if (score <= -0.05) return options.negativeColor || 'rgba(255, 99, 132, 0.7)';
        return options.neutralColor || 'rgba(201, 203, 207, 0.7)';
    });
    
    // Get canvas context
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Create chart
    const chart = new Chart(ctx, {
        type: options.type || 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Sentiment Score',
                data: scores,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: options.title || 'Sentiment Analysis'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const score = context.raw;
                            let label = `Score: ${score.toFixed(2)}`;
                            if (score >= 0.05) label += ' (Positive)';
                            else if (score <= -0.05) label += ' (Negative)';
                            else label += ' (Neutral)';
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: -1,
                    max: 1,
                    ticks: {
                        stepSize: 0.5
                    }
                }
            }
        }
    });
    
    // Add zero line
    chart.options.plugins.annotation = {
        annotations: {
            zeroLine: {
                type: 'line',
                yMin: 0,
                yMax: 0,
                borderColor: 'rgba(128, 128, 128, 0.5)',
                borderWidth: 1,
                borderDash: [2, 2]
            }
        }
    };
    
    chart.update();
    return chart;
}

/**
 * Create a multi-symbol comparison chart
 * @param {string} elementId - Canvas element ID
 * @param {object} symbolsData - Object with symbol keys and array values
 * @param {object} options - Additional chart options
 */
function createComparisonChart(elementId, symbolsData, options = {}) {
    if (!symbolsData || Object.keys(symbolsData).length === 0) {
        console.error('No data provided for comparison chart');
        return;
    }
    
    // Find common date range
    let commonDates = [];
    const colors = [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 205, 86, 1)',
        'rgba(201, 203, 207, 1)'
    ];
    
    // Initialize datasets
    const datasets = [];
    let colorIndex = 0;
    
    // Create dataset for each symbol
    for (const [symbol, data] of Object.entries(symbolsData)) {
        if (!data || !data.length) continue;
        
        // Normalize data to percentage change
        const firstPrice = data[0].close;
        const normalizedData = data.map(d => ((d.close / firstPrice) - 1) * 100);
        
        // Extract dates for this symbol
        const dates = data.map(d => {
            const date = new Date(d.timestamp);
            return date.toLocaleDateString();
        });
        
        // Use first symbol's dates as common dates
        if (commonDates.length === 0) {
            commonDates = dates;
        }
        
        // Add dataset for this symbol
        datasets.push({
            label: symbol,
            data: normalizedData,
            backgroundColor: 'transparent',
            borderColor: colors[colorIndex % colors.length],
            borderWidth: 2,
            tension: 0.1,
            pointRadius: 0,
            fill: false
        });
        
        colorIndex++;
    }
    
    // Get canvas context
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: commonDates,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: options.title || 'Percentage Change Comparison'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Percentage Change (%)'
                    }
                }
            }
        }
    });
    
    // Add zero line
    chart.options.plugins.annotation = {
        annotations: {
            zeroLine: {
                type: 'line',
                yMin: 0,
                yMax: 0,
                borderColor: 'rgba(128, 128, 128, 0.5)',
                borderWidth: 1,
                borderDash: [2, 2]
            }
        }
    };
    
    chart.update();
    return chart;
}
