from fastapi import APIRouter
from .test import get_audio_direct_links

test_route = APIRouter()


@test_route.get("/test/search/")
async def get_direct_links_route(query: str, limit: int = 10):
    return  await get_audio_direct_links(query, limit)
