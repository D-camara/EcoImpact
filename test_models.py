#!/usr/bin/env python
"""
Script para testar os modelos do EcoImpact COP 30
Execute: python test_models.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoimpact.settings')
django.setup()

from simulacao.models import Cidade, Turista, Simulacao, Relatorio
from datetime import date
from decimal import Decimal

def teste_completo():
    print("🌿 Testando modelos EcoImpact COP 30...\n")
    
    # 1. Teste Cidade
    print("1️⃣ Testando modelo Cidade...")
    try:
        belem = Cidade.objects.create(
            nome="Belém",
            estado="PA",
            populacao=1499641,
            pib_per_capita=Decimal('25000.00'),
            indice_sustentabilidade=Decimal('75.5'),
            emissao_co2_per_capita=Decimal('4.2'),
            cobertura_vegetal_pct=Decimal('45.0'),
            energia_renovavel_pct=Decimal('80.0'),
            transporte_publico_sustentavel=True
        )
        print(f"✅ Cidade criada: {belem}")
    except Exception as e:
        print(f"❌ Erro ao criar cidade: {e}")
        return
    
    # 2. Teste Turista
    print("\n2️⃣ Testando modelo Turista...")
    try:
        turista = Turista.objects.create(
            nome="Ana Silva",
            email="ana.silva@email.com",
            idade=35,
            cidade_origem=belem,
            interesse_sustentabilidade="alto",
            preferencia_transporte="publico",
            participante_cop30=True
        )
        print(f"✅ Turista criado: {turista}")
    except Exception as e:
        print(f"❌ Erro ao criar turista: {e}")
        return
    
    # 3. Teste Simulação
    print("\n3️⃣ Testando modelo Simulação...")
    try:
        simulacao = Simulacao.objects.create(
            turista=turista,
            cidade=belem,
            data_viagem=date(2025, 11, 15),
            duracao_dias=5,
            orcamento=Decimal('2500.00'),
            tipo_hospedagem="hotel_sustentavel",
            meio_transporte_principal="onibus",
            atividades_sustentaveis=True,
            compensacao_carbono=True,
            status="concluida"
        )
        print(f"✅ Simulação criada: {simulacao}")
    except Exception as e:
        print(f"❌ Erro ao criar simulação: {e}")
        return
    
    # 4. Teste Relatório
    print("\n4️⃣ Testando modelo Relatório...")
    try:
        relatorio = Relatorio.objects.create(
            simulacao=simulacao,
            pontuacao_sustentabilidade=Decimal('85.5'),
            emissao_co2_total=Decimal('125.30'),
            emissao_co2_transporte=Decimal('80.20'),
            emissao_co2_hospedagem=Decimal('45.10'),
            economia_local_impacto=Decimal('1800.00'),
            impacto_ambiental="Viagem com baixo impacto ambiental devido às escolhas sustentáveis.",
            recomendacoes="Continue priorizando transporte público e hospedagens sustentáveis.",
            alternativas_sustentaveis="Considere utilizar bicicletas para trajetos curtos.",
            metas_cop30_alinhamento="Viagem alinhada com objetivos de redução de emissões da COP 30."
        )
        print(f"✅ Relatório criado: {relatorio}")
    except Exception as e:
        print(f"❌ Erro ao criar relatório: {e}")
        return
    
    # 5. Teste de Relacionamentos
    print("\n5️⃣ Testando relacionamentos...")
    try:
        print(f"🏙️ Simulações de {belem.nome}: {belem.simulacoes.count()}")
        print(f"👤 Simulações de {turista.nome}: {turista.simulacoes.count()}")
        print(f"📊 Relatório da simulação: {simulacao.relatorio}")
        print(f"🌍 Turistas de {belem.nome}: {belem.turistas_origem.count()}")
    except Exception as e:
        print(f"❌ Erro nos relacionamentos: {e}")
        return
    
    # 6. Teste de Listagem
    print("\n6️⃣ Testando consultas...")
    try:
        print(f"📍 Total de cidades: {Cidade.objects.count()}")
        print(f"👥 Total de turistas: {Turista.objects.count()}")
        print(f"🔄 Total de simulações: {Simulacao.objects.count()}")
        print(f"📋 Total de relatórios: {Relatorio.objects.count()}")
        
        # Consulta específica para COP 30
        participantes_cop30 = Turista.objects.filter(participante_cop30=True)
        print(f"🌱 Participantes da COP 30: {participantes_cop30.count()}")
        
        simulacoes_sustentaveis = Simulacao.objects.filter(atividades_sustentaveis=True)
        print(f"♻️ Simulações sustentáveis: {simulacoes_sustentaveis.count()}")
        
    except Exception as e:
        print(f"❌ Erro nas consultas: {e}")
        return
    
    print("\n🎉 TODOS OS TESTES PASSARAM! ✅")
    print("🌿 Sua modelagem para COP 30 está funcionando perfeitamente!")
    
    # Limpar dados de teste (opcional)
    resposta = input("\n🗑️ Deseja limpar os dados de teste? (s/n): ").lower()
    if resposta == 's':
        relatorio.delete()
        simulacao.delete()
        turista.delete()
        belem.delete()
        print("✅ Dados de teste removidos!")

if __name__ == "__main__":
    teste_completo()
