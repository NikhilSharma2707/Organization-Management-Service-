import jwt
from datetime import datetime, timedelta

SECRET = "mysecretkey123"  
ALGORITHM = "HS256"

def create_token():
    payload = {
        "admin_id": "12345",
        "org_id": "99999",
        "org_name": "TestOrg",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token

print("Generated JWT:")
print(create_token())
