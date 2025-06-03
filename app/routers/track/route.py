from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST


from .reader import track_recognize_by_multipart_reader
track_router = APIRouter()

@track_router.post("/track/file/")
async def get_media(file: UploadFile = File(...)):
    # if not file.content_type.startswith("audio/"):
    #     raise HTTPException(
    #         status_code=HTTP_400_BAD_REQUEST,
    #         detail="Invalid file type. Only audio files are allowed."
    #     )

    try:
        result = await track_recognize_by_multipart_reader(file)
        return JSONResponse(content={"recognize_result": result})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Track recognition failed: {str(e)}"
        )
