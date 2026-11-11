from fastapi import FastAPI
from app.api.routes import router
from app.database.connection import client

app = FastAPI()

app.include_router(router)

@app.get("/test-db")
def test_database():
    try:
        client.admin.command("ping")
        return {"message": "MongoDB connected successfully!"}
    except Exception as error:
        return {"error": str(error)}