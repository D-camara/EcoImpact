from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import SimulacaoForm


@require_http_methods(["GET", "POST"])
def simulacao_view(request: HttpRequest) -> HttpResponse:
    """Página de simulação (scaffold). Substituam o conteúdo conforme a implementação."""
    form = SimulacaoForm(request.POST or None)
    return render(request, "simulacao/form.html", {"form": form, "TODO": True})


@require_http_methods(["POST"])  # Scaffold de API
def api_simular(request: HttpRequest) -> JsonResponse:
    try:
        import json
        # Pega os dados do corpo da requisição
        dados = json.loads(request.body)
        
        # Chama a função de cálculo do services.py
        from .services import calcular_impacto_economico
        resultado = calcular_impacto_economico(dados)
        
        # Se tiver erro, retorna status 400
        if 'erro' in resultado:
            return JsonResponse(resultado, status=400)
        
        return JsonResponse(resultado)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'erro': 'JSON inválido. Envie os dados no formato correto.',
            'exemplo': {
                'numero_turistas': 100,
                'gasto_medio': 150.50,
                'duracao_estadia': 7,
                'cidades_visitadas': 3,
                'multiplicador': 1.0
            }
        }, status=400)

@require_http_methods(["GET"])  # Scaffold de API
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    return JsonResponse({"detail": f"TODO: implementar resultado para simulacao_id={simulacao_id}"}, status=501)
