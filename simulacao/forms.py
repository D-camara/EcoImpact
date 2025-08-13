from __future__ import annotations

from django import forms
from .models import Cidade


class SimulacaoForm(forms.Form):
    """Form de exemplo (scaffold). Ajustem validações depois."""
    cidade = forms.ModelChoiceField(queryset=Cidade.objects.all(), required=True, label="Cidade")
    investimento = forms.FloatField(min_value=0, label="Investimento (R$)")
    multiplicador = forms.FloatField(min_value=0, label="Multiplicador")
    anos = forms.IntegerField(min_value=1, initial=1, label="Anos")
