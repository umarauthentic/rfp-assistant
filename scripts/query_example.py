import requests

payload = {
    "query": "What do we usually say about encryption?",
    "use_memory": True,
    "use_documents": True,
}

response = requests.post("http://127.0.0.1:8000/query", json=payload, timeout=180)
print(response.json())
