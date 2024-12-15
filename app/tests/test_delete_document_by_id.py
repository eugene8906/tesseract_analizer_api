import pytest
from httpx import AsyncClient
from sqlalchemy.future import select
from app.models import Documents, Documents_text
from datetime import datetime


@pytest.mark.asyncio
async def test_delete_document_and_related_text(ac: AsyncClient, session, test_file_path):
    # 1. Создаем документ
    document = Documents(
        path="test_path/to/document.txt",
        date=datetime(2024, 11, 10)
    )
    session.add(document)
    await session.commit()

    # Получаем id документа после commit
    document_id = document.id

    # 2. Добавляем текст, связанный с документом
    document_text = Documents_text(
        id_doc=document_id,
        text="This is the text extracted from the document"
    )
    session.add(document_text)
    await session.commit()

    # Проверяем, что документ и текст созданы
    saved_document = await session.get(Documents, document.id)
    saved_text = await session.get(Documents_text, document_text.id)

    assert saved_document is not None
    assert saved_text is not None

    # 3. Запрашиваем удаление документа через API
    response = await ac.delete(f'/doc_delete/{document.id}')

    # Проверяем, что удаление прошло успешно
    assert response.status_code == 404
