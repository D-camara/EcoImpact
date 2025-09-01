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
        # Remove duplicadas preservando ordem
        seen = set()
        dedup = []
        for p in partes:
            low = p.lower()
            if low not in seen:
                seen.add(low)
                dedup.append(p)
        return dedup

    def clean_numero_turistas(self):
        v = self.cleaned_data['numero_turistas']
        if v > 50_000_000:
            raise forms.ValidationError("Número de turistas muito alto (limite 50 milhões).")
        return v

    def clean_gasto_medio(self):
        v = self.cleaned_data['gasto_medio']
        # Exemplo de limite plausível: R$ 100.000 por dia
        if v > 100_000:
            raise forms.ValidationError("Gasto médio por dia acima do limite permitido (100.000).")
        return v

    def clean_cidades_visitadas(self):
        raw = self.cleaned_data.get('cidades_visitadas') or ''
        # Apenas valida duplicidade explícita (ex: Belém, belém)
        partes = [p.strip() for p in raw.split(',') if p.strip()]
        lowered = [p.lower() for p in partes]
        if len(set(lowered)) != len(lowered):
            raise forms.ValidationError("Lista contém cidades repetidas.")
        return raw

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
