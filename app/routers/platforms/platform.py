from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models.user import Platform
from .schema import PlatformCreate, PlatformUpdate
from typing import List, Optional

# Create
async def create_platform(db: AsyncSession, data: PlatformCreate) -> Platform:
    new_platform = Platform(**data)
    db.add(new_platform)
    await db.commit()
    await db.refresh(new_platform)
    return new_platform

# Get all
async def get_all_platforms(db: AsyncSession) -> List[Platform]:
    result = await db.execute(select(Platform))
    return result.scalars().all()

# Get by ID
async def get_platform_by_id(db: AsyncSession, platform_id: int) -> Optional[Platform]:
    result = await db.execute(select(Platform).where(Platform.id == platform_id))
    return result.scalar_one_or_none()

# Update
async def update_platform(db: AsyncSession, platform_id: int, data: PlatformUpdate) -> Optional[Platform]:
    result = await db.execute(select(Platform).where(Platform.id == platform_id))
    platform = result.scalar_one_or_none()
    if platform:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(platform, key, value)
        await db.commit()
        await db.refresh(platform)
        return platform
    return None

# Delete
async def delete_platform(db: AsyncSession, platform_id: int) -> bool:
    result = await db.execute(select(Platform).where(Platform.id == platform_id))
    platform = result.scalar_one_or_none()
    if platform:
        await db.delete(platform)
        await db.commit()
        return True
    return False
