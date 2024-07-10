import re
import json
import requests
from http.server import BaseHTTPRequestHandler

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

        if self.path.startswith('/pnr'):
            pnr = self.path.split('/')[-1]
            if self.is_valid_pnr(pnr):
                status = get_pnr_status(pnr)
                if status:
                    self.wfile.write(json.dumps(status).encode('utf-8'))
                else:
                    self.wfile.write(json.dumps({"error": "Failed to fetch PNR status"}).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({"error": "Invalid PNR format"}).encode('utf-8'))
        else:
            self.wfile.write(json.dumps({"error": "Invalid endpoint"}).encode('utf-8'))

    def is_valid_pnr(self, pnr):
        # Check if PNR is a 10-digit number
        return bool(re.match(r'^\d{10}$', pnr))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        pnr = post_data.strip()

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.is_valid_pnr(pnr):
            status = get_pnr_status(pnr)
            if status:
                self.wfile.write(json.dumps(status).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({"error": "Failed to fetch PNR status"}).encode('utf-8'))
        else:
            self.wfile.write(json.dumps({"error": "Invalid PNR format"}).encode('utf-8'))

if __name__ == '__main__':
    from http.server import HTTPServer
    server_address = ('', 8000)  # You can change the port number if needed
    httpd = HTTPServer(server_address, handler)
    print('Starting httpd server...')
    httpd.serve_forever()
