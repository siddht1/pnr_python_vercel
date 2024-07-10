# pnr_status.py

import requests
import re
import json
from urllib.parse import urlparse, parse_qs

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

def handler(request):
    if request.method == 'GET':
        query_params = request.query
        pnr = query_params.get('pnr')

        if pnr and is_valid_pnr(pnr):
            status = get_pnr_status(pnr)
            if status:
                return {
                    'statusCode': 200,
                    'body': json.dumps(status)
                }
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Failed to fetch PNR status'})
                }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid or missing PNR number'})
            }
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

def is_valid_pnr(pnr):
    return bool(re.match(r'^\d{10}$', pnr))
