"""Modelos de domínio (scaffolding).

Implemente os campos que desejarem manter. Estrutura básica pronta.
"""

from __future__ import annotations

from django.db import models


class Cidade(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    populacao = models.PositiveIntegerField()
    pib_per_capita = models.DecimalField(max_digits=12, decimal_places=2)

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

class ImpactoEconomico(models.Model):
    """Calcula o impacto econômico do turismo"""
    
    # Informações básicas
    nome_simulacao = models.CharField(max_length=100, blank=True, help_text="Dê um nome para sua simulação")
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    # Dados para cálculo
    numero_turistas = models.PositiveIntegerField(help_text="Quantos turistas visitaram?")
    gasto_medio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Quanto cada turista gasta por dia? (R$)"
    )
    duracao_estadia = models.PositiveIntegerField(help_text="Quantos dias eles ficam?")
    cidades_visitadas = models.PositiveIntegerField(
        default=1,
        help_text="Quantas cidades eles visitam?"
    )
    
    # Métodos de cálculo (CONTAS MATEMÁTICAS)
    def calcular_impacto_total(self):
        """Faz a conta: turistas × gasto_por_dia × dias"""
        return self.numero_turistas * self.gasto_medio * self.duracao_estadia
    
    def calcular_impacto_por_cidade(self):
        """Divide o total pelas cidades visitadas"""
        if self.cidades_visitadas > 0:
            return self.calcular_impacto_total() / self.cidades_visitadas
        return 0
    
    def gasto_total_turistas(self):
        """Calcula quanto todos os turistas gastam juntos"""
        return self.calcular_impacto_total()
    
    # Representação bonita no admin
    def __str__(self):
        return f"Impacto Econômico: {self.nome_simulacao or 'Simulação'} - {self.data_criacao.strftime('%d/%m/%Y')}"
    
    # Organiza por data mais recente
    class Meta:
        ordering = ["-data_criacao"]
        verbose_name = "Cálculo de Impacto Econômico"
        verbose_name_plural = "Cálculos de Impacto Econômico"