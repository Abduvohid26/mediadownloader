from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from schema.user import UserCreate, User
from database.database import SessionLocal
from routers.insta_route import insta_router
from routers.proxy_route import proxies
app = FastAPI()
app.include_router(insta_router)
app.include_router(proxies)

# DB sessiyasini olish
# DB sessiyasini olish (Asinxron)
async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

