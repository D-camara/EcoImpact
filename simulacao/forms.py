from __future__ import annotations

from django import forms
from .models import Cidade


class SimulacaoForm(forms.Form):
    cidade_principal = forms.ModelChoiceField(queryset=Cidade.objects.all(), required=True, label="Cidade principal")
    numero_turistas = forms.IntegerField(min_value=1, initial=100, label="Número de turistas")
    gasto_medio = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12, initial=250, label="Gasto médio por dia (R$)")
    duracao_estadia = forms.IntegerField(min_value=1, initial=3, label="Duração (dias)")
    cidades_visitadas = forms.CharField(required=False, label="Outras cidades (separar por vírgula)", help_text="Ex: Belém, Santarém")
    cenario = forms.ChoiceField(choices=[('conservador','Conservador'),('realista','Realista'),('otimista','Otimista')], initial='realista')
    multiplicador = forms.DecimalField(required=False, min_value=0, decimal_places=4, max_digits=8, label="Multiplicador custom (opcional)", help_text="Deixe em branco para usar cenário")

    def limpar_lista_cidades(self):
        raw = self.cleaned_data.get('cidades_visitadas') or ''
        partes = [p.strip() for p in raw.split(',') if p.strip()]
        return partes

    def build_parametros(self):
        if not self.is_valid():
            raise ValueError("Form inválido")
        lista = self.limpar_lista_cidades()
        principal = self.cleaned_data['cidade_principal'].nome
        if not lista:
            lista = [principal]
        else:
            if principal not in lista:
                lista.insert(0, principal)
        params = {
            'numero_turistas': self.cleaned_data['numero_turistas'],
            'gasto_medio': float(self.cleaned_data['gasto_medio']),
            'duracao_estadia': self.cleaned_data['duracao_estadia'],
            'cidades_visitadas': lista,
            'cenario': self.cleaned_data['cenario']
        }
        mult = self.cleaned_data.get('multiplicador')
        if mult is not None:
            params['multiplicador'] = float(mult)
        return params
