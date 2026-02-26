from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./api_sentinel.db"

engine = create_async_engine(
    url=DATABASE_URL,
    echo = True
)

AsyncSessionLocal = sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()