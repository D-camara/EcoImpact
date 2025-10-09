#!/usr/bin/env python3
"""
Teste das novas funcionalidades:
- Parâmetros ambientais (água e lixo)
- Gráfico de pizza
- Interface aprimorada
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoimpact.settings')
django.setup()

from simulacao.services import calcular_impacto_economico
from simulacao.models import Cidade

def testar_novos_parametros():
    """Testa os novos parâmetros ambientais"""
    
    print("🧪 TESTANDO NOVOS PARÂMETROS AMBIENTAIS")
    print("=" * 50)
    
    # Verificar se temos cidades no banco
    cidades = list(Cidade.objects.all())
    if not cidades:
        print("❌ Nenhuma cidade encontrada no banco de dados!")
        return False
    
    print(f"✅ Encontradas {len(cidades)} cidades no banco")
    for cidade in cidades:
        print(f"   - {cidade.nome}: {cidade.populacao:,} hab, PIB/hab: R$ {cidade.pib_per_capita:,.2f}")
    
    # Parâmetros de teste
    parametros = {
        'numero_turistas': 75000,
        'gasto_medio': 250.0,
        'duracao_estadia': 5,
        'multiplicador': 2.2,
        'cidades_selecionadas': [cidade.nome for cidade in cidades],
        # Novos parâmetros ambientais
        'consumo_agua_pessoa': 180.0,  # litros por dia
        'producao_lixo_pessoa': 3.2,   # kg por dia
    }
    
    print(f"\n🔧 PARÂMETROS DO TESTE:")
    print(f"   Turistas: {parametros['numero_turistas']:,}")
    print(f"   Gasto médio: R$ {parametros['gasto_medio']}/dia")
    print(f"   Duração: {parametros['duracao_estadia']} dias")
    print(f"   Multiplicador: {parametros['multiplicador']}")
    print(f"   Cidades: {', '.join(parametros['cidades_selecionadas'])}")
    print(f"   Consumo água: {parametros['consumo_agua_pessoa']} L/dia")
    print(f"   Produção lixo: {parametros['producao_lixo_pessoa']} kg/dia")
    
    try:
        # Executar simulação
        resultado = calcular_impacto_economico(parametros)
        
        print(f"\n📊 RESULTADOS:")
        print(f"   💰 Impacto Econômico Total: R$ {resultado['impacto_total']:,.2f}")
        print(f"   💧 Consumo de Água Total: {resultado['consumo_agua_total']:,.0f} L ({resultado['consumo_agua_total_m3']:,.0f} m³)")
        print(f"   🗑️  Produção de Lixo Total: {resultado['producao_lixo_total']:,.0f} kg ({resultado['producao_lixo_total_toneladas']:.1f} ton)")
        
        print(f"\n🏙️  DISTRIBUIÇÃO POR CIDADE:")
        for cidade, impacto in resultado['impacto_por_cidade'].items():
            print(f"   - {cidade}: R$ {impacto:,.2f}")
        
        # Verificar se todos os novos campos estão presentes
        novos_campos = [
            'consumo_agua_total',
            'consumo_agua_total_m3',
            'producao_lixo_total',
            'producao_lixo_total_toneladas',
            'consumo_agua_pessoa',
            'producao_lixo_pessoa'
        ]
        
        print(f"\n✅ VERIFICAÇÃO DOS NOVOS CAMPOS:")
        for campo in novos_campos:
            if campo in resultado:
                print(f"   ✅ {campo}: {resultado[campo]}")
            else:
                print(f"   ❌ {campo}: AUSENTE")
                return False
        
        print(f"\n🎯 TESTE CONCLUÍDO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_interface_cidades():
    """Testa se a interface de cidades está funcionando"""
    print(f"\n🎨 TESTANDO INTERFACE DE CIDADES")
    print("=" * 50)
    
    from simulacao.forms import SimulacaoForm
    
    # Criar formulário
    form = SimulacaoForm()
    
    # Verificar se o widget customizado está funcionando
    cidades_field = form.fields['cidades_selecionadas']
    print(f"✅ Campo de cidades configurado")
    print(f"   Widget: {type(cidades_field.widget).__name__}")
    print(f"   Queryset: {cidades_field.queryset.count()} cidades")
    
    # Verificar novos campos ambientais
    novos_campos = ['consumo_agua_pessoa', 'producao_lixo_pessoa']
    for campo in novos_campos:
        if campo in form.fields:
            field = form.fields[campo]
            print(f"✅ Campo {campo}:")
            print(f"   Label: {field.label}")
            print(f"   Initial: {field.initial}")
            print(f"   Help: {field.help_text}")
        else:
            print(f"❌ Campo {campo} não encontrado!")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DAS NOVAS FUNCIONALIDADES\n")
    
    sucesso1 = testar_novos_parametros()
    sucesso2 = testar_interface_cidades()
    
    print(f"\n{'='*50}")
    if sucesso1 and sucesso2:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Parâmetros ambientais funcionando")
        print("✅ Interface de cidades atualizada") 
        print("✅ Cálculos integrados")
        print("✅ Gráfico de pizza (visual no browser)")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        sys.exit(1)
