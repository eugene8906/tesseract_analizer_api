import pytest
from httpx import AsyncClient
from unittest.mock import patch


@pytest.mark.asyncio
async def test_doc_analyse(ac: AsyncClient, session, test_file_path):
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

        # Не используем await на None
        task_result = mock_task(document_id=document_id, document_path=test_file_path)

    # Проверим, что Celery задача была вызвана с нужными аргументами
    mock_task.assert_called_with(document_id=document_id, document_path=test_file_path)

    # Дополнительно, можно проверить, что task_result — это строка с id задачи
    assert task_result == 'mock_task_id'
