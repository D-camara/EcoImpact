#!/usr/bin/env python
"""
Teste rápido da lógica de simulação
"""

import sys
import os
import django

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoimpact.settings')
django.setup()

from simulacao.services import calcular_impacto_economico

def testar_simulacao():
    """Testa a lógica de simulação com dados de exemplo"""
    
    parametros_teste = {
        'numero_turistas': 50000,
        'gasto_medio': 200.0,
        'duracao_estadia': 7,
        'cidades_visitadas': 3,
        'cenario': 'realista',
        'multiplicador': None  # Deixa usar o padrão do cenário
    }
    
    print("=== TESTE DE SIMULAÇÃO DE IMPACTO ECONÔMICO ===")
    print(f"Parâmetros: {parametros_teste}")
    print()
    
    try:
        resultado = calcular_impacto_economico(parametros_teste)
        
        print("✅ RESULTADO DA SIMULAÇÃO:")
        print(f"Impacto Total: R$ {resultado['impacto_total']:,.2f}")
        print(f"Gasto Total Direto: R$ {resultado['gasto_total']:,.2f}")
        print(f"Gasto Ajustado: R$ {resultado['gasto_total_ajustado']:,.2f}")
        print(f"Multiplicador usado: {resultado['multiplicador']}")
        print(f"Cenário: {resultado['cenario']}")
        print(f"Número de cidades: {resultado['n_cidades']}")
        print(f"Ajuste por cidades: {resultado['ajuste_cidades']}")
        print(f"Fator duração: {resultado['fator_duracao']}")
        print()
        
        print("💰 IMPACTO POR CIDADE:")
        for cidade, valor in resultado['impacto_por_cidade'].items():
            print(f"  {cidade}: R$ {valor:,.2f}")
        
        print()
        print("✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_simulacao()
