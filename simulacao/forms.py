from __future__ import annotations

from django import forms
from .models import Cidade


class CityCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Widget customizado para exibir cidades com informações detalhadas"""
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        
        if value:
            try:
                cidade = Cidade.objects.get(pk=value.value)
                option['data'] = {
                    'populacao': cidade.populacao,
                    'pib_per_capita': cidade.pib_per_capita
                }
            except Cidade.DoesNotExist:
                option['data'] = {
                    'populacao': 0,
                    'pib_per_capita': 0
                }
        
        return option


class SimulacaoForm(forms.Form):
    """Formulário para simulação de impacto econômico da COP 30"""
    
    # Campo para seleção de cidades do banco de dados
    cidades_selecionadas = forms.ModelMultipleChoiceField(
        queryset=Cidade.objects.all().order_by('nome'),
        widget=CityCheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label="Cidades para Análise",
        help_text="Selecione as cidades que receberão impacto turístico",
        required=True
    )
    
    numero_turistas = forms.IntegerField(
        min_value=1,
        initial=50000,
        label="Número de Turistas",
        help_text="Quantidade estimada de turistas",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 50000'
        })
    )
    
    gasto_medio = forms.FloatField(
        min_value=0.01,
        initial=200.00,
        label="Gasto Médio Diário (R$)",
        help_text="Valor em reais que cada turista gasta por dia",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 200.00',
            'step': '0.01'
        })
    )
    
    duracao_estadia = forms.IntegerField(
        min_value=1,
        max_value=365,
        initial=7,
        label="Duração da Estadia (dias)",
        help_text="Quantos dias cada turista permanece na região",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 7'
        })
    )
    
    multiplicador = forms.FloatField(
        min_value=0.1,
        max_value=5.0,
        initial=2.5,
        required=True,
        label="Multiplicador Econômico",
        help_text="Fator que multiplica o impacto direto dos gastos (recomendado: 1.5 a 3.0)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: 2.5',
            'step': '0.1'
        })
    )
    
    # Novos parâmetros ambientais
    consumo_agua_pessoa = forms.FloatField(
        min_value=1.0,
        initial=150.0,
        label="Consumo de Água por Pessoa (L/dia)",
        help_text="Quantidade média de água consumida por turista por dia",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1.0',
            'placeholder': 'Ex: 150.0'
        })
    )
    
    producao_lixo_pessoa = forms.FloatField(
        min_value=0.1,
        initial=2.5,
        label="Produção de Lixo por Pessoa (kg/dia)",
        help_text="Quantidade média de resíduos gerados por turista por dia",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Ex: 2.5'
        })
    )
