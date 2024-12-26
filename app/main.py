from fastapi import FastAPI
from app.models import Note

app = FastAPI(title="VirtuNote API", description="API za pohranu i razmjenu notnih zapisa", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to VirtuNote API!"}

@app.get("/status")
def read_status():
    return {"status": "API is running!"}