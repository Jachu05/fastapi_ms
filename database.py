from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@' \
                          f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL,
                                   echo=True,
                                   connect_args={'timeout': 10},
                                   pool_size=16,
                                   max_overflow=10
                                   )

Base = declarative_base()

async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False,
    # autocommit=False,
    # autoflush=False,
)


# Dependency
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session
