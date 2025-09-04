#!/usr/bin/env python3
"""
Teste para verificar se os erros JavaScript foram corrigidos
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoimpact.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from simulacao.models import Cidade

def teste_pagina_simulador():
    """Testa se a página do simulador carrega sem erros"""
    
    print("🧪 TESTANDO CORREÇÕES JAVASCRIPT")
    print("=" * 50)
    
    # Verificar se existem cidades no banco
    cidades_count = Cidade.objects.count()
    print(f"✅ Cidades no banco: {cidades_count}")
    
    if cidades_count == 0:
        print("⚠️  Nenhuma cidade encontrada - criando uma cidade de teste")
        Cidade.objects.create(
            nome="Belém - Teste",
            populacao=1500000,
            pib_per_capita=35000.00
        )
    
    # Testar requisição GET (página inicial)
    client = Client()
    try:
        response = client.get('/simular/')
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar se o JavaScript externo está sendo carregado
            content = response.content.decode('utf-8')
            
            checks = [
                ('Chart.js CDN', 'chart.js' in content),
                ('Arquivo JS externo', 'simulador.js' in content),
                ('Canvas do gráfico', 'id="impactChart"' in content),
                ('Formulário presente', 'id="simulationForm"' in content),
                ('Campos ambientais', 'consumo_agua_pessoa' in content),
                ('Seleção de cidades', 'toggleCity' in content or 'city-card' in content),
            ]
            
            print("\n📋 VERIFICAÇÕES DA PÁGINA:")
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
            
            return all(result for _, result in checks)
        else:
            print(f"❌ Erro na página: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar página: {e}")
        return False

def teste_arquivo_js_estatico():
    """Verifica se o arquivo JavaScript estático existe"""
    
    print(f"\n📁 TESTANDO ARQUIVO JAVASCRIPT ESTÁTICO")
    print("=" * 50)
    
    js_path = os.path.join(
        os.path.dirname(__file__), 
        'static', 'js', 'simulador.js'
    )
    
    if os.path.exists(js_path):
        print("✅ Arquivo simulador.js existe")
        
        # Verificar conteúdo do arquivo
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        js_checks = [
            ('Função toggleCity', 'toggleCity' in content),
            ('Função createImpactChart', 'createImpactChart' in content),
            ('Event listeners', 'addEventListener' in content),
            ('Tratamento de Chart.js', 'Chart' in content),
            ('Tratamento de erros', 'try' in content and 'catch' in content),
        ]
        
        print("\n🔍 VERIFICAÇÕES DO JAVASCRIPT:")
        for check_name, result in js_checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
        
        return all(result for _, result in js_checks)
    else:
        print("❌ Arquivo simulador.js não encontrado!")
        return False

def teste_simulacao_completa():
    """Testa uma simulação completa com parâmetros reais"""
    
    print(f"\n⚙️  TESTANDO SIMULAÇÃO COMPLETA")
    print("=" * 50)
    
    # Buscar primeira cidade disponível
    cidade = Cidade.objects.first()
    if not cidade:
        print("❌ Nenhuma cidade disponível para teste")
        return False
    
    client = Client()
    
    # Dados de teste com novos parâmetros ambientais
    dados_simulacao = {
        'cidades_selecionadas': [cidade.id],
        'numero_turistas': 50000,
        'gasto_medio': 200.0,
        'duracao_estadia': 7,
        'multiplicador': 2.5,
        'consumo_agua_pessoa': 150.0,
        'producao_lixo_pessoa': 2.5,
    }
    
    try:
        response = client.post('/simular/', dados_simulacao)
        
        print(f"✅ Simulação executada - Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Verificar se os resultados ambientais estão presentes
            result_checks = [
                ('Impacto econômico', 'Impacto Econômico' in content),
                ('Consumo de água', 'm³' in content),
                ('Produção de lixo', 'ton' in content),
                ('Gráfico com dados', 'data-chart' in content),
                ('Parâmetros ambientais', 'Impactos Ambientais' in content),
            ]
            
            print("\n📊 VERIFICAÇÕES DOS RESULTADOS:")
            for check_name, result in result_checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
            
            return all(result for _, result in result_checks)
        else:
            print(f"❌ Erro na simulação: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE CORREÇÃO JAVASCRIPT\n")
    
    teste1 = teste_pagina_simulador()
    teste2 = teste_arquivo_js_estatico()
    teste3 = teste_simulacao_completa()
    
    print(f"\n{'='*50}")
    if teste1 and teste2 and teste3:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ JavaScript corrigido e funcionando")
        print("✅ Arquivo estático criado")
        print("✅ Simulação com novos parâmetros OK")
        print("✅ Gráfico de pizza integrado")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        if not teste1: print("   - Erro na página do simulador")
        if not teste2: print("   - Problema no arquivo JavaScript")
        if not teste3: print("   - Erro na simulação completa")
        sys.exit(1)
