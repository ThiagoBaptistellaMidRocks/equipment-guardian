from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/assets")
def list_assets() -> list[dict[str, str]]:
    return []

