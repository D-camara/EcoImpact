from __future__ import annotations

from django.urls import path
from . import views

urlpatterns = [
    path("simular/", views.simulacao_view, name="simular"),
    path("api/simular/", views.api_simular, name="api_simular"),
    path("api/resultados/<int:simulacao_id>/", views.api_resultado, name="api_resultado"),
    path("api/calcular/", views.api_calcular_simples, name="api_calcular_simples"),
]
