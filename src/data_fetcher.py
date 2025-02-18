import requests
import re

def generate_url(base_url, shot, nsignal, signals, factors, tstart, tstop):
    """Generates a URL to fetch signal data."""
    tstart = 0 if tstart is None else tstart
    tstop = 2000 if tstop is None else tstop

    url = f"{base_url}?shot={shot}&nsignal={nsignal}"
    for i in range(1, nsignal + 1):
        signal = signals[i - 1] if i - 1 < len(signals) else ""
        factor = factors[i - 1] if i - 1 < len(factors) else "1.00"
        url += f"&signal{i:02}={signal}&fact{i:02}={factor}"
    
    url += f"&tstart={tstart:.2f}&tstop={tstop:.2f}"
    return url

def fetch_data(url):
    """Fetches data from the URL."""
    response = requests.get(url, verify=False)
    return response.text if response.status_code == 200 else None

def extract_data_points(html_content, signals):
    """Extracts data from HTML content."""
    data_points_dict = {}
    matches = list(re.finditer(r"var data(\d{2}) = \[(.*?)\];", html_content, re.DOTALL))
    for signal_name in signals:
        match = next((m for m in matches if f"var data{signals.index(signal_name)+1:02}" in m.group(0)), None)
        if match:
            data_block = match.group(2)
            data_points = [tuple(map(float, line.strip('[]').split(','))) for line in data_block.split('],[')]
            data_points_dict[signal_name] = data_points
    return data_points_dict

