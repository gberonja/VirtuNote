from fastapi import FastAPI
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from app.models import Note
from app.routes import notes
from app.routes import users

class OAuth2PasswordBearerWithScopes(OAuth2):
    """Custom OAuth2PasswordBearer to support Bearer token in Swagger UI."""
    def __init__(self, tokenUrl: str):
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl})
        super().__init__(flows=flows)

# Inicijalizacija aplikacije
app = FastAPI(
    title="VirtuNote API",
    description="API za pohranu i razmjenu notnih zapisa",
    version="1.0.0"
)

# Dodavanje root i status ruta
@app.get("/")
def read_root():
    return {"message": "Welcome to VirtuNote API!"}

@app.get("/status")
def read_status():
    return {"status": "API is running!"}

# Dodavanje ruta iz notes i users modula
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# Swagger OAuth2 konfiguracija
@app.get("/openapi.json")
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = app.openapi()
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/users/login",
                    "scopes": {}
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema
