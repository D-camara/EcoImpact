from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import Cidade, Simulacao, Relatorio
from .services import calcular_impacto_economico, ParametrosInvalidos

from .forms import SimulacaoForm


@require_http_methods(["GET", "POST"])
def simulacao_view(request: HttpRequest) -> HttpResponse:
    """Página de simulação (scaffold). Substituam o conteúdo conforme a implementação."""
    form = SimulacaoForm(request.POST or None)
    return render(request, "simulacao/form.html", {"form": form, "TODO": True})


@csrf_exempt
@require_http_methods(["POST"])
def api_simular(request: HttpRequest) -> JsonResponse:
    """Cria uma simulação persistindo parâmetros e relatório.

    Payload JSON esperado:
      cidade_id (ou cidade_nome)
      numero_turistas, gasto_medio, duracao_estadia, cidades_visitadas (int|lista), opcional cenario, multiplicador
    """
    import json

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"erro": "JSON inválido."}, status=400)

    # Cidade
    cidade = None
    cid = payload.get("cidade_id")
    if cid is not None:
        cidade = Cidade.objects.filter(id=cid).first()
    elif payload.get("cidade_nome"):
        cidade = Cidade.objects.filter(nome__iexact=payload["cidade_nome"].strip()).first()
    if not cidade:
        return JsonResponse({"erro": "Cidade não encontrada (informe cidade_id ou cidade_nome válido)."}, status=400)

    # Parâmetros de simulação (retirando chaves de cidade)
    param_keys = {"numero_turistas", "gasto_medio", "duracao_estadia", "cidades_visitadas", "cenario", "multiplicador"}
    parametros_simulacao = {k: v for k, v in payload.items() if k in param_keys}

    obrigatorios = ["numero_turistas", "gasto_medio", "duracao_estadia", "cidades_visitadas"]
    faltando = [c for c in obrigatorios if c not in parametros_simulacao]
    if faltando:
        return JsonResponse({"erro": f"Campos obrigatórios ausentes: {', '.join(faltando)}"}, status=400)

    try:
        resultado = calcular_impacto_economico(parametros_simulacao)
    except ParametrosInvalidos as e:
        return JsonResponse({"erro": str(e)}, status=400)
    except Exception as e:  # proteção genérica
        return JsonResponse({"erro": f"Falha ao calcular: {e}"}, status=500)

    with transaction.atomic():
        simulacao = Simulacao.objects.create(cidade=cidade, parametros=parametros_simulacao)
        Relatorio.objects.create(simulacao=simulacao, resultado=resultado)

    return JsonResponse({
        "simulacao_id": simulacao.id,
        "cidade": cidade.nome,
        "parametros": parametros_simulacao,
        "resultado": resultado,
    }, status=201)


@require_http_methods(["GET"])  # GET /api/resultados/<id>/
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    simulacao = get_object_or_404(Simulacao, id=simulacao_id)
    rel = getattr(simulacao, "relatorio", None)
    if not rel:
        return JsonResponse({"erro": "Relatório ainda não gerado."}, status=404)
    return JsonResponse({
        "simulacao_id": simulacao.id,
        "cidade": simulacao.cidade.nome,
        "parametros": simulacao.parametros,
        "resultado": rel.resultado,
        "criado_em": rel.criado_em.isoformat(),
    })
