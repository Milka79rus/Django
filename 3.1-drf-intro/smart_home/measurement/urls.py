from django.urls import path
from .views import (
    SensorListCreateView,
    SensorRetrieveUpdateView,
    SensorDetailView,
    MeasurementCreateView,
)

urlpatterns = [
    # Список всех датчиков и создание нового
    path('sensors/', SensorListCreateView.as_view(), name='sensor-list-create'),

    # Получение и обновление информации о конкретном датчике
    path('sensors/<int:pk>/', SensorRetrieveUpdateView.as_view(), name='sensor-update'),

    # Детальная информация по датчику (со всеми измерениями)
    path('sensors/<int:pk>/detail/', SensorDetailView.as_view(), name='sensor-detail'),

    # Добавление нового измерения температуры
    path('measurements/', MeasurementCreateView.as_view(), name='measurement-create'),
]
