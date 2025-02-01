from datetime import date
from uuid import uuid4
from sqlalchemy import Column, Integer, String, ARRAY, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.data2dict import jd_format2dict
from . import Base


class StoreDataInDB(Base):
    # print("jd_parser")
    __tablename__ = "document_data"

    id = Column(UUID, primary_key=True, index=True)
    message = Column(String, default="Parsing Completed.")
    content = Column(String, default="No content found.")

    @classmethod
    async def create(cls, db: AsyncSession, input_data=None, id=None, **kwargs):
        if input_data is None:
            input_data = {}
        if not id:
            id = str(uuid4())
        print("input_data", input_data)
        data = jd_format2dict(input_data)

        transaction = cls(
            id=id,
            message=data["message"],
            content=data["content"],
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @classmethod
    async def get(cls, db: AsyncSession, id):
        return await db.execute(cls.__table__.select().where(cls.id == id))

    @classmethod
    async def delete(cls, db: AsyncSession, id):
        return await db.execute(cls.__table__.delete().where(cls.id == id))

    @classmethod
    async def update_by_id(cls, db: AsyncSession, id, data):
        return await db.execute(cls.__table__.update().where(cls.id == id).values(data))

    # get all the data from the table using pagination
    @classmethod
    async def get_all(cls, db: AsyncSession, skip: int = 0, limit: int = 100):
        return await db.execute(cls.__table__.select().offset(skip).limit(limit))
