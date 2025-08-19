from __future__ import annotations

from django.apps import AppConfig


class SimulacaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'simulacao'
    verbose_name = 'Simulação'
