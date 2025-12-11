
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers import orgs, admin

app = FastAPI(title="Organization Management Service")

app.include_router(orgs.router)
app.include_router(admin.router)


def custom_openapi():
    """
    Add a Bearer (JWT) security scheme to the generated OpenAPI schema so
    Swagger UI shows the 'Authorize' button.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="0.1.0",
        description="Multi-tenant organization service",
        routes=app.routes,
    )

    
    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter: **Bearer &lt;token>**",
    }


    openapi_schema.setdefault("security", [])
    openapi_schema["security"].append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
