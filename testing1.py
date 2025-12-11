import base64, json
token = "access-token"
payload = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "==").decode())
print(json.dumps(payload, indent=2))
