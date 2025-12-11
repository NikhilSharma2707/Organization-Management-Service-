# Organization Management Service Backend 

## Project overview
I have developed a FastAPI backend that implements a simple multi tenant **Organization Management Service**.
We can do the following operations 
- Creating an organization (creates admin user + a tenant collection `org_<name>`).  
- Getting organization metadata from a master database.  
- Updating an organization (rename + migrate tenant collection).  
- Deleting an organization (authorized admin only — removes metadata and the tenant collection).  
- Admin login that returns a JWT for subsequent protected operations.

## Why I built it this way
- The assignment required a master database plus dynamic collections per organization — I followed that strictly.
- I used FastAPI because it’s quick to develop, simple to test, and includes built-in OpenAPI docs which are helpful for reviewers.
- I used MongoDB because the tenant data schema can be flexible, and dynamic collection creation is straightforward.
- I used JWT for stateless authentication so the API can be horizontally scaled (multiple app instances) without session storage.

## How to run (using Docker) 
I recommend using Docker but it can done locally too.
1. Build images and start containers:
```bash
docker-compose build --no-cache app
docker-compose up -d
```
2. Check logs and ensure the app is started:
```bash
docker-compose logs -f app
```
3. Open the API docs in the browser:
```bash
http://localhost:8000/docs
```
## How to run locally (venv):-
1. Create & activate venv:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set environment variables
```bash
MONGO_URL=mongodb://localhost:27017
JWT_SECRET=JWT TOKEN
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
4. Start MongoDB locally (or point MONGO_URL to running instance):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API documentation & examples

Base URL: http://localhost:8000

I used FastAPI’s Pydantic models so requests are validated. Swagger UI is available at /docs. Below are core endpoints and example flows.

1) Create Organization

POST /org/create

Body:
```bash
{
  "organization_name": "TestOrg",
  "email": "admin@testorg.com",
  "password": "Test1234"
}

```

What happens

It validates the organization_name uniqueness.

Creates the collection org_testorg (sanitized name).

Creates the admin user in master_db.admins (password hashed).

Stores the metadata in master_db.organizations.
Success Response (200):

``` bash
{
  "organization_name": "TestOrg",
  "collection_name": "org_testorg",
  "admin_email": "admin@testorg.com"
}
```

2) Admin Login

POST /admin/login

Body:
```bash

{ "email": "admin@testorg.com", "password": "Test1234" }
```

What happens

It verifies the password against stored hash.

Issue JWT with claims:
admin_id, org_id, org_name, exp.

Response
```bash

{ "access_token": "<JWT>", "token_type": "bearer" }

```
3) Delete Organization

DELETE /org/delete?organization_name=TestOrg

Headers:
```bash
Authorization: Bearer <access_token>
x-admin-email: admin@testorg.com
```

What happens

It validates the token & admin identity.

Confirms that the admin belongs to the organization.

Drops org_testorg collection.

And removes master_db.organizations and master_db.admins entries related to the org.

Response
```bash
{ "detail": "deleted" }
```
4) Update Organization (rename)

PUT /org/update example

body:
```bash
{
  "organization_name": "TestOrg",
  "new_organization_name": "TestOrgNew",
  "email": "admin@testorg.com",
  "password": "Test1234"
}
```

# What I implemented

- Validate uniqueness of new_organization_name.

- Programmatically create org_testorgnew.

- Copy data from old tenant collection to the new one if data migration is implemented.

- Update master_db.organizations entry.

- Authentication details (how tokens & hashing work)

- Passwords are hashed using passlib with pbkdf2_sha256 to avoid bcrypt wheel issues and bcrypt’s 72-byte truncation limit.

- JWTs are generated using python-jose with HS256 algorithm. The token includes admin_id, org_id, and org_name.

- The token lifetime is configurable via ACCESS_TOKEN_EXPIRE_MINUTES in config.py or environment variables.

- To call protected endpoints in Swagger:

- First call /admin/login, copy the access_token.

- Click Authorize in Swagger and paste Bearer <access_token> (just once, not Bearer Bearer ...).

- Inspecting MongoDB (what I do to verify)

While Docker is running:

# find mongo container name
```bash
docker ps
```
# enter shell
```bash
docker exec -it <mongo_container_name> bash
```

# start mongo shell
```bash
mongosh
```
# inside mongosh
```bash
use master_db
show collections
db.organizations.find().pretty()
db.admins.find().pretty()
db.getCollection("org_testorg").find().pretty()
db.getCollection("org_testorg").countDocuments()
```

If delete worked, db.organizations.findOne({ organization_name: "TestOrg" }) should return null, admins query should return null, and the tenant collection count should be 0 or the collection should not be listed.

# Design decisions, trade-offs and alternatives I could've used:

## Why master DB + per-tenant collection

- It keeps the global metadata (organizations/admins) in one place and isolates tenant data logically.

- It is easier to operate at the collection level (backup single collection).

- Also the assignment asked for dynamic collection creation.

## Trade-offs

- If you have thousands of tenants, MongoDB will host thousands of collections. Each collection has metadata & index overhead which can impact memory and performance.

- Using one Mongo instance is a single point of failure. For production I would use a replica set and/or sharding.

- Per-tenant migrations and schema upgrades need carefully designed scripts.

## Alternatives I considered

- Better for very high tenant counts (less metadata overhead), but less isolation and harder to backup/restore per-tenant data.

- Best isolation & easiest per-tenant backup/migration, but impractical at scale (resource-heavy).

- Small tenants share collections, large tenants get dedicated DBs. This balances scale and isolation.

- If data is highly relational and needs strong ACID across tenants, a relational DB might be preferable.

# Known issues & assumptions

- I sanitize org names to produce collection names, but collisions (e.g., Org-1 vs Org_1) are possible. Better to use org_<uuid> in production.

- No brute-force protection on login; consider rate-limiting and account lockout for production.

- Mongo runs without auth in Docker by default so it is for development convenience only. For production we would have to enable Mongo authentication, TLS, network security.

- I used pbkdf2_sha256 for portability and to avoid bcrypt wheel problems in some CI/containers. Bcrypt is fine when wheels are available.


# What I would improve for production

- Use a Mongo replica set and enable authentication/TLS.

- Introduce a secrets manager for JWT secret and DB credentials.

- Add rate limiting and audit logging.

- Add health checks, graceful shutdown, and CI pipelines with tests.


# Test script & quick verification

I included test_flow.py to automate a quick end-to-end test:

```bash
pip install requests
python test_flow.py
```

It performs:

POST /org/create

POST /admin/login which would retrive the JWT Token

DELETE /org/delete 

You should see 200 responses for each step on a healthy run.

Thankyou for considering this submission
