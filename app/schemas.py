# schemas.py - описываем, как должны выглядеть данные в запросах и ответах

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# СХЕМА ДЛЯ ВХОДНЫХ ДАННЫХ (что присылает устройство)
class StatisticIn(BaseModel):
    x: float   # x обязательно и должно быть числом с плавающей точкой
    y: float   # y обязательно и должно быть числом
    z: float   # z обязательно и должно быть числом

# СХЕМА ДЛЯ ВЫХОДНЫХ ДАННЫХ (что мы отдаем, когда просят показания)
class StatisticOut(BaseModel):
    device_id: str          # ID устройства
    timestamp: datetime     # Время измерения
    x: float                # Значение X
    y: float                # Значение Y
    z: float                # Значение Z

# СХЕМА ДЛЯ РЕЗУЛЬТАТОВ АНАЛИЗА (что вернем, когда посчитаем)
class AnalysisResult(BaseModel):
    min: float      # Минимум
    max: float      # Максимум
    count: int      # Количество измерений
    sum: float      # Сумма
    median: float   # Медиана

# СХЕМА ДЛЯ СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ
class UserCreate(BaseModel):
    username: str   # Имя пользователя - обязательно и должно быть текстом