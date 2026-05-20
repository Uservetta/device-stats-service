from locust import HttpUser, task, between
import random

class DeviceUser(HttpUser):
    wait_time = between(1, 3)
    
    # ЗАДАЧА 1: Отправить показание
    @task(3)
    def send_statistic(self):
        # Генерируем случайные числа
        data = {
            "x": random.uniform(0, 100),
            "y": random.uniform(0, 100),
            "z": random.uniform(0, 100)
        }
        # Отправляем POST запрос
        self.client.post("/devices/test_device/stats", json=data)
    
    # ЗАДАЧА 2: Получить анализ
    @task(1)
    def get_analysis(self):
        self.client.get("/devices/test_device/analysis?start=2020-01-01T00:00:00&end=2030-01-01T00:00:00")