const ALGO_ORDER = ["Dijkstra", "Bellman-Ford", "Floyd-Warshall", "Uniform Cost Search", "A*"];

// Chart instances (declared early to avoid hoisting issues)
let costChartInst = null;
let timeChartInst = null;

document.getElementById('btnRunBatch').addEventListener('click', runBatch);
document.getElementById('batchDensity').addEventListener('input', (e) => {
    document.getElementById('batchDensityValue').innerText = e.target.value;
});

// Initialize Table on Load
initTable();

function initTable() {
    const stats = ALGO_ORDER.map(algo => ({
        algorithm: algo,
        success_rate: 0,
        avg_cost: 0,
        avg_nodes: 0,
        avg_time: 0
    }));
    renderTable(stats);
    renderCharts(stats);
}

async function runBatch() {
    const btn = document.getElementById('btnRunBatch');
    const loading = document.getElementById('loading');
    const nodes = document.getElementById('batchNodes').value;
    const density = document.getElementById('batchDensity').value;
    const numGraphs = document.getElementById('numGraphs').value;
    const directed = document.getElementById('batchDirected').checked;

    // Get Selected Algorithms
    const selectedAlgos = Array.from(document.querySelectorAll('#algoCheckboxes input:checked'))
        .map(cb => cb.value);

    if (selectedAlgos.length === 0) {
        alert("Please select at least one algorithm.");
        return;
    }

    btn.disabled = true;
    loading.style.display = 'block';

    try {
        const res = await fetch('/api/batch-run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                num_graphs: parseInt(numGraphs),
                num_nodes: parseInt(nodes),
                density: parseFloat(density),
                directed: directed,
                algorithms: selectedAlgos
            })
        });

        const data = await res.json();
        // Check if data is array or object with stats
        // The backend returns a list of results (list of dicts)
        // BUT charts.js expects {stats: [...]}
        // Wait, the backend currently returns just `sanitize_floats(results)` which is a list.
        // I need to adapt charts.js to handle the list response directly OR update backend.
        // Let's check `visualization.py` again. It returns `results` which is `[ {algo: {stats}}, ... ]`
        // `charts.js` expects `data.stats` which implies backend should return `{"stats": [...]}` OR charts.js logic is wrong for the NEW backend.
        // Actually, the backend I wrote returns `[ { "Dijkstra": {...}, "A*": {...} }, ... ]` (list of maps).
        // `charts.js` expects `renderTable(data.stats)` where stats is array of `{algorithm, avg_cost, ...}`.
        // The logic in charts.js seems to expect pre-aggregated stats?
        // Let's look at `charts.js` again.
        // It sorts by `avg_cost`.
        // My backend returns RAW runs.
        // I need to AGGREGATE strings in the frontend OR backend.
        // The previous backend likely did aggregation.
        // I should probably fix the backend to aggregate, OR do it here. 
        // Doing it here is safer given I can't interactively test backend easily.

        let aggregated = {};
        // data = [{ "Dijkstra": {cost, ...}, "A*":... }, ...]

        if (Array.isArray(data)) {
            data.forEach(run => {
                for (const [algo, stat] of Object.entries(run)) {
                    if (!aggregated[algo]) {
                        aggregated[algo] = {
                            algorithm: algo,
                            total_cost: 0,
                            total_nodes: 0,
                            total_time: 0,
                            success_count: 0,
                            count: 0
                        };
                    }
                    if (stat.success) {
                        aggregated[algo].total_cost += stat.cost;
                        aggregated[algo].total_nodes += stat.visited;
                        aggregated[algo].total_time += stat.time; // ms
                        aggregated[algo].success_count++;
                    }
                    aggregated[algo].count++;
                }
            });

            // Average
            const stats = Object.values(aggregated).map(a => ({
                algorithm: a.algorithm,
                success_rate: a.success_count / a.count,
                avg_cost: a.success_count ? a.total_cost / a.success_count : 0,
                avg_nodes: a.success_count ? a.total_nodes / a.success_count : 0,
                avg_time: (a.success_count ? a.total_time / a.success_count : 0) / 1000 // charts expects seconds based on existing code? No, existing code says `s.avg_time * 1000` to get ms. So it expects seconds. My backend returns ms. So I should divide by 1000 here to match existing format or just pass ms and change charts.js.
                // existing: `s.avg_time * 1000` in renderTable.
                // So if I pass seconds here, it works.
            }));

            renderTable(stats);
            renderCharts(stats);
        } else if (data.stats) {
            // Fallback if backend does aggregation
            renderTable(data.stats);
            renderCharts(data.stats);
        }

    } catch (e) {
        alert("Batch run failed: " + e.message);
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
}

function renderTable(stats) {
    const tbody = document.querySelector('#statsTable tbody');
    tbody.innerHTML = '';

    // Sort by Algorithm Order (using Global ALGO_ORDER)
    stats.sort((a, b) => {
        const idxA = ALGO_ORDER.indexOf(a.algorithm);
        const idxB = ALGO_ORDER.indexOf(b.algorithm);
        // Handle cases where algorithm might not be in the list (fallback to end)
        return (idxA === -1 ? 999 : idxA) - (idxB === -1 ? 999 : idxB);
    });

    stats.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-6 py-3">${s.algorithm}</td>
            <td class="px-6 py-3 text-center">${(s.success_rate * 100).toFixed(0)}%</td>
            <td class="px-6 py-3 text-center">${s.avg_cost.toFixed(2)}</td>
            <td class="px-6 py-3 text-center">${s.avg_nodes.toFixed(2)}</td>
            <td class="px-6 py-3 text-center">${(s.avg_time * 1000).toFixed(2)} ms</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderCharts(stats) {
    const labels = stats.map(s => s.algorithm);
    const costs = stats.map(s => s.avg_cost);
    const times = stats.map(s => s.avg_time * 1000);

    const ctx1 = document.getElementById('costChart');
    if (costChartInst) costChartInst.destroy();

    costChartInst = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Avg Path Cost',
                data: costs,
                backgroundColor: '#FFFF00'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: 'white' } }
            },
            scales: {
                y: { ticks: { color: 'white' } },
                x: { ticks: { color: 'white' } }
            }
        }
    });

    const ctx2 = document.getElementById('timeChart');
    if (timeChartInst) timeChartInst.destroy();

    timeChartInst = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Avg Time (ms)',
                data: times,
                backgroundColor: '#1919A6'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: 'white' } }
            },
            scales: {
                y: { ticks: { color: 'white' } },
                x: { ticks: { color: 'white' } }
            }
        }
    });
}
