import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import analyzer
from routes import analyses
from database import init_db

@asynccontextmanager
async def lifespan(_app):
    init_db()
    yield


app = FastAPI(title="SkillSync AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyzer.router)
app.include_router(analyses.router)


@app.get("/")
def home():
    return {"message": "Backend Running"}
