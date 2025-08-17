from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from fastapi import Depends
from typing import AsyncGenerator, Annotated

from decouple import config

DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_NAME = config("DB_NAME")
DB_PORT = config("DB_PORT", cast=int)


DATABASE_URL = f"""postgresql+asyncpg://{DB_USER}:{DB_PASS}
@localhost:{DB_PORT}/{DB_NAME}"""

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def create_tables():
    from app.account.models import User, RefreshToken
    from app.converter.models import UserCredits, CreditRequest, APIKey
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables Created...")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
