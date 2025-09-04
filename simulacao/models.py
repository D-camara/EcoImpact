"""Modelagem mínima: Cidade, Simulacao, Relatorio."""

from __future__ import annotations

from django.db import models


class Cidade(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    populacao = models.PositiveIntegerField()
    pib_per_capita = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=50, default="Pará", help_text="Unidade federativa (default Pará)")

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Simulacao(models.Model):
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name="simulacoes")
    data_criacao = models.DateTimeField(auto_now_add=True)
    parametros = models.JSONField()
    
    # Campos obrigatórios adicionais que existem no banco
    atividades_sustentaveis = models.BooleanField(default=True)
    compensacao_carbono = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default='ativo')
    cenario = models.CharField(max_length=20, default='realista')
    numero_turistas = models.PositiveIntegerField(default=1)
    duracao_estadia = models.PositiveIntegerField(default=1)
    
    # Campos opcionais que existem no banco
    data_viagem = models.DateField(null=True, blank=True)
    meio_transporte_principal = models.CharField(max_length=30, null=True, blank=True)
    orcamento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo_hospedagem = models.CharField(max_length=30, null=True, blank=True)
    turista_id = models.BigIntegerField(null=True, blank=True)
    gasto_medio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-data_criacao"]

    def __str__(self) -> str:
        return f"Simulação {self.id} - {self.cidade.nome}"


class Relatorio(models.Model):
    simulacao = models.OneToOneField(Simulacao, on_delete=models.CASCADE, related_name="relatorio")
    resultado = models.JSONField()
    criado_em = models.DateTimeField(auto_now_add=True)
    
    # Campos obrigatórios adicionais que existem no banco
    alternativas_sustentaveis = models.TextField(default='{}')
    atualizado_em = models.DateTimeField(auto_now=True)
    impacto_ambiental = models.TextField(default='{}')
    metas_cop30_alinhamento = models.TextField(default='{}')
    recomendacoes = models.TextField(default='{}')
    
    # Campos opcionais que existem no banco
    economia_local_impacto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    emissao_co2_hospedagem = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    emissao_co2_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    emissao_co2_transporte = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pontuacao_sustentabilidade = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return f"Relatório Simulação {self.simulacao_id}"


## Modelo ImpactoEconomico removido (fora do escopo atual).