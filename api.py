import httpx

resp = httpx.get("http://localhost:8000/data")
resp2 = httpx.get("http://localhost:8000/history")
print(resp.json())
# print(resp2.json())