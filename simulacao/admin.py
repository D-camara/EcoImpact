from __future__ import annotations

from django.contrib import admin

from .models import Cidade, Simulacao, Relatorio

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "populacao", "pib_per_capita")
    search_fields = ("nome",)


@admin.register(Simulacao)
class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "cidade", "data_criacao")
    list_filter = ("cidade", "data_criacao")
    readonly_fields = ("data_criacao",)


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ("simulacao", "criado_em")
    readonly_fields = ("criado_em",)


## Admin de ImpactoEconomico removido.