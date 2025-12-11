from .db import master_db
from .auth import hash_password, verify_password
from bson.objectid import ObjectId
import re

ORG_COLL = master_db.organizations
ADMIN_COLL = master_db.admins

def _sanitize_name(name: str) -> str:
    
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9_-]+', '_', name)
    return name

async def org_exists(org_name: str) -> bool:
    return await ORG_COLL.find_one({"organization_name": org_name}) is not None

async def create_organization(organization_name: str, email: str, password: str):
    if await org_exists(organization_name):
        raise ValueError("Organization already exists")
    collection_name = f"org_{_sanitize_name(organization_name)}"
    
    admin_doc = {"email": email, "password": hash_password(password)}
    admin_result = await ADMIN_COLL.insert_one(admin_doc)
    org_doc = {
        "organization_name": organization_name,
        "collection_name": collection_name,
        "admin_id": admin_result.inserted_id,
        "created_at": __import__("datetime").datetime.utcnow()
    }
    org_result = await ORG_COLL.insert_one(org_doc)
    
    await master_db.create_collection(collection_name)
    return {**org_doc, "_id": org_result.inserted_id}

async def get_org_by_name(organization_name: str):
    doc = await ORG_COLL.find_one({"organization_name": organization_name})
    return doc

async def admin_login(email: str, password: str):
    admin = await ADMIN_COLL.find_one({"email": email})
    if not admin:
        return None
    if not verify_password(password, admin["password"]):
        return None
   
    org = await ORG_COLL.find_one({"admin_id": admin["_id"]})
    return {"admin": admin, "org": org}

async def delete_org(organization_name: str, admin_email: str):
    
    org = await ORG_COLL.find_one({"organization_name": organization_name})
    if not org:
        raise ValueError("Org not found")
    admin = await ADMIN_COLL.find_one({"_id": org["admin_id"]})
    if not admin or admin["email"] != admin_email:
        raise PermissionError("Not authorized")
    
    await master_db.drop_collection(org["collection_name"])
    
    await ADMIN_COLL.delete_one({"_id": admin["_id"]})
    await ORG_COLL.delete_one({"_id": org["_id"]})
    return True

async def update_org_name(old_name: str, new_name: str):
    org = await ORG_COLL.find_one({"organization_name": old_name})
    if not org:
        raise ValueError("Org not found")
    if await org_exists(new_name):
        raise ValueError("New organization name already exists")
    new_collection_name = f"org_{_sanitize_name(new_name)}"
   
    
    await master_db.command("renameCollection", f"{master_db.name}.{org['collection_name']}", to=f"{master_db.name}.{new_collection_name}")

    await ORG_COLL.update_one({"_id": org["_id"]}, {"$set": {"organization_name": new_name, "collection_name": new_collection_name}})
    return await ORG_COLL.find_one({"_id": org["_id"]})
