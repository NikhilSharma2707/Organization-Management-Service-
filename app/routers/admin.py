from fastapi import APIRouter, HTTPException
from ..models import AdminLogin
from ..crud import admin_login
from ..auth import create_access_token

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/login")
async def admin_login_route(payload: AdminLogin):
    res = await admin_login(payload.email, payload.password)
    if not res:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    admin = res["admin"]
    org = res["org"]
    token = create_access_token({"admin_id": str(admin["_id"]), "org_id": str(org["_id"]), "org_name": org["organization_name"]})
    return {"access_token": token, "token_type": "bearer"}
