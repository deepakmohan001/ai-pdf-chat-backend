import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database.connection import client

load_dotenv()

app = FastAPI()

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "").split(",")
origins = [origin.strip() for origin in origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/test-db")
def test_database():
    try:
        client.admin.command("ping")
        return {"message": "MongoDB connected successfully!"}
    except Exception as error:
        return {"error": str(error)}