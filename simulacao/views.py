from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import ImpactoEconomicoForm
from .models import Simulacao, Relatorio, Cidade
from .services import calcular_impacto_economico


@require_http_methods(["GET", "POST"])
def simulacao_view(request: HttpRequest) -> HttpResponse:
    """Página de simulação com formulário simples.

    POST: cria `Simulacao` + `Relatorio` e redireciona para página de resultado.
    """
    form = ImpactoEconomicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cidades = form.cleaned_data["cidades"]
        # Monta estrutura de cidades homogênea (mesmo peso)
        peso = 1.0
        cities_payload = [
            {
                "name": c.nome,
                "weight": peso,
            }
            for c in cidades
        ]
        parametros = {
            "tourists": form.cleaned_data["turistas"],
            "average_daily_spend": form.cleaned_data["gasto_medio_diario"],
            "stay_duration_days": form.cleaned_data["duracao_estadia"],
            "inflation_factor": form.cleaned_data["inflation_factor"],
            "global_leakage_rate": form.cleaned_data["global_leakage_rate"],
            "cities": cities_payload,
            "scenario_name": "Form Web",
        }
        resultado = calcular_impacto_economico(parametros)
        cidade_ref = cidades.first()  # apenas para referenciar uma cidade no modelo
        simulacao = Simulacao.objects.create(
            cidade=cidade_ref,
            parametros=parametros,
        )
        Relatorio.objects.create(simulacao=simulacao, resultado=resultado)
        return redirect("resultado_html", simulacao_id=simulacao.id)

    return render(request, "simulacao/form.html", {"form": form})


@csrf_exempt
@require_http_methods(["POST"])  # API JSON: recebe payload e retorna resultado
def api_simular(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    resultado = calcular_impacto_economico(payload)
    if "error" in resultado:
        return JsonResponse(resultado, status=400)

    # Persistência opcional se for solicitado
    if payload.get("persist", True):
        # Escolhe a primeira cidade se existir correspondência no banco só para vínculo
        first_city_name = None
        if payload.get("cities"):
            first_city_name = payload["cities"][0].get("name")
        cidade_ref = None
        if first_city_name:
            cidade_ref = Cidade.objects.filter(nome=first_city_name).first()
        simulacao = Simulacao.objects.create(
            cidade=cidade_ref or Cidade.objects.first(),  # fallback (ou None se não houver)
            parametros=payload,
        )
        Relatorio.objects.create(simulacao=simulacao, resultado=resultado)
        resultado["simulacao_id"] = simulacao.id
    return JsonResponse(resultado, status=200)


@require_http_methods(["GET"])
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    try:
        simulacao = Simulacao.objects.get(pk=simulacao_id)
    except Simulacao.DoesNotExist:
        return JsonResponse({"error": "Simulação não encontrada"}, status=404)
    resultado = getattr(simulacao, "relatorio", None)
    if not resultado:
        return JsonResponse({"error": "Relatório não disponível"}, status=404)
    return JsonResponse(resultado.resultado, status=200)


@require_http_methods(["GET"])
def resultado_html(request: HttpRequest, simulacao_id: int) -> HttpResponse:
    try:
        simulacao = Simulacao.objects.get(pk=simulacao_id)
    except Simulacao.DoesNotExist:
        return HttpResponse("Simulação não encontrada", status=404)
    rel = getattr(simulacao, "relatorio", None)
    contexto = {
        "simulacao": simulacao,
        "resultado": rel.resultado if rel else None,
    }
    return render(request, "simulacao/resultado.html", contexto)


@require_http_methods(["GET"])
def ultimo_resultado(request: HttpRequest) -> HttpResponse:
    """Redireciona para o último resultado disponível ou para o formulário."""
    sim = Simulacao.objects.order_by("-id").first()
    if sim and hasattr(sim, "relatorio"):
        return redirect("resultado_html", simulacao_id=sim.id)
    return redirect("simular")
