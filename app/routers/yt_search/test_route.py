from fastapi import APIRouter
from .test import fast_parallel_links
import time
test_route = APIRouter()


@test_route.get("/test/search/")
async def get_direct_links_route(query: str, limit: int = 10):
    curr_time = time.time()
    data =  await fast_parallel_links(query, limit)
    print("time", time.time() - curr_time)
    return data