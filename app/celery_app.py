from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pytesseract
from PIL import Image
from celery import Celery
from sqlalchemy.orm import Session
from .models import Documents_text, Documents
from app.config import settings
from app.database import SYNC_DATABASE_URL
from sqlalchemy import create_engine


# Настройка обычной синхронной сессии для Celery
engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Инициализация Celery
celery_app = Celery(
    "app_name",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL
)

# Функция для обработки документа и сохранения текста в БД
@celery_app.task
def analyse_document(document_id: int, document_path: str):
    # Создаем синхронную сессию
    db_session = SessionLocal()
    try:
        # Извлечение текста из изображения
        extracted_text = pytesseract.image_to_string(Image.open(document_path))

        # Добавление записи в базу данных
        new_text_entry = Documents_text(id_doc=document_id, text=extracted_text)
        db_session.add(new_text_entry)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

    return f"Document {document_id} processed successfully"
