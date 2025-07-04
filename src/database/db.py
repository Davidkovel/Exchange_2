from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.database.base import Base

url = f"postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/postgres"
engine = create_async_engine(url=url, echo=False, future=True)
db_pool = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def create_all_tables():
    try:
        async with engine.begin() as conn:
            tables = Base.metadata.tables.keys()
            print(f"Creating tables: {Base.metadata.tables}")
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error creating tables: {e}")
