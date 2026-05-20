from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# СОЗДАЕМ ВРЕМЕННЫЙ АДРЕС БАЗЫ ДАННЫХ (для Docker поменяется)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/devicestats")

# СОЗДАЕМ ДВИГАТЕЛЬ 
engine = create_engine(DATABASE_URL)

# СОЗДАЕМ ФАБРИКУ СЕССИЙ 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)