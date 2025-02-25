from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from routes.metadata import router as metadata_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="MetadataAPI",
    description="API za upravljanje metapodacima notnih zapisa",
    version="1.0.0"
)


app.include_router(
    metadata_router,
    prefix="/metadata",
    tags=["Metadata"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
