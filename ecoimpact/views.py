from django.shortcuts import render

def home(request):
    return render(request, 'base.html')

from django.shortcuts import render

# Constante
FATOR_MULTIPLICADOR = 1.5

# Função de cálculo
def calcular_impactos(num_turistas, media_gasto_por_dia, dias_estadia, cidades, fator=FATOR_MULTIPLICADOR):
    impacto_direto = num_turistas * media_gasto_por_dia * dias_estadia
    impacto_total = impacto_direto * fator
    impacto_por_cidade = impacto_total / cidades
    return impacto_direto, impacto_total, impacto_por_cidade

# View inicial
def home(request):
    return render(request, "base.html")

# View do cálculo
def impacto_view(request):
    resultado = None
    
    if request.method == "POST":
        num_turistas = int(request.POST.get("num_turistas"))
        media_gasto_por_dia = float(request.POST.get("media_gasto_por_dia"))
        dias_estadia = int(request.POST.get("dias_estadia"))
        cidades = int(request.POST.get("cidades"))

        impacto_direto, impacto_total, impacto_por_cidade = calcular_impactos(
            num_turistas, media_gasto_por_dia, dias_estadia, cidades
        )

        resultado = {
            "impacto_direto": impacto_direto,
            "impacto_total": impacto_total,
            "impacto_por_cidade": impacto_por_cidade,
        }

    return render(request, "impacto.html", {"resultado": resultado})
