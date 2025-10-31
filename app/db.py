from collections.abc import AsyncGenerator
from datetime import datetime
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Time, engine, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

class Metadata(Base):
    __tablename__ = "metadata"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    file_size = Column(String, nullable=False)
    uploaded_at = Column(DateTime,default=datetime.utcnow)

class Booking(Base):
    __tablename__="bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True),default=datetime.now())


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
