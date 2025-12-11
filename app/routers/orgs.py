from fastapi import APIRouter, HTTPException, Depends, Header
from ..models import OrgCreate, OrgGet, OrgUpdate, OrgOut
from ..crud import create_organization, get_org_by_name, delete_org, update_org_name
from ..auth import create_access_token
import bson

router = APIRouter(prefix="/org", tags=["org"])

@router.post("/create", response_model=OrgOut)
async def create_org(payload: OrgCreate):
    try:
        doc = await create_organization(payload.organization_name, payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "_id": str(doc["_id"]),
        "organization_name": doc["organization_name"],
        "collection_name": doc["collection_name"],
        "admin_email": payload.email
    }

@router.get("/get", response_model=OrgOut)
async def get_org(organization_name: str):
    doc = await get_org_by_name(organization_name)
    if not doc:
        raise HTTPException(status_code=404, detail="Org not found")
    admin = await __import__("app.crud", fromlist=["ADMIN_COLL"]).ADMIN_COLL.find_one({"_id": doc["admin_id"]})
    return {
        "_id": str(doc["_id"]),
        "organization_name": doc["organization_name"],
        "collection_name": doc["collection_name"],
        "admin_email": admin["email"] if admin else None
    }

@router.put("/update", response_model=OrgOut)
async def update_org(payload: OrgUpdate):
    try:
        updated = await update_org_name(payload.old_organization_name, payload.new_organization_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "_id": str(updated["_id"]),
        "organization_name": updated["organization_name"],
        "collection_name": updated["collection_name"],
        "admin_email": (await __import__("app.crud", fromlist=["ADMIN_COLL"]).ADMIN_COLL.find_one({"_id": updated["admin_id"]}))["email"]
    }

@router.delete("/delete")
async def delete_organization(organization_name: str, x_admin_email: str = Header(...)):
    # require header X-ADMIN-EMAIL to ensure auth (in prod use Authorization JWT)
    try:
        await delete_org(organization_name, x_admin_email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return {"detail":"deleted"}
