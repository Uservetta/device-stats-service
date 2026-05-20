from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
from app import crud, schemas, models, tasks
from app.database import engine, SessionLocal

# 1. СОЗДАЕМ ВСЕ ТАБЛИЦЫ В БАЗЕ ДАННЫХ (если их нет)
models.Base.metadata.create_all(bind=engine)

# 2. СОЗДАЕМ ПРИЛОЖЕНИЕ FASTAPI
app = FastAPI(title="Device Statistics Service", version="1.0")

# 3. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПОДКЛЮЧЕНИЯ К БД
def get_db():
    db = SessionLocal()
    try:
        yield db  
    finally:
        db.close()  

# ========== ОСНОВНЫЕ ЭНДПОИНТЫ ==========

# ЭНДПОИНТ 1: ПРИНЯТЬ СТАТИСТИКУ ОТ УСТРОЙСТВА
@app.post("/devices/{device_id}/stats")
def add_statistic(
    device_id: str,              # берется из URL
    stat: schemas.StatisticIn,   # берется из тела запроса (JSON)
    db: Session = Depends(get_db) # получаем соединение с БД
):
    """
    Устройство присылает показания x, y, z.
    Мы сохраняем их в базу с текущей временной меткой.
    """
    result = crud.add_statistic(db, device_id, stat)
    return {"status": "ok", "id": result.id}

# ЭНДПОИНТ 2: ПОЛУЧИТЬ АНАЛИТИКУ (синхронно, быстро)
@app.get("/devices/{device_id}/analysis")
def get_analysis(
    device_id: str,
    start: datetime,  # FastAPI сам превратит строку из параметров в datetime
    end: datetime,
    db: Session = Depends(get_db)
):
    # Получаем данные из БД
    stats = crud.get_statistics(db, device_id, start, end)
    
    if not stats:
        raise HTTPException(status_code=404, detail="No data for this device in given period")
    
    # Считаем аналитику для x, y, z
    result = {}
    for coord in ['x', 'y', 'z']:
        values = [getattr(s, coord) for s in stats]
        result[coord] = crud.compute_analysis(values)
    
    return result

# ЭНДПОИНТ 3: ЗАПУСТИТЬ АСИНХРОННЫЙ АНАЛИЗ
@app.post("/devices/{device_id}/analysis/async")
def start_async_analysis(
    device_id: str,
    start: datetime,
    end: datetime
):
    """
    Запускаем анализ в фоне через Celery.
    Сразу возвращаем task_id, по которому потом можно получить результат.
    """
    task = tasks.analyze_device_task.delay(
        device_id, 
        start.isoformat(),  
        end.isoformat()
    )
    return {"task_id": task.id, "status": "processing"}

# ЭНДПОИНТ 4: ПОЛУЧИТЬ РЕЗУЛЬТАТ АСИНХРОННОГО АНАЛИЗА
@app.get("/tasks/{task_id}")
def get_task_result(task_id: str):
    """
    Проверяем, готов ли результат фоновой задачи.
    Если готов - возвращаем его, если нет - сообщаем "pending"
    """
    task = tasks.analyze_device_task.AsyncResult(task_id)
    if task.ready():
        return {"status": "completed", "result": task.result}
    return {"status": "pending", "task_id": task_id}

# ЭНДПОИНТ 5: СОЗДАТЬ ПОЛЬЗОВАТЕЛЯ
@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Добавляем нового пользователя"""
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ЭНДПОИНТ 6: ПРИВЯЗАТЬ УСТРОЙСТВО К ПОЛЬЗОВАТЕЛЮ
@app.post("/users/{user_id}/devices/{device_id}")
def assign_device(user_id: int, device_id: str, db: Session = Depends(get_db)):
    # Ищем, есть ли уже такое устройство
    device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    
    if not device:
        # Если нет - создаем новую запись
        device = models.Device(device_id=device_id, user_id=user_id)
        db.add(device)
    else:
        # Если есть - обновляем владельца
        device.user_id = user_id  # type: ignore
    
    db.commit()
    return {"ok": True, "device_id": device_id, "user_id": user_id}

# ЭНДПОИНТ 7: ПОЛУЧИТЬ АНАЛИТИКУ ПО ВСЕМ УСТРОЙСТВАМ ПОЛЬЗОВАТЕЛЯ
@app.get("/users/{user_id}/analysis")
def user_analysis(
    user_id: int,
    start: datetime,
    end: datetime,
    db: Session = Depends(get_db)
):
    # Находим все устройства пользователя
    devices = db.query(models.Device).filter(models.Device.user_id == user_id).all()
    
    result = {}
    for dev in devices:
        # Когда мы получаем объект из БД, его атрибуты уже являются значениями, а не колонками
        stats = crud.get_statistics(db, dev.device_id, start, end) # type: ignore
        dev_result = {}
        for coord in ['x', 'y', 'z']:
            values = [getattr(s, coord) for s in stats]
            dev_result[coord] = crud.compute_analysis(values)
        result[dev.device_id] = dev_result  # type: ignore
    
    return result