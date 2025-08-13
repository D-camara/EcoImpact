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
    return JsonResponse({"detail": "TODO: implementar endpoint de simulação"}, status=501)


@require_http_methods(["GET"])  # Scaffold de API
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    return JsonResponse({"detail": f"TODO: implementar resultado para simulacao_id={simulacao_id}"}, status=501)
