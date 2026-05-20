from celery import Celery
from app.crud import get_statistics, compute_analysis
from app.database import SessionLocal
from datetime import datetime

# СОЗДАЕМ ПРИЛОЖЕНИЕ CELERY
# broker - где хранить очередь задач (в нашем случае Redis)
# backend - где хранить результаты (тоже Redis)
celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",  # адрес Redis внутри Docker
    backend="redis://redis:6379/0"
)

# ЗАДАЧА: проанализировать устройство за период
@celery_app.task
def analyze_device_task(device_id: str, start: str, end: str):
    """
    Асинхронно считает аналитику для устройства.
    start и end - строки, потому что Celery не умеет передавать datetime напрямую
    """
    # 1. Превращаем строки обратно в datetime
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    
    # 2. Создаем соединение с БД
    db = SessionLocal()
    
    # 3. Получаем все показания за период
    stats = get_statistics(db, device_id, start_dt, end_dt)
    
    # 4. Закрываем соединение
    db.close()
    
    # 5. Если данных нет возвращаем None
    if not stats:
        return None
    
    # 6. Считаем аналитику отдельно для x, y, z
    result = {}
    for coord in ['x', 'y', 'z']:
        # Берем все значения этой координаты из всех записей
        values = [getattr(s, coord) for s in stats]
        # Считаем аналитику
        result[coord] = compute_analysis(values)
    
    # 7. Возвращаем результат (сохранится в Redis)
    return result