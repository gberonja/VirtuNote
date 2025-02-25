from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from routes.scores import router as scores_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ScoreAPI",
    description="API za upravljanje notnim zapisima i sinhronizaciju metadata",
    version="1.0.0"
)

# Uključujemo router s globalnim dependencyjem – svi zahtjevi moraju imati token
app.include_router(
    scores_router,
    prefix="/scores",
    tags=["Scores"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://127.0.0.1:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
