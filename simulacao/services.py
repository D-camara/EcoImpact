"""Cálculo de impacto econômico do turismo"""

from typing import Dict, Any
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ParamErro(ValueError):
    pass


def validar_parametros(parametros):
    obrigatorios = ['numero_turistas', 'gasto_medio', 'duracao_estadia', 'cidades_visitadas']
    
    for param in obrigatorios:
        if param not in parametros:
            raise ParamErro(f"Parâmetro obrigatório '{param}' não fornecido")
    
    # Validações básicas
    if parametros['numero_turistas'] <= 0:
        raise ParamErro("Número de turistas deve ser maior que zero")
    
    if parametros['gasto_medio'] < 0:
        raise ParamErro("Gasto médio não pode ser negativo")
    
    if parametros['duracao_estadia'] <= 0:
        raise ParamErro("Duração da estadia deve ser maior que zero")
    
    if not parametros['cidades_visitadas'] or len(parametros['cidades_visitadas']) == 0:
        raise ParamErro("Lista de cidades visitadas não pode estar vazia")
    
    ocupacao = parametros.get('ocupacao', 1.0)
    if not (0 < ocupacao <= 1.0):
        raise ParamErro("Taxa de ocupação deve estar entre 0 e 1")


def calcular_impacto_economico(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula impacto econômico do turismo"""
    
    try:
        validar_parametros(parametros)
        
        numero_turistas = int(parametros['numero_turistas'])
        gasto_medio = float(parametros['gasto_medio'])
        duracao_estadia = int(parametros['duracao_estadia'])
        cidades_visitadas = parametros['cidades_visitadas']
        n_cidades = len(cidades_visitadas)
        
        cenario = parametros.get('cenario', 'realista')
        ocupacao = float(parametros.get('ocupacao', 1.0))
        
        # Configurações por cenário
        cenarios = {
            'conservador': {
                'multiplicador_base': 2.0,
                'multiplicador_setorial': 0.2,
                'fator_sazonal': 0.9,
                'elasticidade_cidades': 0.10,
                'elasticidade_duracao': 0.08
            },
            'realista': {
                'multiplicador_base': 2.5,
                'multiplicador_setorial': 0.3,
                'fator_sazonal': 1.0,
                'elasticidade_cidades': 0.15,
                'elasticidade_duracao': 0.05
            },
            'otimista': {
                'multiplicador_base': 3.0,
                'multiplicador_setorial': 0.4,
                'fator_sazonal': 1.2,
                'elasticidade_cidades': 0.20,
                'elasticidade_duracao': 0.03
            }
        }
        
        config = cenarios.get(cenario, cenarios['realista'])
        
        # Parâmetros do cálculo
        multiplicador_base = float(parametros.get('multiplicador_base', config['multiplicador_base']))
        multiplicador_setorial = float(parametros.get('multiplicador_setorial', config['multiplicador_setorial']))
        fator_sazonal = float(parametros.get('fator_sazonal', config['fator_sazonal']))
        ajuste_custom = float(parametros.get('ajuste_custom', 1.0))
        elasticidade_cidades = float(parametros.get('elasticidade_cidades', config['elasticidade_cidades']))
        elasticidade_duracao = float(parametros.get('elasticidade_duracao', config['elasticidade_duracao']))
        limite_reducao_duracao = float(parametros.get('limite_reducao_duracao', 0.3))
        
        # Ajustes por múltiplas cidades e duração
        ajuste_cidades = 1 + elasticidade_cidades * (n_cidades - 1)
        reducao_duracao = min(limite_reducao_duracao, elasticidade_duracao * (duracao_estadia - 1))
        ajuste_duracao = 1 - reducao_duracao
        
        # Cálculo do gasto
        gasto_diario_ajustado = gasto_medio * ajuste_cidades * ajuste_duracao
        gasto_direto = gasto_diario_ajustado * duracao_estadia * numero_turistas * ocupacao
        
        # Multiplicador e impacto total
        multiplicador_total = (multiplicador_base + multiplicador_setorial) * fator_sazonal * ajuste_custom
        impacto_total = gasto_direto * multiplicador_total
        
        # Impacto por cidade
        impacto_por_cidade = {
            cidade: impacto_total / n_cidades 
            for cidade in cidades_visitadas
        }
        
        # Função para arredondar
        def arredondar(valor):
            return round(float(valor), 2)
        
        # Resultado
        resultado = {
            'impacto_total': arredondar(impacto_total),
            'gasto_direto': arredondar(gasto_direto),
            'gasto_diario_ajustado': arredondar(gasto_diario_ajustado),
            'multiplicador_total': arredondar(multiplicador_total),
            'impacto_por_cidade': {k: arredondar(v) for k, v in impacto_por_cidade.items()},
            
            'detalhes': {
                'numero_turistas': numero_turistas,
                'gasto_medio_original': gasto_medio,
                'duracao_estadia': duracao_estadia,
                'numero_cidades': n_cidades,
                'ocupacao': ocupacao,
                'cenario': cenario,
                'ajuste_cidades': arredondar(ajuste_cidades),
                'ajuste_duracao': arredondar(ajuste_duracao),
                'reducao_duracao': arredondar(reducao_duracao),
                'multiplicador_base': multiplicador_base,
                'multiplicador_setorial': multiplicador_setorial,
                'fator_sazonal': fator_sazonal,
                'ajuste_custom': ajuste_custom,
            },
            
            'formula_version': 1,
            'cidades_visitadas': cidades_visitadas,
            'moeda': 'BRL'
        }
        
        return resultado
        
    except Exception as e:
        raise


def calcular_impacto_cop30_especial(parametros):
    """Cálculo especial para COP 30 em Belém"""
    
    # Ajustes para COP 30
    parametros_cop30 = parametros.copy()
    parametros_cop30['multiplicador_setorial'] = parametros_cop30.get('multiplicador_setorial', 0.3) + 0.2
    parametros_cop30['fator_sazonal'] = parametros_cop30.get('fator_sazonal', 1.0) * 1.3
    
    if 'cenario' not in parametros_cop30:
        parametros_cop30['cenario'] = 'otimista'
    
    resultado = calcular_impacto_economico(parametros_cop30)
    resultado['evento_especial'] = 'COP30'
    resultado['ajustes_cop30'] = {
        'multiplicador_evento': 0.2,
        'fator_sazonal_evento': 1.3
    }
    
    return resultado


def gerar_relatorio(simulacao):
    from .models import Relatorio
    
    try:
        # Extrair parâmetros da simulação
        parametros = simulacao.parametros.copy()
        
        # Garantir parâmetros mínimos
        if 'numero_turistas' not in parametros:
            parametros['numero_turistas'] = 1
        
        if 'gasto_medio' not in parametros:
            parametros['gasto_medio'] = simulacao.orcamento / simulacao.duracao_dias if simulacao.orcamento else 200.0
        
        if 'duracao_estadia' not in parametros:
            parametros['duracao_estadia'] = simulacao.duracao_dias
        
        if 'cidades_visitadas' not in parametros:
            parametros['cidades_visitadas'] = [simulacao.cidade.nome]
        
        # Calcular impacto econômico
        if parametros.get('evento_cop30', False):
            resultado_calculo = calcular_impacto_cop30_especial(parametros)
        else:
            resultado_calculo = calcular_impacto_economico(parametros)
        
        # Criar relatório
        relatorio = Relatorio.objects.create(
            simulacao=simulacao,
            resultado=resultado_calculo,
            economia_local_impacto=Decimal(str(resultado_calculo['impacto_total'])),
            pontuacao_sustentabilidade=Decimal(str(_calcular_pontuacao_sustentabilidade(simulacao, resultado_calculo))),
            impacto_ambiental=_gerar_texto_impacto_ambiental(resultado_calculo),
            recomendacoes=_gerar_recomendacoes(simulacao, resultado_calculo),
            alternativas_sustentaveis=_gerar_alternativas_sustentaveis(simulacao),
            metas_cop30_alinhamento=_gerar_alinhamento_cop30(simulacao, resultado_calculo)
        )
        
        # Atualizar status da simulação
        simulacao.status = 'concluida'
        simulacao.save()
        
        return relatorio
        
    except Exception as e:
        simulacao.status = 'erro'
        simulacao.save()
        raise


def _calcular_pontuacao_sustentabilidade(simulacao, resultado_calculo):
    pontuacao = 50.0
    
    if simulacao.atividades_sustentaveis:
        pontuacao += 15
    
    if simulacao.compensacao_carbono:
        pontuacao += 20
    
    if simulacao.tipo_hospedagem == 'hotel_sustentavel':
        pontuacao += 10
    elif simulacao.tipo_hospedagem in ['pousada_local', 'casa_local']:
        pontuacao += 15
    
    if simulacao.meio_transporte_principal in ['onibus', 'trem']:
        pontuacao += 10
    elif simulacao.meio_transporte_principal == 'aviao':
        pontuacao -= 15
    
    if simulacao.duracao_dias > 10:
        pontuacao -= 5
    elif simulacao.duracao_dias <= 3:
        pontuacao += 5
    
    num_cidades = len(resultado_calculo.get('cidades_visitadas', [simulacao.cidade.nome]))
    if num_cidades > 3:
        pontuacao -= (num_cidades - 3) * 3
    
    return max(0, min(100, pontuacao))


def _gerar_texto_impacto_ambiental(resultado_calculo):
    impacto = resultado_calculo['impacto_total']
    num_cidades = len(resultado_calculo['cidades_visitadas'])
    
    if impacto < 5000:
        nivel = "baixo"
    elif impacto < 20000:
        nivel = "moderado"
    else:
        nivel = "alto"
    
    texto = f"Esta simulação apresenta um impacto econômico {nivel} de R$ {impacto:,.2f}. "
    
    if num_cidades > 1:
        texto += f"A viagem por {num_cidades} cidades resulta em maior movimentação e consumo. "
    
    if resultado_calculo.get('evento_especial') == 'COP30':
        texto += "Como parte da COP 30, esta viagem contribui para o turismo de eventos sustentáveis em Belém."
    
    return texto


def _gerar_recomendacoes(simulacao, resultado_calculo):
    recomendacoes = []
    
    if not simulacao.atividades_sustentaveis:
        recomendacoes.append("Priorize atividades sustentáveis como ecoturismo e visitas a reservas.")
    
    if not simulacao.compensacao_carbono:
        recomendacoes.append("Considere programas de compensação de carbono para neutralizar emissões.")
    
    if simulacao.meio_transporte_principal == 'aviao' and simulacao.duracao_dias < 5:
        recomendacoes.append("Para viagens curtas, considere transportes alternativos com menor pegada de carbono.")
    
    if simulacao.tipo_hospedagem == 'hotel_convencional':
        recomendacoes.append("Hospedagens certificadas sustentavelmente reduzem o impacto ambiental.")
    
    return " ".join(recomendacoes) if recomendacoes else "Continue suas práticas sustentáveis!"


def _gerar_alternativas_sustentaveis(simulacao):
    alternativas = []
    
    if simulacao.meio_transporte_principal not in ['onibus', 'trem']:
        alternativas.append("Utilize transporte público ou compartilhado sempre que possível.")
    
    if simulacao.duracao_dias > 7:
        alternativas.append("Considere estadias mais curtas com foco em experiências locais intensas.")
    
    alternativas.append("Explore a gastronomia local para apoiar produtores regionais.")
    alternativas.append("Participe de atividades de conservação ou projetos comunitários.")
    
    return " ".join(alternativas)


def _gerar_alinhamento_cop30(simulacao, resultado_calculo):
    texto = "Esta viagem se alinha com os objetivos da COP 30 de: "
    
    objetivos = []
    
    if simulacao.atividades_sustentaveis:
        objetivos.append("promover turismo sustentável na Amazônia")
    
    if simulacao.compensacao_carbono:
        objetivos.append("reduzir pegada de carbono através de compensação")
    
    if simulacao.tipo_hospedagem in ['pousada_local', 'casa_local']:
        objetivos.append("fortalecer economia local e comunitária")
    
    economia_local = resultado_calculo['impacto_total']
    objetivos.append(f"gerar impacto econômico positivo de R$ {economia_local:,.2f} na região")
    
    if not objetivos:
        return "Considere práticas mais sustentáveis para melhor alinhamento com as metas da COP 30."
    
    return texto + "; ".join(objetivos) + "."
