import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.metadata import router as metadata_router

app = FastAPI(
    title="Metadata API",
    description="API for managing music score metadata",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metadata_router, prefix="/metadata", tags=["metadata"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Metadata API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
