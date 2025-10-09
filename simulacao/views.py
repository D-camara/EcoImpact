from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
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
                cidade_selecionada = form.cleaned_data['cidade_selecionada']
                print(f"🏙️ Cidade selecionada: {cidade_selecionada.nome}")

                parametros = {
                    'numero_turistas': form.cleaned_data['numero_visitantes'],
                    'gasto_medio': form.cleaned_data['gasto_medio_diario'],
                    'duracao_estadia': form.cleaned_data['duracao_evento'],
                    'cidades_selecionadas': [cidade_selecionada.nome],
                    'multiplicador': form.cleaned_data['multiplicador'],
                    'consumo_agua_pessoa': form.cleaned_data['agua_consumida_por_pessoa'],
                    'producao_lixo_pessoa': form.cleaned_data['lixo_gerado_por_pessoa'],
                }

                print(f"📊 Parâmetros: {parametros}")
                
                # Calcular impacto
                resultado = calcular_impacto_economico(parametros)
                print(f"✅ Resultado calculado: {resultado is not None}")

                # Salvar simulação no banco
                from .models import Simulacao, Cidade, Relatorio
                cidade_obj = Cidade.objects.get(nome=cidade_selecionada.nome)

                # Dados comparativos para gráficos (turistas x habitantes)
                populacao_cidade = cidade_obj.populacao
                duracao_estadia = parametros['duracao_estadia']
                consumo_agua_pessoa = parametros['consumo_agua_pessoa']
                lixo_pessoa = parametros['producao_lixo_pessoa']
                gasto_medio = parametros['gasto_medio']
                numero_turistas = parametros['numero_turistas']

                # Impacto econômico estimado para residentes utilizando PIB per capita (conversão diária)
                try:
                    pib_per_capita = float(cidade_obj.pib_per_capita)
                except (TypeError, ValueError):
                    pib_per_capita = 0.0

                impacto_residentes = round(
                    (pib_per_capita / 365.0) * duracao_estadia * populacao_cidade,
                    2
                )

                consumo_agua_residentes = round(
                    populacao_cidade * consumo_agua_pessoa * duracao_estadia,
                    2
                )

                lixo_residentes = round(
                    populacao_cidade * lixo_pessoa * duracao_estadia,
                    2
                )

                resultado.update({
                    'populacao_cidade': populacao_cidade,
                    'impacto_residentes': impacto_residentes,
                    'consumo_agua_residentes': consumo_agua_residentes,
                    'lixo_residentes': lixo_residentes,
                    'gasto_medio_turista': gasto_medio,
                    'numero_turistas_evento': numero_turistas,
                })

                simulacao = Simulacao(
                    cidade=cidade_obj,
                    parametros=parametros
                )
                simulacao.save()

                # Salvar resultado no banco
                relatorio = Relatorio(
                    simulacao=simulacao,
                    resultado=resultado
                )
                relatorio.save()

                # Se há resultado, mostrar template de resultado
                if resultado:
                    print("🎯 Redirecionando para template de resultado...")
                    return render(request, 'simulacao/resultado_simples.html', {
                        'resultado': resultado,
                        'parametros': parametros
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
    return render(request, 'simulacao/form.html', {
        'form': form,
        'resultado': resultado
    })


@require_http_methods(["POST"])
def api_simular(request: HttpRequest) -> JsonResponse:
    import json
    from .models import Cidade, Simulacao, Relatorio
    from .services import calcular_impacto_economico, ParametrosInvalidos

    try:
        dados = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "erro": "JSON inválido. Envie os dados no formato correto.",
            "exemplo": {
                "cidade_id": 1,
                "numero_turistas": 100,
                "gasto_medio": 150.50,
                "duracao_estadia": 7,
                "cidades_visitadas": 3,
                "cenario": "realista",
            },
        }, status=400)

    obrigatorios = {"cidade_id", "numero_turistas", "gasto_medio", "duracao_estadia", "cidades_visitadas"}
    faltantes = obrigatorios - set(dados)
    if faltantes:
        campo = sorted(faltantes)[0]
        return JsonResponse({"erro": f"Campo '{campo}' é obrigatório."}, status=400)

    try:
        cidade = Cidade.objects.get(pk=dados["cidade_id"])
    except Cidade.DoesNotExist:
        return JsonResponse({"erro": "Cidade informada não foi encontrada."}, status=400)

    parametros = {
        "numero_turistas": dados["numero_turistas"],
        "gasto_medio": dados["gasto_medio"],
        "duracao_estadia": dados["duracao_estadia"],
        "cidades_visitadas": dados.get("cidades_visitadas", []),
        "cidades_selecionadas": [cidade.nome],
        "multiplicador": dados.get("multiplicador"),
        "cenario": dados.get("cenario"),
        "consumo_agua_pessoa": dados.get("consumo_agua_pessoa"),
        "producao_lixo_pessoa": dados.get("producao_lixo_pessoa"),
    }

    try:
        resultado = calcular_impacto_economico(parametros)
    except ParametrosInvalidos as exc:
        return JsonResponse({"erro": str(exc)}, status=400)
    except Exception as exc:  # salvaguarda inesperada
        return JsonResponse({"erro": f"Erro interno ao calcular impacto: {exc}"}, status=500)

    simulacao = Simulacao.objects.create(
        cidade=cidade,
        parametros=parametros,
    )
    Relatorio.objects.create(simulacao=simulacao, resultado=resultado)

    return JsonResponse(
        {
            "simulacao_id": simulacao.id,
            "resultado": resultado,
        },
        status=201,
    )


@require_http_methods(["GET"])  # Scaffold de API
def api_resultado(request: HttpRequest, simulacao_id: int) -> JsonResponse:
    from .models import Relatorio

    relatorio = get_object_or_404(Relatorio, simulacao_id=simulacao_id)

    return JsonResponse(
        {
            "simulacao_id": simulacao_id,
            "resultado": relatorio.resultado,
        }
    )
