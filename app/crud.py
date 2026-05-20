from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime

# ФУНКЦИЯ 1: СОХРАНИТЬ НОВОЕ ПОКАЗАНИЕ
def add_statistic(db: Session, device_id: str, data: schemas.StatisticIn):
    """
    Параметры:
    - db: соединение с БД (сессия)
    - device_id: ID устройства
    - data: объект с полями x, y, z
    """
    # Создаем новую запись в Python
    stat = models.Statistic(
        device_id=device_id,
        timestamp=datetime.utcnow(),  # текущее время по UTC
        x=data.x,
        y=data.y,
        z=data.z
    )
    
    # 1. Добавляем запись в сессию
    db.add(stat)
    
    # 2. Сохраняем в БД
    db.commit()
    
    # 3. Обновляем объект stat, чтобы он содержал ID из базы
    db.refresh(stat)
    
    # 4. Возвращаем сохраненную запись
    return stat

# ФУНКЦИЯ 2: ПОЛУЧИТЬ ПОКАЗАНИЯ ЗА ПЕРИОД
def get_statistics(db: Session, device_id: str, start: datetime, end: datetime):
    """
    Возвращает список всех показаний устройства device_id 
    с start по end
    """
    # Запрос к базе: выбрать всё из таблицы statistics, где
    # device_id совпадает И timestamp между start и end
    return db.query(models.Statistic).filter(
        models.Statistic.device_id == device_id,
        models.Statistic.timestamp >= start,
        models.Statistic.timestamp <= end
    ).all()  # .all() - выполнить запрос и вернуть все строки

# ФУНКЦИЯ 3: ВЫЧИСЛИТЬ АНАЛИТИКУ
def compute_analysis(values):
    """
    На вход - список чисел (например [1.5, 2.3, 1.8])
    На выход - словарь с min, max, count, sum, median
    """
    if not values:  # Если список пустой
        return None
    
    # Сортируем числа по возрастанию
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    # МЕДИАНА
    if n % 2 == 1:  # нечетное
        median = sorted_vals[n // 2]
    else:           # четное
        median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
    
    # Возвращаем словарь с результатами
    return {
        "min": min(values),      # минимальное
        "max": max(values),      # максимальное
        "count": n,              # количество
        "sum": sum(values),      # сумма
        "median": median         # медиана
    }