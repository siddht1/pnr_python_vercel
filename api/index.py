from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import re
import requests

PNR_BASE_URL = 'https://www.confirmtkt.com/pnr-status'

def get_pnr_status(pnr):
    url = f"{PNR_BASE_URL}/{pnr}"
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
        pattern = r'data\s*=\s*({.*?;)'
        match = re.search(pattern, html_content, re.DOTALL)

        if match:
            json_data = match.group(1).replace(';', '')

            try:
                parsed_data = json.loads(json_data)
                return parsed_data
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                return None
        else:
            print("No JSON data found on the webpage.")
            return None
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        pnr = query_params.get('pnr', [None])[0]

        if pnr and self.is_valid_pnr(pnr):
            status = get_pnr_status(pnr)
            if status:
                self.wfile.write(json.dumps(status).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({"error": "Failed to fetch PNR status"}).encode('utf-8'))
        else:
            self.wfile.write(json.dumps({"error": "Invalid or missing PNR number"}).encode('utf-8'))

    def is_valid_pnr(self, pnr):
        return bool(re.match(r'^\d{10}$', pnr))

