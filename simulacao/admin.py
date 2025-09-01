from __future__ import annotations

from django.contrib import admin

from .models import Cidade, Simulacao, Relatorio

from .models import ImpactoEconomico

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


@admin.register(ImpactoEconomico)
class ImpactoEconomicoAdmin(admin.ModelAdmin):
    list_display = (
        "nome_simulacao",
        "cidade",
        "numero_turistas",
        "gasto_medio",
        "duracao_estadia",
        "cidades_visitadas",
        "impacto_total",
        "impacto_por_cidade",
        "gasto_total_turistas",
        "data_criacao",
    )
    list_filter = ("data_criacao", "cidades_visitadas")
    search_fields = ("nome_simulacao",)
    readonly_fields = (
        "data_criacao",
        "impacto_total",
        "impacto_por_cidade",
        "gasto_total_turistas",
    )
    list_display_links = ("nome_simulacao", "cidade")

    # Mostra a cidade da simulação
    def cidade(self, obj):
        return obj.simulacao.cidade
    cidade.admin_order_field = "simulacao__cidade"
    cidade.short_description = "Cidade"

    # Campos calculados
    def impacto_total(self, obj):
        return obj.calcular_impacto_total()
    impacto_total.short_description = "Impacto Total"

    def impacto_por_cidade(self, obj):
        return obj.calcular_impacto_por_cidade()
    impacto_por_cidade.short_description = "Impacto por Cidade"

    def gasto_total_turistas(self, obj):
        return obj.gasto_total_turistas()
    gasto_total_turistas.short_description = "Gasto Total Turistas"