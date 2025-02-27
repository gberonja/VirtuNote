from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.users import router as users_router

app = FastAPI(
    title="UserAPI",
    description="User Management API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/users", tags=["Users"])


@app.get("/")
def read_root():
    return {"message": "UserAPI service is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
