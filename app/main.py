from fastapi import FastAPI
from routers import users, notes

app = FastAPI(
    title="VirtuNote",
    description="Aplikacija za pohranu i razmjenu notnih zapisa.",
    version="1.0.0"
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])