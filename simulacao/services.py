"""Serviços de simulação - Cálculo de Impacto Econômico da COP 30"""

from typing import Dict, Any


class ParametrosInvalidos(ValueError):
    """Erro de validação de parâmetros da simulação."""
    pass


def calcular_impacto_economico(parametros: Dict[str, Any]) -> Dict[str, Any]:
    try:
        numero_turistas = int(parametros.get('numero_turistas', 0))
        gasto_medio = float(parametros.get('gasto_medio', 0))
        duracao_estadia = int(parametros.get('duracao_estadia', 0))
        multiplicador = float(parametros.get('multiplicador', 2.5))
        
        # Novos parâmetros ambientais
        consumo_agua_pessoa = float(parametros.get('consumo_agua_pessoa', 150.0))
        producao_lixo_pessoa = float(parametros.get('producao_lixo_pessoa', 2.5))

        # Agora trabalhamos com cidades selecionadas do banco de dados
        cidades_selecionadas = parametros.get('cidades_selecionadas', [])
        if isinstance(cidades_selecionadas, (list, tuple)):
            lista_cidades = [str(cidade).strip() for cidade in cidades_selecionadas if str(cidade).strip()]
            n_cidades = len(lista_cidades)
        else:
            # Fallback para compatibilidade
            cidades_raw = parametros.get('cidades_visitadas', [])
            if isinstance(cidades_raw, int):
                n_cidades = cidades_raw
                lista_cidades = [f"Cidade {i+1}" for i in range(n_cidades)]
            else:
                lista_cidades = []
                n_cidades = 0

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
        raise ParametrosInvalidos("Deve selecionar pelo menos 1 cidade")
    if multiplicador <= 0:
        raise ParametrosInvalidos("multiplicador deve ser > 0")
    if consumo_agua_pessoa <= 0:
        raise ParametrosInvalidos("consumo_agua_pessoa deve ser > 0")
    if producao_lixo_pessoa <= 0:
        raise ParametrosInvalidos("producao_lixo_pessoa deve ser > 0")

    # Ajuste leve por diversidade (mais cidades => + até 10%)
    ajuste_cidades = 1 + min(0.10, 0.02 * (n_cidades - 1))
    # Ajuste de estadia (diminui gasto marginal após 10 dias)
    fator_duracao = 1 - min(0.25, max(0, duracao_estadia - 10) * 0.02)

    gasto_total = numero_turistas * gasto_medio * duracao_estadia
    gasto_ajustado = gasto_total * ajuste_cidades * fator_duracao
    impacto_total = gasto_ajustado * multiplicador

    impacto_por_cidade = impacto_total / n_cidades
    breakdown_cidades = {nome: round(impacto_por_cidade, 2) for nome in lista_cidades}

    # Cálculos ambientais
    consumo_agua_total = numero_turistas * consumo_agua_pessoa * duracao_estadia  # litros
    producao_lixo_total = numero_turistas * producao_lixo_pessoa * duracao_estadia  # kg
    
    # Conversões para unidades mais legíveis
    consumo_agua_total_m3 = consumo_agua_total / 1000  # metros cúbicos
    producao_lixo_total_toneladas = producao_lixo_total / 1000  # toneladas

    return {
        'impacto_total': round(impacto_total, 2),
        'gasto_total': round(gasto_total, 2),
        'gasto_total_ajustado': round(gasto_ajustado, 2),
        'multiplicador': round(multiplicador, 4),
        'ajuste_cidades': round(ajuste_cidades, 4),
        'fator_duracao': round(fator_duracao, 4),
        'numero_turistas': numero_turistas,
        'duracao_estadia': duracao_estadia,
        'gasto_medio': gasto_medio,
        'cidades_visitadas': lista_cidades,
        'impacto_por_cidade': breakdown_cidades,
        'n_cidades': n_cidades,
        # Novos dados ambientais
        'consumo_agua_total': round(consumo_agua_total, 2),
        'consumo_agua_total_m3': round(consumo_agua_total_m3, 2),
        'producao_lixo_total': round(producao_lixo_total, 2),
        'producao_lixo_total_toneladas': round(producao_lixo_total_toneladas, 2),
        'consumo_agua_pessoa': consumo_agua_pessoa,
        'producao_lixo_pessoa': producao_lixo_pessoa,
        'ok': True
    }