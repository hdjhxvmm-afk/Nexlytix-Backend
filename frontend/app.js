const API = 'http://localhost:8000'
const KEY = 'nx-prod-key-2026'
const POLL = 5000

let activeDevice = 'VemCore-01'
let charts = {}
let pollTimer = null


// ── API ──────────────────────────────────────────────────────────────────────

async function fetchTelemetry(deviceId) {
    const res = await fetch(`${API}/api/telemetry/${deviceId}`, {
        headers: { 'X-API-Key': KEY }
    })
    if (!res.ok) throw new Error(`${res.status}`)
    return res.json()
}


// ── Charts ───────────────────────────────────────────────────────────────────

const chartCfg = (label, color) => ({
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label,
            data: [],
            borderColor: color,
            backgroundColor: color + '15',
            borderWidth: 2,
            pointRadius: 3,
            pointBackgroundColor: color,
            tension: 0.4,
            fill: true,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 400 },
        plugins: { legend: { display: false } },
        scales: {
            x: { ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 6 }, grid: { color: 'rgba(255,255,255,0.04)' } },
            y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
        }
    }
})

function initCharts() {
    const accent = '#00c2ff'
    const green = '#22c55e'
    const violet = '#a78bfa'

    if (charts.temp) { charts.temp.destroy(); charts.hum.destroy(); charts.vib.destroy() }

    charts.temp = new Chart(document.getElementById('chart-temp'), chartCfg('°C', accent))
    charts.hum = new Chart(document.getElementById('chart-hum'), chartCfg('%', green))
    charts.vib = new Chart(document.getElementById('chart-vib'), chartCfg('m/s²', violet))
}

function updateCharts(readings) {
    // readings newest-first, reverse for chart
    const data = [...readings].reverse()
    const labels = data.map(r => {
        const d = new Date(r.time)
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    })

    const set = (chart, vals) => {
        chart.data.labels = labels
        chart.data.datasets[0].data = vals
        chart.update('none')
    }

    set(charts.temp, data.map(r => r.temp_c))
    set(charts.hum, data.map(r => r.humidity_pct))
    set(charts.vib, data.map(r => r.vibration_rms))
}


// ── KPI cards ────────────────────────────────────────────────────────────────

function updateKPIs(r) {
    // temp
    const tempPct = Math.min(100, Math.max(0, ((r.temp_c + 5) / 65) * 100))
    document.getElementById('val-temp').textContent = r.temp_c.toFixed(1)
    const barTemp = document.getElementById('bar-temp')
    barTemp.style.width = tempPct + '%'
    barTemp.className = 'kpi-fill' + (r.temp_c > 55 ? ' error' : r.temp_c > 45 ? ' warn' : '')

    // humidity
    document.getElementById('val-hum').textContent = r.humidity_pct.toFixed(1)
    document.getElementById('bar-hum').style.width = r.humidity_pct + '%'

    // vibration (0-2 scale)
    const vibPct = Math.min(100, (r.vibration_rms / 2) * 100)
    document.getElementById('val-vib').textContent = r.vibration_rms.toFixed(3)
    const barVib = document.getElementById('bar-vib')
    barVib.style.width = vibPct + '%'
    barVib.className = 'kpi-fill' + (r.vibration_rms > 1.8 ? ' error' : r.vibration_rms > 1.2 ? ' warn' : '')

    // status
    const s = document.getElementById('val-status')
    s.textContent = r.status
    s.className = `status-badge ${r.status}`

    // seq
    document.getElementById('val-seq').textContent = '#' + r.seq
}


// ── Table ────────────────────────────────────────────────────────────────────

function formatTime(iso) {
    return new Date(iso).toLocaleString([], {
        month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    })
}

function updateTable(readings) {
    const tbody = document.getElementById('readings-tbody')
    tbody.innerHTML = readings.map(r => `
    <tr>
      <td>${formatTime(r.time)}</td>
      <td>${r.temp_c.toFixed(2)}</td>
      <td>${r.humidity_pct.toFixed(2)}</td>
      <td>${r.vibration_rms.toFixed(4)}</td>
      <td>${r.seq}</td>
      <td><span class="badge ${r.status}">${r.status}</span></td>
    </tr>
  `).join('')
}


// ── Main update ──────────────────────────────────────────────────────────────

async function update() {
    try {
        const res = await fetchTelemetry(activeDevice)

        document.getElementById('record-count').textContent = `${res.count} records`
        document.getElementById('last-update').textContent =
            'Updated ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

        if (res.data?.length) {
            updateKPIs(res.data[0])
            updateCharts(res.data)
            updateTable(res.data)
        }
    } catch (e) {
        showToast(`Failed to fetch ${activeDevice}: ${e.message}`)
    }
}


// ── Toast ────────────────────────────────────────────────────────────────────

let toastTimer = null
function showToast(msg) {
    const t = document.getElementById('toast')
    t.textContent = msg
    t.classList.add('show')
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => t.classList.remove('show'), 4000)
}


// ── Init ─────────────────────────────────────────────────────────────────────

function startPolling() {
    clearInterval(pollTimer)
    update()
    pollTimer = setInterval(update, POLL)
}

function switchDevice(id) {
    document.querySelectorAll('.device-btn').forEach(b => b.classList.remove('active'))
    document.querySelector(`[data-id="${id}"]`).classList.add('active')
    activeDevice = id
    initCharts()
    startPolling()
}

document.querySelectorAll('.device-btn').forEach(btn => {
    btn.addEventListener('click', () => switchDevice(btn.dataset.id))
})

document.getElementById('refresh-btn').addEventListener('click', update)

// kick off
initCharts()
startPolling()
