from django.shortcuts import render
from simulacao.models import Cidade


def home(request):
    return render(request, 'home.html')


def simulador(request):
    cidades = list(Cidade.objects.all())
    return render(request, 'simulador.html', {'cidades': cidades})
