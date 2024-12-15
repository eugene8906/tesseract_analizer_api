# from app.celery_app import celery_app
#
# import asyncio
# import pytesseract
# from PIL import Image
# from asgiref.sync import async_to_sync
#
# from app.database import get_async_session
# from app.models import Documents_text
#
#
# async def process_document(document_id: int, document_path: str):
#     extracted_text = await pytesseract.image_to_string(Image.open(document_path))
#
#
#     async with get_async_session() as session:
#         # Запись текста в таблицу
#         new_text_entry = Documents_text(id_doc=document_id, text=extracted_text)
#         session.add(new_text_entry)
#         await session.commit()
#
#
# @celery_app.task
# def analyse_document(document_id: int, document_path: str):
#
#     result_text = async_to_sync(process_document)(document_id, document_path)
#     return result_text
#
#
#     # Запуск асинхронной функции в синхронной задаче
# def run(coro):
#     loop = asyncio.get_event_loop()
#     return loop.run_until_complete(coro)