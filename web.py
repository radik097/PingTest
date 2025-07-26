from flask import Flask, jsonify, render_template_string
import sqlite3

DB_PATH = 'pingtest.db'

app = Flask(__name__)


def query_results():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT ts, ping_ms, download_mbps, upload_mbps, router_ping_ms, jitter_ms FROM results ORDER BY ts')
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.route('/data')
def data():
    return jsonify(query_results())


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Stats</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="speedChart" width="800" height="400"></canvas>
    <canvas id="pingChart" width="800" height="400"></canvas>
    <script>
    async function draw() {
        const resp = await fetch('/data');
        const data = await resp.json();
        const labels = data.map(r => new Date(r.ts * 1000));
        const dl = data.map(r => r.download_mbps);
        const ul = data.map(r => r.upload_mbps);
        const ping = data.map(r => r.ping_ms);
        const router = data.map(r => r.router_ping_ms);
        const jitter = data.map(r => r.jitter_ms);

        new Chart(document.getElementById('speedChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {label: 'Download Mbps', data: dl, borderColor: 'blue', fill: false},
                    {label: 'Upload Mbps', data: ul, borderColor: 'green', fill: false}
                ]
            },
            options: {scales: {x: {type: 'time', time: {unit: 'minute'}}}}
        });

        new Chart(document.getElementById('pingChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {label: 'Ping ms', data: ping, borderColor: 'red', fill: false},
                    {label: 'Router Ping ms', data: router, borderColor: 'orange', fill: false},
                    {label: 'Jitter ms', data: jitter, borderColor: 'purple', fill: false}
                ]
            },
            options: {scales: {x: {type: 'time', time: {unit: 'minute'}}}}
        });
    }
    draw();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
