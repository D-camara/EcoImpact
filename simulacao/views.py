from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

from .models import Cidade, Simulacao, Relatorio
from .services import calcular_impacto_economico, calcular_impacto_ambiental, ParametrosInvalidos

from .forms import SimulacaoForm


def _preparar_dados_relatorio_default():
    """Prepara dados padrão para campos obrigatórios do relatório."""
    return {
        'alternativas_sustentaveis': json.dumps([], ensure_ascii=False),
        'impacto_ambiental': json.dumps({}, ensure_ascii=False),
        'metas_cop30_alinhamento': json.dumps({}, ensure_ascii=False),
        'recomendacoes': json.dumps([], ensure_ascii=False),
    }
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import Cidade, Simulacao, Relatorio
from .services import calcular_impacto_economico, calcular_impacto_ambiental, ParametrosInvalidos

from .forms import SimulacaoForm


@require_http_methods(["GET", "POST"])
def simulacao_view(request: HttpRequest) -> HttpResponse:
    form = SimulacaoForm(request.POST or None)
    contexto = {"form": form}
    if request.method == "POST" and form.is_valid():
        try:
            params = form.build_parametros()
            resultado = calcular_impacto_economico(params)
            # calcula também impactos ambientais quando os campos existem
            try:
                resultado_ambiental = calcular_impacto_ambiental(params)
            except ParametrosInvalidos:
                resultado_ambiental = None
            contexto.update({
                "resultado": resultado,
                "resultado_ambiental": resultado_ambiental,
                "params": params,
            })
            return render(request, "simulacao/resultado.html", contexto)
        except ParametrosInvalidos as e:
            contexto["erro"] = str(e)
        except Exception as e:  # fallback
            contexto["erro"] = f"Erro inesperado: {e}"
    return render(request, "simulacao/form.html", contexto)


@csrf_exempt
@require_http_methods(["POST"])
def api_simular(request: HttpRequest) -> JsonResponse:
    """Cria uma simulação persistindo parâmetros e relatório.

        Payload JSON esperado:
            cidade_id (ou cidade_nome)
            numero_turistas, gasto_medio, duracao_estadia, cidades_visitadas (int|lista), opcional multiplicador
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
    param_keys = {"numero_turistas", "gasto_medio", "duracao_estadia", "cidades_visitadas", "multiplicador"}
    parametros_simulacao = {k: v for k, v in payload.items() if k in param_keys}

    obrigatorios = ["numero_turistas", "gasto_medio", "duracao_estadia", "cidades_visitadas"]
    faltando = [c for c in obrigatorios if c not in parametros_simulacao]
    if faltando:
        return JsonResponse({"erro": f"Campos obrigatórios ausentes: {', '.join(faltando)}"}, status=400)

    try:
        resultado = calcular_impacto_economico(parametros_simulacao)
        # tenta calcular ambiental se parâmetros disponíveis
        try:
            resultado_ambiental = calcular_impacto_ambiental(parametros_simulacao)
            # anexa campos ambientais ao resultado para persistência
            resultado['ambiental'] = resultado_ambiental
        except ParametrosInvalidos:
            resultado['ambiental'] = None
    except ParametrosInvalidos as e:
        return JsonResponse({"erro": str(e)}, status=400)
    except Exception as e:  # proteção genérica
        return JsonResponse({"erro": f"Falha ao calcular: {e}"}, status=500)

    with transaction.atomic():
        # Extrair valores dos parâmetros para campos específicos
        numero_turistas = parametros_simulacao.get('numero_turistas', 1)
        duracao_estadia = parametros_simulacao.get('duracao_estadia', 1)
        cenario = parametros_simulacao.get('cenario', 'realista')
        gasto_medio = parametros_simulacao.get('gasto_medio')
        
        simulacao = Simulacao.objects.create(
            cidade=cidade, 
            parametros=parametros_simulacao,
            numero_turistas=numero_turistas,
            duracao_estadia=duracao_estadia,
            cenario=cenario,
            gasto_medio=gasto_medio,
            atividades_sustentaveis=True,
            compensacao_carbono=True,
            status='ativo'
        )
        Relatorio.objects.create(simulacao=simulacao, resultado=resultado)

    return JsonResponse({
        "simulacao_id": simulacao.id,
        "cidade": cidade.nome,
        "parametros": parametros_simulacao,
        "resultado": resultado,
    }, status=201)



@require_http_methods(["GET", "POST"])
def api_calcular(request: HttpRequest) -> JsonResponse:
    """Retorna cálculo econômico e ambiental sem persistir.

    Aceita JSON no POST ou query params no GET com as chaves usadas pelo formulário.
    """
    import json

    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({"erro": "JSON inválido."}, status=400)
    else:
        # GET -> extrai de query params
        payload = {k: v for k, v in request.GET.items()}

    # Mapeia nomes comuns do template para os esperados pelos serviços
    # Expecting: numero_turistas, gasto_medio, duracao_estadia, cidades_visitadas, cenario, multiplicador,
    # consumo_agua_por_pessoa, taxa_reciclagem
    # Allow short names from front-end
    mapped = {}
    mapping = {
        'numeroPessoas': 'numero_turistas',
        'numero_turistas': 'numero_turistas',
        'diasEvento': 'duracao_estadia',
        'duracao_estadia': 'duracao_estadia',
        'gastoTurista': 'gasto_medio',
        'gasto_medio': 'gasto_medio',
        'multiplicador': 'multiplicador',
        'consumoAgua': 'consumo_agua_por_pessoa',
        'consumo_agua_por_pessoa': 'consumo_agua_por_pessoa',
        'taxaReciclagem': 'taxa_reciclagem',
        'taxa_reciclagem': 'taxa_reciclagem',
    }
    for k, v in payload.items():
        key = mapping.get(k, k)
        mapped[key] = v

    # Some fields need conversion: cidades_visitadas can be a comma string or omitted
    if 'cidades_visitadas' in mapped and isinstance(mapped['cidades_visitadas'], str):
        mapped['cidades_visitadas'] = [p.strip() for p in mapped['cidades_visitadas'].split(',') if p.strip()]

    # If cidades_visitadas is missing, try to build it from cidade_principal (id) or cidade_nome
    if 'cidades_visitadas' not in mapped:
        # cidade_principal may be provided as an id
        cp = mapped.get('cidade_principal') or mapped.get('cidade_id')
        if cp:
            try:
                cid = int(cp)
                cidade_obj = Cidade.objects.filter(id=cid).first()
                if cidade_obj:
                    mapped['cidades_visitadas'] = [cidade_obj.nome]
            except (ValueError, TypeError):
                # if not an int, treat as name
                mapped['cidades_visitadas'] = [str(cp)]
        elif mapped.get('cidade_nome'):
            mapped['cidades_visitadas'] = [str(mapped.get('cidade_nome'))]

    try:
        econ = calcular_impacto_economico(mapped)
    except ParametrosInvalidos as e:
        return JsonResponse({"erro": str(e)}, status=400)
    try:
        amb = calcular_impacto_ambiental(mapped)
    except ParametrosInvalidos:
        amb = None
    # If a main city was provided, try to include its PIB (per capita and total) so frontend can compute percentages
    cidade_info = None
    cp = mapped.get('cidade_principal') or mapped.get('cidade_id') or (mapped.get('cidades_visitadas')[0] if mapped.get('cidades_visitadas') else None)
    if cp:
        try:
            cid = int(cp)
            cidade_obj = Cidade.objects.filter(id=cid).first()
        except (ValueError, TypeError):
            cidade_obj = Cidade.objects.filter(nome__iexact=str(cp)).first()
        if cidade_obj:
            pib_pc = float(cidade_obj.pib_per_capita)
            pib_total = pib_pc * float(cidade_obj.populacao)
            cidade_info = {"id": cidade_obj.id, "nome": cidade_obj.nome, "pib_per_capita": pib_pc, "pib_total": pib_total}

    result = {"economico": econ, "ambiental": amb, "cidade": cidade_info}
    return JsonResponse(result)


@require_http_methods(["GET"])  # GET /api/resultados/<id>/
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    simulacao = get_object_or_404(Simulacao, id=simulacao_id)
    rel = getattr(simulacao, "relatorio", None)
    if not rel:
        return JsonResponse({"erro": "Relatório ainda não gerado."}, status=404)
    # Try to include city PIB information so frontends (histórico) can display percentages
    cidade_info = None
    try:
        cidade_obj = simulacao.cidade
        if cidade_obj:
            pib_pc = float(cidade_obj.pib_per_capita)
            pib_total = pib_pc * float(cidade_obj.populacao)
            cidade_info = {"id": cidade_obj.id, "nome": cidade_obj.nome, "pib_per_capita": pib_pc, "pib_total": pib_total}
    except Exception:
        cidade_info = None

    return JsonResponse({
        "simulacao_id": simulacao.id,
        "cidade": simulacao.cidade.nome,
        "cidade_info": cidade_info,
        "parametros": simulacao.parametros,
        "resultado": rel.resultado,
        "criado_em": rel.criado_em.isoformat(),
    })


@require_http_methods(["POST"])
def salvar_resultado(request: HttpRequest) -> JsonResponse:
    """Endpoint auxiliar para salvar o resultado atualmente exibido na UI.

    Recebe JSON com os mesmos campos aceitos por `api_simular`. Retorna simulacao_id.
    """
    import json
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"erro": "JSON inválido."}, status=400)

    # Reuse api_simular's logic by delegating creation steps here
    cidade = None
    cid = payload.get("cidade_id")
    if cid is not None:
        cidade = Cidade.objects.filter(id=cid).first()
    elif payload.get("cidade_nome"):
        cidade = Cidade.objects.filter(nome__iexact=payload["cidade_nome"].strip()).first()
    if not cidade:
        return JsonResponse({"erro": "Cidade não encontrada."}, status=400)

    param_keys = {"numero_turistas", "gasto_medio", "duracao_estadia", "cidades_visitadas", "multiplicador"}
    parametros_simulacao = {k: v for k, v in payload.items() if k in param_keys}
    try:
        resultado = calcular_impacto_economico(parametros_simulacao)
        try:
            resultado_ambiental = calcular_impacto_ambiental(parametros_simulacao)
            resultado['ambiental'] = resultado_ambiental
        except ParametrosInvalidos:
            resultado['ambiental'] = None
    except ParametrosInvalidos as e:
        return JsonResponse({"erro": str(e)}, status=400)

    # Prevent near-duplicate saves: if a simulation for same city and identical params exists in last 30s, return it
    from django.utils import timezone
    from datetime import timedelta

    thirty_seconds_ago = timezone.now() - timedelta(seconds=30)
    recent = Simulacao.objects.filter(cidade=cidade, data_criacao__gte=thirty_seconds_ago)
    for s in recent:
        if s.parametros == parametros_simulacao:
            # found duplicate
            return JsonResponse({"simulacao_id": s.id, "duplicate": True}, status=200)

    with transaction.atomic():
        # Extrair valores dos parâmetros para campos específicos
        numero_turistas = parametros_simulacao.get('numero_turistas', 1)
        duracao_estadia = parametros_simulacao.get('duracao_estadia', 1)
        cenario = parametros_simulacao.get('cenario', 'realista')
        gasto_medio = parametros_simulacao.get('gasto_medio')
        
        simulacao = Simulacao.objects.create(
            cidade=cidade, 
            parametros=parametros_simulacao,
            numero_turistas=numero_turistas,
            duracao_estadia=duracao_estadia,
            cenario=cenario,
            gasto_medio=gasto_medio,
            atividades_sustentaveis=True,
            compensacao_carbono=True,
            status='ativo'
        )
        Relatorio.objects.create(simulacao=simulacao, resultado=resultado)

    return JsonResponse({"simulacao_id": simulacao.id, "duplicate": False}, status=201)


@require_http_methods(["GET"])
def historico_view(request: HttpRequest) -> HttpResponse:
    sims = Simulacao.objects.select_related('cidade').all().order_by('-data_criacao')[:200]
    contexto = {"simulacoes": sims}
    return render(request, "simulacao/historico.html", contexto)
