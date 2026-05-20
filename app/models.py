# models.py - описываем таблицы в базе данных

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# СОЗДАЕМ БАЗОВЫЙ КЛАСС
Base = declarative_base()

# ТАБЛИЦА "devices" (устройства)
class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True) 
    device_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

# ТАБЛИЦА "statistics" (показания)
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime

class Statistic(Base):
    __tablename__ = "statistics" 
    id = Column(Integer, primary_key=True, index=True) 
    device_id = Column(String, index=True) 
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 
    x = Column(Float) # Показание X 
    y = Column(Float) # Показание Y 
    z = Column(Float) # Показание Z


# ТАБЛИЦА "users" (пользователи)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)