#!/usr/bin/env python3
"""
Teste para verificar os valores do gráfico e fazer uma simulação
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoimpact.settings')
django.setup()

from simulacao.services import calcular_impacto_economico

def testar_valores_grafico():
    print("🔍 ANALISANDO VALORES DOS GRÁFICOS")
    print("=" * 50)
    
    # Parâmetros de teste
    params = {
        'numero_turistas': 50000,
        'gasto_medio': 200,
        'duracao_estadia': 7,
        'multiplicador': 2.5,
        'cidades_selecionadas': ['Belém'],
        'consumo_agua_pessoa': 150.0,
        'producao_lixo_pessoa': 2.5
    }
    
    resultado = calcular_impacto_economico(params)
    
    print(f"💰 Impacto Econômico: R$ {resultado['impacto_total']:,.0f}")
    print(f"💧 Água Total: {resultado['consumo_agua_total_m3']:,.0f} m³")
    print(f"🗑️  Lixo Total: {resultado['producao_lixo_total_toneladas']:,.1f} toneladas")
    
    # Mostrar o problema da escala
    print(f"\n📊 PROBLEMA DE ESCALA:")
    print(f"   Razão Economia/Água: {resultado['impacto_total'] / resultado['consumo_agua_total_m3']:,.0f}:1")
    print(f"   Razão Economia/Lixo: {resultado['impacto_total'] / resultado['producao_lixo_total_toneladas']:,.0f}:1")
    
    # Como fica o gráfico de pizza original
    total = resultado['impacto_total'] + resultado['consumo_agua_total_m3'] + resultado['producao_lixo_total_toneladas']
    
    print(f"\n🥧 PORCENTAGENS NO GRÁFICO DE PIZZA ORIGINAL:")
    print(f"   💰 Economia: {(resultado['impacto_total'] / total * 100):.1f}%")
    print(f"   💧 Água: {(resultado['consumo_agua_total_m3'] / total * 100):.3f}%")
    print(f"   🗑️  Lixo: {(resultado['producao_lixo_total_toneladas'] / total * 100):.5f}%")
    
    print(f"\n✅ SOLUÇÃO IMPLEMENTADA:")
    print(f"   📊 Gráficos individuais tipo donut para cada métrica")
    print(f"   📈 Gráfico de barras com normalização logarítmica")
    print(f"   🎯 Tooltips mostrando valores reais")
    
    return resultado

if __name__ == "__main__":
    resultado = testar_valores_grafico()
    
    print(f"\n🌐 ACESSE: http://127.0.0.1:8000/simular/")
    print(f"📝 Preencha os campos e teste os novos gráficos!")
