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

    class Meta:
        ordering = ["-data_criacao"]

    def __str__(self) -> str:
        return f"Simulação {self.id} - {self.cidade.nome}"


class Relatorio(models.Model):
    simulacao = models.OneToOneField(Simulacao, on_delete=models.CASCADE, related_name="relatorio")
    resultado = models.JSONField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Relatório Simulação {self.simulacao_id}"


## Modelo ImpactoEconomico removido (fora do escopo atual).