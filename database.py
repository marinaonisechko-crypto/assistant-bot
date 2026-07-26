"""
База даних асистента.
Зараз тут таблиця для посилань (перший модуль).
Таблиці wardrobe_items та movies вже описані наперед —
підключимо їх у наступних модулях (Шафа, трекер фільмів).
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///assistant.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # верх/низ/взуття/аксесуари
    season = Column(String(50), nullable=True)
    photo_file_id = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    rating = Column(Integer, nullable=True)
    review = Column(Text, nullable=True)
    watched_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
