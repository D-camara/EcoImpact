#!/usr/bin/env python
"""
Teste rápido dos gráficos de barras
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoimpact.settings')
django.setup()

from django.test import Client
from simulacao.models import Cidade

def teste_graficos():
    print("🧪 Testando gráficos de barras...")
    
    # Criar cliente de teste
    client = Client()
    
    # Verificar se existem cidades
    cidades = Cidade.objects.all()
    print(f"📊 Cidades disponíveis: {cidades.count()}")
    
    if cidades.count() == 0:
        print("❌ Nenhuma cidade encontrada")
        return
    
    # Selecionar primeira cidade
    cidade = cidades.first()
    print(f"🏙️ Testando com cidade: {cidade.nome}")
    
    # Dados de teste
    dados_simulacao = {
        'cidades_selecionadas': [cidade.id],
        'numero_turistas': 50000,
        'gasto_medio': 150.00,
        'duracao_estadia': 3,
        'multiplicador': 2.5,
        'consumo_agua_pessoa': 200.0,  # litros por pessoa
        'producao_lixo_pessoa': 2.0    # kg por pessoa
    }
    
    print("📋 Dados da simulação:")
    for chave, valor in dados_simulacao.items():
        print(f"   {chave}: {valor}")
    
    try:
        # Fazer POST para simulação
        response = client.post('/', dados_simulacao)
        print(f"🌐 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar se é template de resultado
            content = response.content.decode('utf-8')
            
            if 'economicChart' in content and 'environmentChart' in content:
                print("✅ Template de resultado carregado com gráficos")
                
                # Verificar dados JavaScript
                if 'window.impactoTotal' in content:
                    print("✅ Dados JavaScript encontrados no template")
                else:
                    print("❌ Dados JavaScript não encontrados")
                    
                if 'Chart.js' in content or 'chart.js' in content:
                    print("✅ Chart.js incluído no template")
                else:
                    print("❌ Chart.js não encontrado")
                    
            else:
                print("❌ Template de resultado sem gráficos")
                print("📄 Conteúdo parcial:")
                print(content[:500] + "...")
        else:
            print(f"❌ Erro na simulação: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Erro no teste: {e}")

if __name__ == "__main__":
    teste_graficos()
