from __future__ import annotations

from django.contrib import admin

from .models import Cidade, Turista, Simulacao, Relatorio


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "estado", "populacao", "indice_sustentabilidade", "emissao_co2_per_capita")
    search_fields = ("nome", "estado")
    list_filter = ("estado", "transporte_publico_sustentavel")
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("nome", "estado", "pais", "populacao", "pib_per_capita", "area_km2")
        }),
        ("Localização", {
            "fields": ("latitude", "longitude")
        }),
        ("Sustentabilidade e COP 30", {
            "fields": (
                "indice_sustentabilidade", 
                "emissao_co2_per_capita", 
                "cobertura_vegetal_pct",
                "energia_renovavel_pct",
                "transporte_publico_sustentavel"
            )
        }),
    )


@admin.register(Turista)
class TuristaAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "cidade_origem", "interesse_sustentabilidade", "participante_cop30", "ativo")
    search_fields = ("nome", "email")
    list_filter = ("interesse_sustentabilidade", "participante_cop30", "preferencia_transporte", "ativo")
    readonly_fields = ("data_cadastro",)
    fieldsets = (
        ("Informações Pessoais", {
            "fields": ("nome", "email", "telefone", "idade", "cidade_origem")
        }),
        ("Sustentabilidade", {
            "fields": ("interesse_sustentabilidade", "preferencia_transporte", "participante_cop30")
        }),
        ("Sistema", {
            "fields": ("data_cadastro", "ativo")
        }),
    )


@admin.register(Simulacao)
class SimulacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "turista", "cidade", "data_criacao", "status", "duracao_estadia", "data_fim", "numero_turistas", "gasto_medio", "atividades_sustentaveis")
    list_filter = ("status", "cidade", "data_criacao", "atividades_sustentaveis", "compensacao_carbono", "cenario")
    search_fields = ("turista__nome", "cidade__nome")
    readonly_fields = ("data_criacao", "data_fim")
    fieldsets = (
        ("Participantes", {
            "fields": ("turista", "cidade")
        }),
        ("Detalhes da Viagem", {
            "fields": ("data_viagem", "duracao_estadia", "data_fim", "numero_turistas", "gasto_medio", "orcamento", "cenario", "tipo_hospedagem", "meio_transporte_principal")
        }),
        ("Sustentabilidade", {
            "fields": ("atividades_sustentaveis", "compensacao_carbono")
        }),
        ("Sistema", {
            "fields": ("data_criacao", "status", "parametros")
        }),
    )


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ("simulacao", "pontuacao_sustentabilidade", "emissao_co2_total", "criado_em")
    list_filter = ("criado_em", "simulacao__cidade")
    readonly_fields = ("criado_em", "atualizado_em")
    search_fields = ("simulacao__turista__nome", "simulacao__cidade__nome")
    fieldsets = (
        ("Simulação", {
            "fields": ("simulacao",)
        }),
        ("Resultados", {
            "fields": ("resultado", "pontuacao_sustentabilidade", "impacto_ambiental", "recomendacoes")
        }),
        ("Métricas de Carbono", {
            "fields": ("emissao_co2_total", "emissao_co2_transporte", "emissao_co2_hospedagem")
        }),
        ("Impacto COP 30", {
            "fields": ("economia_local_impacto", "alternativas_sustentaveis", "metas_cop30_alinhamento")
        }),
        ("Sistema", {
            "fields": ("criado_em", "atualizado_em")
        }),
    )
