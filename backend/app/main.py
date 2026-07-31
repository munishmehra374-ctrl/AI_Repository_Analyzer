from fastapi import FastAPI
from app.api.repository import router as repository_router

app = FastAPI(
    title="AI Repository Analyzer"
)

app.include_router(repository_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI Repository Analyzer"
    }