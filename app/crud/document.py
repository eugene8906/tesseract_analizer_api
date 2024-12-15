from app.models import Documents as docs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def create_document_entry(db: AsyncSession, file_path, date):
    document = docs(path=file_path, date=date)
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def delete_document(db: AsyncSession, document_id: int):
    result = await db.execute(select(docs).filter(docs.id == document_id))
    document = result.scalar_one_or_none()

    if document:
        await db.delete(document)
        await db.commit()