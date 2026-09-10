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

    function buildChartFromCounts(id, statusCounts){
        const el = document.getElementById(id);
        if(!el) return null;
        const labels = Object.keys(statusCounts);
        const data = Object.values(statusCounts).map(v=>Number(v||0));
        const colors = ['#17a2b8', '#ffc107', '#28a745', '#dc3545', '#6c757d'];
        const chart = new Chart(el.getContext('2d'), {
            type: 'doughnut',
            data: { labels: labels, datasets: [{ data: data, backgroundColor: colors }] },
            options: { maintainAspectRatio: false }
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
            }
        }, 30000);
    });
})();
