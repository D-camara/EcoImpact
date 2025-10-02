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
