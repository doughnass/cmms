// Dashboard chart + polling logic for CMMS
(function(){
    function animateCount(el, from, to, duration=600){
        const start = performance.now();
        function frame(now){
            const t = Math.min(1, (now - start)/duration);
            const value = Math.floor(from + (to - from) * t);
            el.textContent = value;
            if(t < 1) requestAnimationFrame(frame);
            else el.textContent = to;
        }
        requestAnimationFrame(frame);
    }

    // Create gradient colors for chart
    function createGradients(ctx) {
        const gradients = [];
        const gradientConfigs = [
            ['#667eea', '#764ba2'], // Pending - purple
            ['#f093fb', '#f5576c'], // In Progress - pink
            ['#11998e', '#38ef7d'], // Completed - green
            ['#fc8181', '#f56565'], // Cancelled - red
            ['#6c757d', '#495057']  // Other - gray
        ];
        gradientConfigs.forEach(([start, end]) => {
            const gradient = ctx.createLinearGradient(0, 0, 0, 200);
            gradient.addColorStop(0, start);
            gradient.addColorStop(1, end);
            gradients.push(gradient);
        });
        return gradients;
    }

    // Update legend with data
    function updateLegend(statusCounts) {
        const legend = document.getElementById('status-legend');
        const total = document.getElementById('chart-total');
        if (!legend) return;

        const items = legend.querySelectorAll('.status-legend-item');
        const keys = Object.keys(statusCounts);
        const values = Object.values(statusCounts).map(v => Number(v || 0));
        const sum = values.reduce((a, b) => a + b, 0);

        // Update total
        if (total) {
            const oldVal = parseInt(total.textContent) || 0;
            if (sum !== oldVal) animateCount(total, oldVal, sum);
        }

        items.forEach((item, idx) => {
            const countEl = item.querySelector('.status-legend-count');
            const percentEl = item.querySelector('.status-legend-percent');
            const value = values[idx] || 0;
            const percent = sum > 0 ? Math.round((value / sum) * 100) : 0;

            if (countEl) {
                const oldVal = parseInt(countEl.textContent) || 0;
                if (value !== oldVal) animateCount(countEl, oldVal, value);
            }
            if (percentEl) {
                percentEl.textContent = percent + '%';
            }
        });
    }

    function buildChartFromCounts(id, statusCounts){
        const el = document.getElementById(id);
        if(!el) return null;
        
        const ctx = el.getContext('2d');
        const labels = Object.keys(statusCounts);
        const data = Object.values(statusCounts).map(v=>Number(v||0));
        const gradients = createGradients(ctx);

        // Update legend
        updateLegend(statusCounts);

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: { 
                labels: labels, 
                datasets: [{ 
                    data: data, 
                    backgroundColor: gradients,
                    borderWidth: 0,
                    hoverOffset: 8,
                    spacing: 2
                }] 
            },
            options: { 
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(26, 26, 46, 0.9)',
                        titleFont: { size: 13, weight: '600' },
                        bodyFont: { size: 12 },
                        padding: 12,
                        cornerRadius: 10,
                        displayColors: true,
                        boxWidth: 10,
                        boxHeight: 10,
                        boxPadding: 4
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 800,
                    easing: 'easeOutQuart'
                },
                onHover: (event, elements) => {
                    el.style.cursor = elements.length ? 'pointer' : 'default';
                }
            }
        });
        return chart;
    }

    async function fetchStats(endpoint){
        try{
            const res = await fetch(endpoint, { credentials: 'same-origin' });
            if(!res.ok) return null;
            return await res.json();
        }catch(e){ console.warn('fetchStats error', e); return null; }
    }

    function updateCardsFromStats(stats){
        for(const key in stats){
            if(key === 'status_counts') continue;
            const selector = `[data-stat="${key}"]`;
            const card = document.querySelector(selector);
            if(!card) continue;
            const h3 = card.querySelector('h3');
            if(!h3) continue;
            const newVal = Number(stats[key] ?? 0);
            const oldVal = Number(h3.textContent.replace(/[^0-9]/g,'')) || 0;
            if(newVal !== oldVal) animateCount(h3, oldVal, newVal);
        }
    }

    // initialization on DOM ready
    document.addEventListener('DOMContentLoaded', async function(){
        const endpointEl = document.querySelector('[data-dashboard-endpoint]');
        const endpoint = endpointEl ? endpointEl.getAttribute('data-dashboard-endpoint') : '/api/dashboard_stats/';

        // try to read initial status from template-injected JSON if present
        let initialStatus = {};
        try{
            const el = document.getElementById('status_counts_json');
            if(el) initialStatus = JSON.parse(el.textContent || el.innerText) || {};
        }catch(e){ initialStatus = {}; }

        // build chart
        window.woStatusChart = buildChartFromCounts('woStatusChart', initialStatus);

        // initial update from server
        const stats = await fetchStats(endpoint);
        if(stats){
            updateCardsFromStats(stats);
            if(stats.status_counts && window.woStatusChart){
                window.woStatusChart.data.labels = Object.keys(stats.status_counts);
                window.woStatusChart.data.datasets[0].data = Object.values(stats.status_counts);
                window.woStatusChart.update();
                updateLegend(stats.status_counts);
            }
        }

        // periodic polling
        setInterval(async ()=>{
            const s = await fetchStats(endpoint);
            if(!s) return;
            updateCardsFromStats(s);
            if(s.status_counts && window.woStatusChart){
                window.woStatusChart.data.labels = Object.keys(s.status_counts);
                window.woStatusChart.data.datasets[0].data = Object.values(s.status_counts);
                window.woStatusChart.update();
                updateLegend(s.status_counts);
            }
        }, 30000);

        // Add hover interaction for legend items
        const legendItems = document.querySelectorAll('.status-legend-item');
        legendItems.forEach((item, idx) => {
            item.addEventListener('mouseenter', () => {
                if (window.woStatusChart) {
                    window.woStatusChart.setActiveElements([{datasetIndex: 0, index: idx}]);
                    window.woStatusChart.update();
                }
            });
            item.addEventListener('mouseleave', () => {
                if (window.woStatusChart) {
                    window.woStatusChart.setActiveElements([]);
                    window.woStatusChart.update();
                }
            });
        });
    });
})();
