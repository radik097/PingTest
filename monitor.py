import argparse
import sqlite3
import time
from pythonping import ping
import speedtest

DB_PATH = 'pingtest.db'
SERVER_ID = 64665  # Oldenburg, Germany


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL,
            ping_ms REAL,
            download_mbps REAL,
            upload_mbps REAL,
            router_ping_ms REAL,
            jitter_ms REAL
        )"""
    )
    conn.commit()
    conn.close()


def measure(server_id=SERVER_ID, router_ip='192.168.1.1'):
    st = speedtest.Speedtest()
    st.get_servers([server_id])
    st.get_best_server()
    st.download()
    st.upload()
    results = st.results.dict()
    ping_ms = results['ping']
    download_mbps = results['download'] / 1e6
    upload_mbps = results['upload'] / 1e6

    resp = ping(router_ip, count=5, timeout=2)
    router_ping_ms = resp.rtt_avg_ms
    jitter_ms = resp.rtt_max_ms - resp.rtt_min_ms

    return ping_ms, download_mbps, upload_mbps, router_ping_ms, jitter_ms


def monitor(duration_sec, interval_sec=60):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    start = time.time()
    while time.time() - start < duration_sec:
        ts = time.time()
        try:
            ping_ms, dl, ul, router_ping, jitter = measure()
        except Exception as e:
            print('measurement error:', e)
            ping_ms = dl = ul = router_ping = jitter = None
        cur.execute(
            'INSERT INTO results (ts, ping_ms, download_mbps, upload_mbps, router_ping_ms, jitter_ms) VALUES (?, ?, ?, ?, ?, ?)',
            (ts, ping_ms, dl, ul, router_ping, jitter),
        )
        conn.commit()
        remaining = start + duration_sec - time.time()
        if remaining <= 0:
            break
        time.sleep(min(interval_sec, remaining))
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor network quality')
    parser.add_argument('duration', type=int, help='monitoring duration in seconds')
    parser.add_argument('--interval', type=int, default=60, help='interval between tests in seconds')
    args = parser.parse_args()
    monitor(args.duration, args.interval)
