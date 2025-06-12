from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import SessionLocal
from .schema import PlatformCreate, PlatformOut, PlatformUpdate
from routers.platforms import platform as crud


platform_route = APIRouter(prefix="/platforms", tags=["Platforms"])


async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db


@platform_route.post("/", response_model=PlatformOut)
async def create_platform(
    name: str = Form(...),
    base_url: str = Form(...),
    extra_link: str = Form(None),
    hidden: bool = Form(False),
    avatar: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    avatar_path = None
    if avatar:
        filename = f"media/{avatar.filename}"
        with open(filename, "wb") as f:
            f.write(await avatar.read())
        avatar_path = filename

    data = {
        "name": name,
        "base_url": base_url,
        "extra_link": extra_link,
        "hidden": hidden,
        "avatar": avatar_path
    }
    print(data)
    return await crud.create_platform(db, data)


@platform_route.get("/", response_model=list[PlatformOut])
async def get_all(db: AsyncSession = Depends(get_db)):
    data = await crud.get_all_platforms(db)
    if not data:
        raise HTTPException(status_code=404, detail="Platforms not found")
    return data

@platform_route.get("/{platform_id}", response_model=PlatformOut)
async def get_one(platform_id: int, db: AsyncSession = Depends(get_db)):
    platform = await crud.get_platform_by_id(db, platform_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform

@platform_route.put("/{platform_id}", response_model=PlatformOut)
async def update(platform_id: int, data: PlatformUpdate, db: AsyncSession = Depends(get_db)):
    platform = await crud.update_platform(db, platform_id, data)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")
    return platform

@platform_route.delete("/{platform_id}")
async def delete(platform_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_platform(db, platform_id)
    if not success:
        raise HTTPException(status_code=404, detail="Platform not found")
    return {"detail": "Deleted successfully"}
