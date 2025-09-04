#!/usr/bin/env python
"""
Script para gerenciar cidades no banco de dados
"""

import sys
import os
import django

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoimpact.settings')
django.setup()

from simulacao.models import Cidade

def verificar_e_criar_cidades():
    """Verifica se existem cidades e cria algumas padrão se necessário"""
    
    print("=== GERENCIAMENTO DE CIDADES ===")
    
    # Verificar cidades existentes
    cidades = Cidade.objects.all()
    print(f"Cidades existentes: {cidades.count()}")
    
    if cidades.exists():
        print("\nCidades no banco:")
        for cidade in cidades:
            print(f"  - {cidade.nome} (pop: {cidade.populacao:,}, PIB per capita: R$ {cidade.pib_per_capita})")
    else:
        print("\nNenhuma cidade encontrada. Criando cidades padrão...")
        
        cidades_padrao = [
            {
                'nome': 'Belém',
                'populacao': 1492745,
                'pib_per_capita': 25847.50
            },
            {
                'nome': 'Ananindeua', 
                'populacao': 535547,
                'pib_per_capita': 18234.80
            },
            {
                'nome': 'Santarém',
                'populacao': 306480,
                'pib_per_capita': 15678.90
            },
            {
                'nome': 'Marabá',
                'populacao': 275086,
                'pib_per_capita': 22145.70
            },
            {
                'nome': 'Parauapebas',
                'populacao': 208273,
                'pib_per_capita': 89234.60
            },
            {
                'nome': 'Castanhal',
                'populacao': 200793,
                'pib_per_capita': 16892.40
            }
        ]
        
        for cidade_data in cidades_padrao:
            cidade, created = Cidade.objects.get_or_create(
                nome=cidade_data['nome'],
                defaults={
                    'populacao': cidade_data['populacao'],
                    'pib_per_capita': cidade_data['pib_per_capita']
                }
            )
            
            if created:
                print(f"✅ Criada: {cidade.nome}")
            else:
                print(f"⚠️  Já existe: {cidade.nome}")
        
        print(f"\n✅ Total de cidades: {Cidade.objects.count()}")

def listar_cidades():
    """Lista todas as cidades com detalhes"""
    cidades = Cidade.objects.all().order_by('nome')
    
    print("\n=== LISTA COMPLETA DE CIDADES ===")
    for cidade in cidades:
        print(f"ID: {cidade.id}")
        print(f"Nome: {cidade.nome}")
        print(f"População: {cidade.populacao:,} habitantes")
        print(f"PIB per capita: R$ {cidade.pib_per_capita}")
        print("-" * 40)

if __name__ == '__main__':
    verificar_e_criar_cidades()
    listar_cidades()
