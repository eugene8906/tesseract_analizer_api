from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import Documents, Documents_text
from app.utils.file_handler import save_file, delete_file
from app.crud.document import create_document_entry, delete_document
from app.celery_app import analyse_document
from typing import List, Dict, Any


router = APIRouter()

@router.post(
        '/upload_doc',
             summary="Загрузить документ",
             description="Загружает документ и сохраняет его в файловой системе, затем создает запись о документе в базе данных.",
             response_model=dict
)
async def upload_document(
    file: UploadFile,
    db: AsyncSession = Depends(get_async_session)
):
    """
        Загружает документ на сервер и сохраняет информацию о нем в базе данных.

        Параметры:
        - **file** (UploadFile): Загружаемый файл документа.

        Возвращает:
        - **message** (str): Сообщение об успешной загрузке.
        - **document** (int): Идентификатор загруженного документа.

        Пример ошибки:
        - 400: Ошибка при сохранении файла или создании записи в базе данных.
    """
    try:
        file_path = await save_file(file)

        document_entry = await create_document_entry(
            db=db, file_path=file_path, date=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        return {'message': 'Document uploaded successfully', 'document': document_entry.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
         '/doc_delete/{document_id}',
               summary="Удалить документ",
               description="Удаляет документ из файловой системы и базы данных по его `document_id`.",
               response_model=dict
)
async def delete_document_by_id(
        document_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    """
       Удаляет документ из файловой системы и базы данных.

       Параметры:
       - **document_id** (int): Идентификатор документа для удаления.

       Возвращает:
       - **message** (str): Сообщение об успешном удалении.

       Примеры ошибок:
       - 404: Документ или файл не найден.
    """

    result = await db.execute(select(Documents).filter(Documents.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail='Document not found')

    file_path = document.path

    if not delete_file(file_path):
        raise HTTPException(status_code=404, detail='File not found on disk')

    await delete_document(db, document_id)

    return {'message': 'Document deleted successfully'}


@router.post(
        '/doc_analyse/{document_id}',
             summary="Анализировать документ",
             description="Запускает задачу Celery для анализа текста документа, заданного по его `document_id`.",
             response_model=dict
)
async def doc_analyse(
        document_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """
        Запускает задачу анализа документа с использованием Celery.

        Параметры:
        - **document_id** (int): Идентификатор документа для анализа.

        Возвращает:
        - **message** (str): Сообщение о запуске задачи анализа.
        - **task_id** (str): Идентификатор запущенной задачи Celery.

        Примеры ошибок:
        - 404: Документ не найден.
    """

    result = await session.execute(select(Documents).filter(Documents.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = document.path

    await session.close()

    task = analyse_document.delay(document_id, file_path)

    return {'message': 'Document analysis started successfully', 'task_id': task.id}


@router.get(
        '/get_text/{document_id}',
            response_model=Dict[str, Any],
            summary="Получить текст документа",
            description="Возвращает текст, связанный с указанным `document_id`, из таблицы `Documents_text`."
)
async def get_text(
        document_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
        Получить текст документа по его ID.

        Параметры:
        - **document_id** (int): Идентификатор документа, текст которого нужно получить.

        Возвращает:
        - **document_id** (int): ID запрашиваемого документа.
        - **text** (str): Текст, связанный с документом. Если текста нет, возвращает ошибку 404.

        Примеры ошибок:
        - 404: "Text not found for the given document ID" — если текста для указанного ID нет в базе данных.
        """

    result = await session.execute(
        select(Documents_text).filter(Documents_text.id_doc == document_id)
    )
    document_text = result.scalars().all()

    if not document_text:
        raise HTTPException(status_code=404, detail="Text not found for the given document ID")

    return {"document_id": document_id, "text": [text.text for text in document_text]}



