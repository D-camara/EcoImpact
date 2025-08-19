from __future__ import annotations

from django import forms
from .models import Cidade


class ImpactoEconomicoForm(forms.Form):
    """Formulário para simulação de impacto econômico simplificada.

    A interface web oferece um caso simples: mesma ponderação para todas as
    cidades escolhidas. Para cenários avançados use a API JSON.
    """

    turistas = forms.IntegerField(min_value=0, label="Número de turistas")
    gasto_medio_diario = forms.FloatField(min_value=0, label="Gasto médio diário (R$)")
    duracao_estadia = forms.FloatField(min_value=0, label="Duração da estadia (dias)")
    cidades = forms.ModelMultipleChoiceField(
        queryset=Cidade.objects.all(), required=True, label="Cidades visitadas"
    )
    inflation_factor = forms.FloatField(
        min_value=0, required=False, initial=1.0, label="Fator de inflação (opcional)"
    )
    global_leakage_rate = forms.FloatField(
        min_value=0,
        max_value=0.99,
        required=False,
        initial=0.0,
        label="Leakage global (0-0.99)",
        help_text="Fraçao adicional não retida após leakages locais.",
    )

    def clean(self):
        data = super().clean()
        if data.get("inflation_factor") in (None, ""):
            data["inflation_factor"] = 1.0
        if data.get("global_leakage_rate") in (None, ""):
            data["global_leakage_rate"] = 0.0
        return data
