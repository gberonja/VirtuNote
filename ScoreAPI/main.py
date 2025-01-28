from fastapi import FastAPI
from routes.scores import router as scores_router

app = FastAPI(
    title="ScoreAPI",
    description="Servis za upravljanje pohranom notnih zapisa.",
    version="1.0.0"
)

app.include_router(scores_router, prefix="/scores", tags=["Scores"])