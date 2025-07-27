import requests

response = requests.post(
    "http://127.0.0.1:8000/api/suggest",
    json={"query": "I need a toggle button"}
)

print(response.json())
