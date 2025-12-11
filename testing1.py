import base64, json
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZG1pbl9pZCI6IjEyMzQ1Iiwib3JnX2lkIjoiOTk5OTkiLCJvcmdfbmFtZSI6IlRlc3RPcmciLCJleHAiOjE3NjU0NTk4NjZ9.HKTKLRYJWNuzk2vML-kWZ30tA7XPiPZNe1rfXnSODFE"
payload = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "==").decode())
print(json.dumps(payload, indent=2))
