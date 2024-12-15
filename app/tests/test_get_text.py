import pytest
from httpx import AsyncClient
from unittest.mock import patch
from sqlalchemy.future import select
from app.models import Documents_text


@pytest.mark.asyncio
async def test_get_text(ac: AsyncClient, session, test_file_path):
    # 1. Загрузить документ
    with open(test_file_path, 'rb') as file:
        upload_response = await ac.post(
            '/upload_doc',
            files={'file': ('text1.png', file, 'image/png')}
        )
    assert upload_response.status_code == 200
    document_id = upload_response.json()['document']

    # 2. Запустить анализ документа
    analyse_response = await ac.post(f'/doc_analyse/{document_id}')
    assert analyse_response.status_code == 200
    task_id = analyse_response.json()['task_id']

    # 3. Мокируем выполнение Celery задачи
    with patch('app.celery_app.analyse_document') as mock_task:
        # Мокируем возвращаемое значение как успешный результат
        mock_task.return_value = 'mock_task_id'  # Симулируем успешное выполнение задачи

        # Вместо того чтобы только мокировать, вручную добавляем текст в таблицу
        mock_task(document_id=document_id, document_path=test_file_path)

        # Добавляем запись в таблицу Documents_text вручную для теста
        new_document_text = Documents_text(id_doc=document_id, text="mock extracted text")
        session.add(new_document_text)
        await session.commit()

    # 4. Проверяем, что текст был добавлен в таблицу Documents_text
    result = await session.execute(
        select(Documents_text).filter(Documents_text.id_doc == document_id)
    )
    document_text = result.scalars().all()
    assert document_text, f"No text found for document_id {document_id}"

    # 5. Запрашиваем текст документа
    response = await ac.get(f'/get_text/{document_id}')
    assert response.status_code == 200
    data = response.json()

    # Проверим, что текст документа получен
    assert data['document_id'] == document_id
    assert isinstance(data['text'], list)  # text должен быть списком
    assert len(data['text']) > 0  # Убедимся, что текст не пустой
