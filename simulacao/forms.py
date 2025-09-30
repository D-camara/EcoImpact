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
    cidade_selecionada = forms.ModelChoiceField(
        queryset=Cidade.objects.all().order_by('nome'),
        widget=forms.Select(attrs={
            'class': 'form-select h-12 text-base border-2 border-success/30',
        }),
        label="Cidade Sede do Evento",
        help_text="Escolha a cidade que sediará o evento COP-30",
        required=True
    )

    numero_visitantes = forms.IntegerField(
        initial=50000,
        label="Número de Visitantes",
        help_text="Quantidade estimada de visitantes",
        widget=forms.NumberInput(attrs={
            'class': 'form-control h-11',
            'placeholder': '50000'
        })
    )

    gasto_medio_diario = forms.FloatField(
        initial=250,
        label="Gasto Médio Diário (R$)",
        help_text="Valor médio gasto por pessoa/dia",
        widget=forms.NumberInput(attrs={
            'class': 'form-control h-11',
            'placeholder': '250',
            'step': '0.01'
        })
    )

    duracao_evento = forms.IntegerField(
        initial=10,
        label="Duração do Evento (dias)",
        help_text="Número de dias do evento",
        widget=forms.NumberInput(attrs={
            'class': 'form-control h-11',
            'placeholder': '10'
        })
    )

    multiplicador = forms.FloatField(
        initial=2.5,
        label="Multiplicador Econômico",
        help_text="Fator multiplicador do impacto econômico (ex: 2.5)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control h-11',
            'placeholder': '2.5',
            'step': '0.01'
        })
    )

    lixo_gerado_por_pessoa = forms.FloatField(
        initial=2.5,
        label="Lixo Gerado por Pessoa (kg/dia)",
        help_text="Quantidade média de lixo gerado por pessoa por dia",
        widget=forms.NumberInput(attrs={
            'class': 'form-control h-11',
            'placeholder': '2.5',
            'step': '0.01'
        })
    )

    agua_consumida_por_pessoa = forms.FloatField(
        initial=150.0,
        label="Água Consumida por Pessoa (litros/dia)",
        help_text="Quantidade média de água consumida por pessoa por dia",
        widget=forms.NumberInput(attrs={
            'class': 'form-control h-11',
            'placeholder': '150',
            'step': '0.01'
        })
    )
