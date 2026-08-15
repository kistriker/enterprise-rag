from fastapi import FastAPI
from sqlalchemy import text

from app.api.documents import router as documents_router
from app.api.query import router as query_router
from app.db.session import engine

app = FastAPI()

app.include_router(documents_router)
app.include_router(query_router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {"database": "ok", "result": value}