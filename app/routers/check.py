from fastapi import APIRouter
from .proxy_route import get_proxy_config
from .youtube import redis_client

check_url = APIRouter()
#

@check_url.get("/check/token/", include_in_schema=False)
async def check(proxy_token: str):
     proxy_url = redis_client.get(proxy_token)
     print(proxy_url, "proxy_url")
     if proxy_url is None:
         return {"error": True, "message": f"Token invalid or expired {proxy_url}"}
     return {"proxy_url": proxy_url.decode()}


