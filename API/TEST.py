import requests
response = requests.get("http://127.0.0.1:8001/ping")
print(response.status_code, response.text)
