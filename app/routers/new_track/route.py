from fastapi import APIRouter, HTTPException
from .backend_track_search import track_backend_yt_dlp_search
from ..proxy_route import get_proxy_config

new_track_router = APIRouter()

@new_track_router.get("/track/search")
async def track_search(query: str, offset: int = 0, limit: int = 10):
    try:
        proxy_config , proxy = await get_proxy_config(), None
        if proxy_config:
            proxy = f"http://{proxy_config['username']}:{proxy_config['password']}@{proxy_config['server'].replace('http://', '')}"
        search_results = await track_backend_yt_dlp_search(query, int(offset), int(limit), proxy)
        return {"search_results": search_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))












# async def track_search_route_handler(request: http.Request):
#   """
#    description: Track search
#    tags:
#    - Track
#    produces:
#    - application/json
#    parameters:
#    - in: query
#      name: query
#      schema:
#        type: string
#    - in: query
#      name: offset
#      schema:
#        type: string
#    - in: query
#      name: limit
#      schema:
#        type: string
#    - in: query
#      name: proxy
#      schema:
#        type: string
#   """

#   query = request.query.get("query", "")
#   offset = request.query.get("offset", "0")
#   limit = request.query.get("limit", "10")
#   proxy = request.query.get("proxy", None)

#   if not (offset.isnumeric() and limit.isnumeric()):
#     return http.json_response({"error": "Invalid parameters"}, status=http.HTTPBadRequest.status_code)

#   try:
#     search_results = await track_search(query, int(offset), int(limit), proxy)
#     return http.json_response({"search_results": search_results})
#   except Exception as ex:
#     await report("track-search", f"Unable to search (Query: {query}, Offset: {offset}, Limit: {limit})", str(ex))
#     return http.json_response({"error": "Unable to search"}, status=http.HTTPInternalServerError.status_code)