from __future__ import annotations

from django.urls import path
from . import views

urlpatterns = [
    path("simular/", views.simulacao_view, name="simular"),
    path("resultado/ultimo/", views.ultimo_resultado, name="ultimo_resultado"),
    path("resultado/<int:simulacao_id>/", views.resultado_html, name="resultado_html"),
    path("api/simular/", views.api_simular, name="api_simular"),
    path("api/resultados/<int:simulacao_id>/", views.api_resultado, name="api_resultado"),
]
