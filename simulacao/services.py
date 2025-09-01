"""Serviços de simulação (scaffolding)

Preencha aqui a lógica de negócio quando forem implementar.
"""

from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP, getcontext

# Ajusta precisão global (suficiente para valores grandes)
getcontext().prec = 28


class ParametrosInvalidos(ValueError):
    """Erro de validação de parâmetros da simulação."""
    pass


def calcular_impacto_economico(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula o impacto econômico a partir de parâmetros.

    Parâmetros esperados:
      numero_turistas (int > 0)
      gasto_medio (float/decimal >= 0) – gasto médio por turista por dia
      duracao_estadia (int > 0)
      cidades_visitadas (list[str] | int) – lista de nomes ou quantidade
      cenario (str) – conservador | realista | otimista (default: realista)
      multiplicador (float) – opcional; se não fornecido usa tabela de cenários

    Retorna dicionário com valores agregados e breakdown por cidade.
    Lança ParametrosInvalidos em caso de erro de validação.
    """

    # --- Normalização de entradas ---
    try:
        numero_turistas = int(parametros.get('numero_turistas', 0))
        gasto_medio = Decimal(str(parametros.get('gasto_medio', 0)))
        duracao_estadia = int(parametros.get('duracao_estadia', 0))

        cidades_raw = parametros.get('cidades_visitadas', [])
        if isinstance(cidades_raw, int):
            n_cidades = cidades_raw
            lista_cidades = [f"Cidade {i+1}" for i in range(n_cidades)]
        elif isinstance(cidades_raw, (list, tuple)):
            lista_cidades = [str(c).strip() for c in cidades_raw if str(c).strip()]
            n_cidades = len(lista_cidades)
        else:
            lista_cidades = []
            n_cidades = 0

        cenario = str(parametros.get('cenario', 'realista')).lower()
        multiplicador_input = parametros.get('multiplicador')
    except (ValueError, TypeError) as e:
        raise ParametrosInvalidos(f"Erro ao converter parâmetros: {e}")

    # --- Validações ---
    if numero_turistas <= 0:
        raise ParametrosInvalidos("numero_turistas deve ser > 0")
    if gasto_medio < 0:
        raise ParametrosInvalidos("gasto_medio não pode ser negativo")
    if duracao_estadia <= 0:
        raise ParametrosInvalidos("duracao_estadia deve ser > 0")
    if n_cidades <= 0:
        raise ParametrosInvalidos("cidades_visitadas deve conter pelo menos 1 cidade")
    if cenario not in {"conservador", "realista", "otimista"}:
        raise ParametrosInvalidos("cenario inválido (use conservador|realista|otimista)")

    # --- Multiplicadores por cenário (se não fornecido explicitamente) ---
    tabela_cenarios = {
        'conservador': 0.9,
        'realista': 1.0,
        'otimista': 1.15,
    }
    multiplicador = Decimal(str(multiplicador_input)) if multiplicador_input is not None else Decimal(str(tabela_cenarios[cenario]))
    if multiplicador <= 0:
        raise ParametrosInvalidos("multiplicador deve ser > 0")

    # Ajuste leve por diversidade (mais cidades => + até 10%)
    ajuste_cidades = Decimal('1') + Decimal(str(min(0.10, 0.02 * (n_cidades - 1))))
    # Ajuste de estadia (diminui gasto marginal após 10 dias)
    fator_duracao = Decimal('1') - Decimal(str(min(0.25, max(0, duracao_estadia - 10) * 0.02)))

    gasto_total = (Decimal(numero_turistas) * gasto_medio * Decimal(duracao_estadia))
    gasto_ajustado = (gasto_total * ajuste_cidades * fator_duracao)
    impacto_total = (gasto_ajustado * multiplicador)

    impacto_por_cidade = impacto_total / Decimal(n_cidades)
    TWO_PLACES = Decimal('0.01')
    def q(v: Decimal, places=TWO_PLACES):
        return float(v.quantize(places, rounding=ROUND_HALF_UP))
    breakdown_cidades = {nome: q(impacto_por_cidade) for nome in lista_cidades}

    return {
        'impacto_total': q(impacto_total),
        'gasto_total': q(gasto_total),
        'gasto_total_ajustado': q(gasto_ajustado),
        'multiplicador': float(multiplicador.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)),
        'cenario': cenario,
        'ajuste_cidades': float(Decimal(str(ajuste_cidades)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)),
        'fator_duracao': float(Decimal(str(fator_duracao)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)),
        'numero_turistas': numero_turistas,
        'duracao_estadia': duracao_estadia,
        'gasto_medio': float(gasto_medio),
        'cidades_visitadas': lista_cidades,
        'impacto_por_cidade': breakdown_cidades,
        'n_cidades': n_cidades,
        'ok': True
    }