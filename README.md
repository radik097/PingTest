# PingTest

Simple tools for monitoring internet speed and ping. Run `monitor.py` to collect data into `pingtest.db` and `web.py` to view graphs.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Collect data for an hour (tests every minute):
   ```bash
   python monitor.py 3600 --interval 60
   ```
3. Start web server and open `http://localhost:8000` in browser:
   ```bash
   python web.py
   ```
