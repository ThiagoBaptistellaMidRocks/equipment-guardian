from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Equipment Guardian API")

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
