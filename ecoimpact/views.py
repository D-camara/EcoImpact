from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse


def home(request):
    return render(request, 'base.html', {"home": True})


def contato(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        comentario = request.POST.get('comentario')
        
        # Aqui você pode processar o comentário (salvar no banco, enviar email, etc.)
        # Por enquanto, vamos apenas mostrar uma mensagem de sucesso
        
        messages.success(request, 'Comentário enviado com sucesso! Obrigado pelo seu feedback.')
        return redirect('home')
    
    return redirect('home')


def buscar(request):
    query = request.GET.get('q', '')
    # Implementar lógica de busca aqui
    context = {
        'query': query,
        'resultados': []  # Adicionar resultados da busca aqui
    }
    return render(request, 'busca.html', context)
