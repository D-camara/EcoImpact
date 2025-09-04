#!/usr/bin/env python
"""
Teste da simulação com cidades do banco de dados
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
from simulacao.models import Cidade

def testar_simulacao_com_cidades():
    """Testa a simulação com cidades reais do banco"""
    
    print("=== TESTE DE SIMULAÇÃO COM CIDADES DO BANCO ===")
    
    # Pegar cidades do banco
    cidades = list(Cidade.objects.all()[:2])  # Pegar 2 cidades
    print(f"Cidades selecionadas: {[c.nome for c in cidades]}")
    
    parametros_teste = {
        'numero_turistas': 30000,
        'gasto_medio': 250.0,
        'duracao_estadia': 5,
        'cidades_selecionadas': [cidade.nome for cidade in cidades],
        'cenario': 'realista',
        'multiplicador': None
    }
    
    print(f"Parâmetros: {parametros_teste}")
    print()
    
    try:
        resultado = calcular_impacto_economico(parametros_teste)
        
        print("✅ RESULTADO DA SIMULAÇÃO:")
        print(f"Impacto Total: R$ {resultado['impacto_total']:,.2f}")
        print(f"Gasto Total Direto: R$ {resultado['gasto_total']:,.2f}")
        print(f"Cenário: {resultado['cenario']}")
        print(f"Multiplicador: {resultado['multiplicador']}")
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
    testar_simulacao_com_cidades()
