import requests

class BecknAPIClient:
    """Wrapper around POST calls with printing + safety."""

    def __init__(self, base_url):
        self.base_url = base_url

    def post(self, endpoint, payload):
        url = self.base_url + endpoint
        
        response = requests.post(url, json=payload)
        print("STATUS:", response.status_code)

        try:
            print(response.json())
            return response.json()
        except Exception:
            return response.text
