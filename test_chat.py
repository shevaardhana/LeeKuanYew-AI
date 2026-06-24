import requests
import json

url = "http://127.0.0.1:8000/api/chat"
payload = {
    "message": "bagaimana reaksi Anda saat pemisahan dengan Malaysia di tahun 1965?",
    "history": []
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
