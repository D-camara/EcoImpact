from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def simulador(request):
    return render(request, 'simulador.html')
