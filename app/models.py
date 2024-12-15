from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Documents(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

    texts = relationship("Documents_text", back_populates="document", cascade="all, delete-orphan")


class Documents_text(Base):
    __tablename__ = 'documents_text'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_doc = Column(Integer, ForeignKey('documents.id'), nullable=False)
    text = Column(String)

    document = relationship("Documents", back_populates="texts")