from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import SimulacaoForm


@require_http_methods(["GET", "POST"])
def simulacao_view(request: HttpRequest) -> HttpResponse:
    """Página principal de simulação de impacto econômico"""
    resultado = None
    
    if request.method == 'POST':
        form = SimulacaoForm(request.POST)
        if form.is_valid():
            try:
                from .services import calcular_impacto_economico, ParametrosInvalidos
                from django.contrib import messages
                
                print("🔄 Processando simulação...")
                
                # Preparar parâmetros para o cálculo
                cidades_selecionadas = form.cleaned_data['cidades_selecionadas']
                print(f"🏙️ Cidades selecionadas: {[c.nome for c in cidades_selecionadas]}")
                
                parametros = {
                    'numero_turistas': form.cleaned_data['numero_turistas'],
                    'gasto_medio': form.cleaned_data['gasto_medio'],
                    'duracao_estadia': form.cleaned_data['duracao_estadia'],
                    'cidades_selecionadas': [cidade.nome for cidade in cidades_selecionadas],
                    'multiplicador': form.cleaned_data['multiplicador'],
                    'consumo_agua_pessoa': form.cleaned_data['consumo_agua_pessoa'],
                    'producao_lixo_pessoa': form.cleaned_data['producao_lixo_pessoa'],
                }
                
                print(f"📊 Parâmetros: {parametros}")
                
                # Calcular impacto
                resultado = calcular_impacto_economico(parametros)
                print(f"✅ Resultado calculado: {resultado is not None}")
                
                # Se há resultado, mostrar template de resultado
                if resultado:
                    print("🎯 Redirecionando para template de resultado...")
                    return render(request, 'simulacao/resultado_simples.html', {
                        'resultado': resultado
                    })
                else:
                    print("❌ Resultado vazio")
                
            except Exception as e:
                print(f"💥 Erro no cálculo: {e}")
                from django.contrib import messages
                messages.error(request, f'Erro no cálculo: {e}')
    else:
        form = SimulacaoForm()
    
    # Mostrar formulário (GET ou POST com erro)
    return render(request, 'simulador.html', {
        'form': form,
        'resultado': resultado
    })


@require_http_methods(["POST"])
def api_simular(request: HttpRequest) -> JsonResponse:
    import json
    from .services import calcular_impacto_economico

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "erro": "JSON inválido. Envie os dados no formato correto.",
            "exemplo": {
                "numero_turistas": 100,
                "gasto_medio": 150.50,
                "duracao_estadia": 7,
                "cidades_visitadas": 3,
                "multiplicador": 1.0,
            },
        }, status=400)

    # Valida campos obrigatórios
    obrigatorios = ["numero_turistas", "gasto_medio", "duracao_estadia", "cidades_visitadas"]
    for campo in obrigatorios:
        if campo not in dados:
            return JsonResponse({"erro": f"Campo '{campo}' é obrigatório."}, status=400)

    # Garante que o multiplicador tenha valor padrão
    dados.setdefault("multiplicador", 1.0)

    # Validação de tipos
    if not isinstance(dados["numero_turistas"], int):
        return JsonResponse({"erro": "O campo 'numero_turistas' deve ser um número inteiro."}, status=400)
    if not isinstance(dados["gasto_medio"], (int, float)):
        return JsonResponse({"erro": "O campo 'gasto_medio' deve ser numérico."}, status=400)
    if not isinstance(dados["duracao_estadia"], int):
        return JsonResponse({"erro": "O campo 'duracao_estadia' deve ser um número inteiro."}, status=400)
    if not isinstance(dados["cidades_visitadas"], int):
        return JsonResponse({"erro": "O campo 'cidades_visitadas' deve ser um número inteiro."}, status=400)
    if not isinstance(dados["multiplicador"], (int, float)):
        return JsonResponse({"erro": "O campo 'multiplicador' deve ser numérico."}, status=400)

    try:
        resultado = calcular_impacto_economico(dados)
    except Exception as e:
        return JsonResponse({"erro": f"Erro interno ao calcular impacto: {str(e)}"}, status=500)

    if "erro" in resultado:
        return JsonResponse(resultado, status=400)

    return JsonResponse(resultado)


@require_http_methods(["GET"])  # Scaffold de API
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    return JsonResponse({"detail": f"TODO: implementar resultado para simulacao_id={simulacao_id}"}, status=501)
