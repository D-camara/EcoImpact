from __future__ import annotations

import json
import logging
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError

from .forms import SimulacaoForm
from .models import Simulacao, Cidade, Turista, Relatorio
from .services import calcular_impacto_economico, calcular_impacto_cop30_especial, gerar_relatorio, ParamErro

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def simulacao_view(request: HttpRequest) -> HttpResponse:
    """Página de simulação com cálculo de impacto econômico."""
    if request.method == "POST":
        form = SimulacaoForm(request.POST)
        if form.is_valid():
            try:
                # Criar simulação
                simulacao = form.save(commit=False)
                simulacao.status = 'processando'
                simulacao.save()
                
                # Gerar relatório automaticamente
                relatorio = gerar_relatorio(simulacao)
                
                return render(request, "simulacao/resultado.html", {
                    "simulacao": simulacao,
                    "relatorio": relatorio,
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"Erro ao processar simulação: {e}")
                return render(request, "simulacao/form.html", {
                    "form": form,
                    "error": f"Erro ao processar simulação: {e}"
                })
    else:
        form = SimulacaoForm()
    
    return render(request, "simulacao/form.html", {"form": form})


@method_decorator(csrf_exempt, name='dispatch')
@require_http_methods(["POST"])
def api_simular(request: HttpRequest) -> JsonResponse:
    """API endpoint para criar simulação e calcular impacto econômico."""
    try:
        # Parse JSON
        data = json.loads(request.body)
        
        # Validar parâmetros obrigatórios da API
        required_fields = ['numero_turistas', 'gasto_medio', 'duracao_estadia', 'cidades_visitadas']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Campo obrigatório "{field}" não fornecido',
                    'code': 'MISSING_FIELD'
                }, status=400)
        
        # Opcionais para criação de simulação completa
        turista_data = data.get('turista', {})
        cidade_principal = data['cidades_visitadas'][0] if data['cidades_visitadas'] else None
        
        # Buscar ou criar cidade principal
        cidade = None
        if cidade_principal:
            try:
                cidade = Cidade.objects.get(nome=cidade_principal)
            except Cidade.DoesNotExist:
                return JsonResponse({
                    'error': f'Cidade "{cidade_principal}" não encontrada',
                    'code': 'CITY_NOT_FOUND'
                }, status=404)
        
        # Buscar ou criar turista (opcional)
        turista = None
        if turista_data.get('email'):
            turista, created = Turista.objects.get_or_create(
                email=turista_data['email'],
                defaults={
                    'nome': turista_data.get('nome', 'Usuário API'),
                    'interesse_sustentabilidade': turista_data.get('interesse_sustentabilidade', 'medio'),
                    'participante_cop30': turista_data.get('participante_cop30', False)
                }
            )
        
        # Calcular impacto econômico
        if data.get('evento_cop30', False):
            resultado_calculo = calcular_impacto_cop30_especial(data)
        else:
            resultado_calculo = calcular_impacto_economico(data)
        
        # Criar simulação (opcional - só se tiver cidade e turista)
        simulacao_id = None
        if cidade and turista:
            simulacao = Simulacao.objects.create(
                turista=turista,
                cidade=cidade,
                duracao_dias=data['duracao_estadia'],
                orcamento=data.get('orcamento'),
                parametros=data,
                tipo_hospedagem=data.get('tipo_hospedagem'),
                meio_transporte_principal=data.get('meio_transporte_principal'),
                atividades_sustentaveis=data.get('atividades_sustentaveis', True),
                compensacao_carbono=data.get('compensacao_carbono', False),
                status='concluida'
            )
            
            # Criar relatório
            relatorio = Relatorio.objects.create(
                simulacao=simulacao,
                resultado=resultado_calculo,
                economia_local_impacto=resultado_calculo['impacto_total'],
                pontuacao_sustentabilidade=data.get('pontuacao_sustentabilidade', 75.0)
            )
            
            simulacao_id = simulacao.id
        
        # Resposta da API
        response_data = {
            'calculo': resultado_calculo,
            'simulacao_id': simulacao_id,
            'status': 'success',
            'message': 'Cálculo realizado com sucesso'
        }
        
        return JsonResponse(response_data)
        
    except ParamErro as e:
        return JsonResponse({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'code': 'INVALID_JSON'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Erro na API de simulação: {e}")
        return JsonResponse({
            'error': 'Erro interno do servidor',
            'code': 'INTERNAL_ERROR'
        }, status=500)


@require_http_methods(["GET"])
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    """API endpoint para buscar resultado de uma simulação."""
    try:
        simulacao = get_object_or_404(Simulacao, id=simulacao_id)
        
        try:
            relatorio = simulacao.relatorio
            response_data = {
                'simulacao_id': simulacao.id,
                'status': simulacao.status,
                'turista': simulacao.turista.nome if simulacao.turista else None,
                'cidade': simulacao.cidade.nome,
                'duracao_dias': simulacao.duracao_dias,
                'relatorio': {
                    'impacto_economico_total': float(relatorio.economia_local_impacto) if relatorio.economia_local_impacto else None,
                    'pontuacao_sustentabilidade': float(relatorio.pontuacao_sustentabilidade) if relatorio.pontuacao_sustentabilidade else None,
                    'resultado_completo': relatorio.resultado,
                    'impacto_ambiental': relatorio.impacto_ambiental,
                    'recomendacoes': relatorio.recomendacoes,
                    'criado_em': relatorio.criado_em.isoformat()
                }
            }
            
        except Relatorio.DoesNotExist:
            response_data = {
                'simulacao_id': simulacao.id,
                'status': simulacao.status,
                'message': 'Relatório ainda não foi gerado',
                'relatorio': None
            }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Erro ao buscar resultado da simulação {simulacao_id}: {e}")
        return JsonResponse({
            'error': 'Erro ao buscar resultado',
            'code': 'FETCH_ERROR'
        }, status=500)


@require_http_methods(["GET"])
def api_calcular_simples(request: HttpRequest) -> JsonResponse:
    """API simples para cálculo direto sem criar simulação."""
    try:
        # Parâmetros via GET
        parametros = {
            'numero_turistas': int(request.GET.get('turistas', 1)),
            'gasto_medio': float(request.GET.get('gasto', 200)),
            'duracao_estadia': int(request.GET.get('dias', 3)),
            'cidades_visitadas': request.GET.get('cidades', 'Belém').split(','),
            'cenario': request.GET.get('cenario', 'realista'),
            'ocupacao': float(request.GET.get('ocupacao', 1.0))
        }
        
        # Calcular
        evento_cop30 = request.GET.get('cop30', 'false').lower() == 'true'
        if evento_cop30:
            resultado = calcular_impacto_cop30_especial(parametros)
        else:
            resultado = calcular_impacto_economico(parametros)
        
        return JsonResponse({
            'parametros': parametros,
            'resultado': resultado,
            'evento_cop30': evento_cop30
        })
        
    except (ValueError, ParamErro) as e:
        return JsonResponse({
            'error': str(e),
            'code': 'PARAMETER_ERROR'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Erro no cálculo simples: {e}")
        return JsonResponse({
            'error': 'Erro no cálculo',
            'code': 'CALCULATION_ERROR'
        }, status=500)
