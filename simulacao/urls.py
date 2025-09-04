from __future__ import annotations

from django.urls import path
from . import views

urlpatterns = [
    path("simular/", views.simulacao_view, name="simular"),
    path("api/simular/", views.api_simular, name="api_simular"),
    path("api/calcular/", views.api_calcular, name="api_calcular"),
    path("api/resultados/<int:simulacao_id>/", views.api_resultado, name="api_resultado"),
    path("historico/", views.historico_view, name="historico"),
    path("salvar/", views.salvar_resultado, name="salvar_resultado"),
]
