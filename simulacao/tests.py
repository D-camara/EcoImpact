"""Testes para serviços de cálculo de impacto econômico."""

from __future__ import annotations

import unittest
from django.test import TestCase
from decimal import Decimal

from .services import calcular_impacto_economico, calcular_impacto_cop30_especial, ParamErro


class TestCalculoImpactoEconomico(TestCase):
    """Testes para função de cálculo de impacto econômico."""
    
    def setUp(self):
        """Parâmetros base para testes."""
        self.parametros_base = {
            'numero_turistas': 100,
            'gasto_medio': 200.0,
            'duracao_estadia': 5,
            'cidades_visitadas': ['Belém']
        }
    
    def test_calculo_basico(self):
        """Teste do cálculo básico com parâmetros mínimos."""
        resultado = calcular_impacto_economico(self.parametros_base)
        
        # Verificar estrutura do resultado
        self.assertIn('impacto_total', resultado)
        self.assertIn('gasto_direto', resultado)
        self.assertIn('multiplicador_total', resultado)
        self.assertIn('impacto_por_cidade', resultado)
        self.assertIn('detalhes', resultado)
        self.assertIn('formula_version', resultado)
        
        # Verificar valores básicos
        self.assertGreater(resultado['impacto_total'], 0)
        self.assertGreater(resultado['gasto_direto'], 0)
        self.assertEqual(resultado['detalhes']['numero_turistas'], 100)
        self.assertEqual(resultado['detalhes']['duracao_estadia'], 5)
        
        # Verificar que impacto > gasto direto (devido ao multiplicador)
        self.assertGreater(resultado['impacto_total'], resultado['gasto_direto'])
    
    def test_calculo_multiplas_cidades_aumenta_gasto(self):
        """Teste que múltiplas cidades aumentam o gasto por elasticidade."""
        # Uma cidade
        params_uma_cidade = self.parametros_base.copy()
        resultado_uma = calcular_impacto_economico(params_uma_cidade)
        
        # Três cidades
        params_tres_cidades = self.parametros_base.copy()
        params_tres_cidades['cidades_visitadas'] = ['Belém', 'Manaus', 'Santarém']
        resultado_tres = calcular_impacto_economico(params_tres_cidades)
        
        # Gasto diário ajustado deve ser maior com mais cidades
        self.assertGreater(
            resultado_tres['gasto_diario_ajustado'],
            resultado_uma['gasto_diario_ajustado']
        )
        
        # Impacto total também deve ser maior
        self.assertGreater(resultado_tres['impacto_total'], resultado_uma['impacto_total'])
        
        # Deve ter 3 cidades no resultado
        self.assertEqual(len(resultado_tres['impacto_por_cidade']), 3)
    
    def test_calculo_duracao_longa_reduz_gasto_diario(self):
        """Teste que duração longa reduz gasto diário marginal."""
        # Estadia curta
        params_curta = self.parametros_base.copy()
        params_curta['duracao_estadia'] = 2
        resultado_curta = calcular_impacto_economico(params_curta)
        
        # Estadia longa
        params_longa = self.parametros_base.copy()
        params_longa['duracao_estadia'] = 15
        resultado_longa = calcular_impacto_economico(params_longa)
        
        # Gasto diário ajustado deve ser menor para estadia longa
        self.assertLess(
            resultado_longa['gasto_diario_ajustado'],
            resultado_curta['gasto_diario_ajustado']
        )
        
        # Mas impacto total ainda deve ser maior (mais dias)
        self.assertGreater(resultado_longa['impacto_total'], resultado_curta['impacto_total'])
    
    def test_cenarios_diferentes(self):
        """Teste que cenários diferentes produzem resultados diferentes."""
        params_conservador = self.parametros_base.copy()
        params_conservador['cenario'] = 'conservador'
        resultado_conservador = calcular_impacto_economico(params_conservador)
        
        params_otimista = self.parametros_base.copy()
        params_otimista['cenario'] = 'otimista'
        resultado_otimista = calcular_impacto_economico(params_otimista)
        
        # Cenário otimista deve ter impacto maior que conservador
        self.assertGreater(
            resultado_otimista['impacto_total'],
            resultado_conservador['impacto_total']
        )
        
        # Multiplicadores devem ser diferentes
        self.assertGreater(
            resultado_otimista['multiplicador_total'],
            resultado_conservador['multiplicador_total']
        )
    
    def test_ocupacao_parcial(self):
        """Teste com taxa de ocupação menor que 100%."""
        params_ocupacao = self.parametros_base.copy()
        params_ocupacao['ocupacao'] = 0.7  # 70% de ocupação
        resultado = calcular_impacto_economico(params_ocupacao)
        
        # Deve reduzir o impacto proporcionalmente
        params_total = self.parametros_base.copy()
        resultado_total = calcular_impacto_economico(params_total)
        
        # Impacto com 70% ocupação deve ser ~70% do impacto total
        ratio = resultado['impacto_total'] / resultado_total['impacto_total']
        self.assertAlmostEqual(ratio, 0.7, places=1)
    
    def test_validacao_turistas_zero(self):
        """Teste erro quando número de turistas é zero."""
        params_invalidos = self.parametros_base.copy()
        params_invalidos['numero_turistas'] = 0
        
        with self.assertRaises(ParamErro) as context:
            calcular_impacto_economico(params_invalidos)
        
        self.assertIn("maior que zero", str(context.exception))
    
    def test_validacao_gasto_negativo(self):
        """Teste erro quando gasto médio é negativo."""
        params_invalidos = self.parametros_base.copy()
        params_invalidos['gasto_medio'] = -100
        
        with self.assertRaises(ParamErro) as context:
            calcular_impacto_economico(params_invalidos)
        
        self.assertIn("não pode ser negativo", str(context.exception))
    
    def test_validacao_cidades_vazia(self):
        """Teste erro quando lista de cidades está vazia."""
        params_invalidos = self.parametros_base.copy()
        params_invalidos['cidades_visitadas'] = []
        
        with self.assertRaises(ParamErro) as context:
            calcular_impacto_economico(params_invalidos)
        
        self.assertIn("não pode estar vazia", str(context.exception))
    
    def test_validacao_ocupacao_invalida(self):
        """Teste erro quando taxa de ocupação é inválida."""
        # Ocupação maior que 1
        params_invalidos = self.parametros_base.copy()
        params_invalidos['ocupacao'] = 1.5
        
        with self.assertRaises(ParamErro):
            calcular_impacto_economico(params_invalidos)
        
        # Ocupação zero ou negativa
        params_invalidos['ocupacao'] = 0
        with self.assertRaises(ParamErro):
            calcular_impacto_economico(params_invalidos)
    
    def test_validacao_parametros_obrigatorios(self):
        """Teste erro quando faltam parâmetros obrigatórios."""
        obrigatorios = ['numero_turistas', 'gasto_medio', 'duracao_estadia', 'cidades_visitadas']
        
        for param in obrigatorios:
            params_incompletos = self.parametros_base.copy()
            del params_incompletos[param]
            
            with self.assertRaises(ParamErro) as context:
                calcular_impacto_economico(params_incompletos)
            
            self.assertIn(f"'{param}'", str(context.exception))
    
    def test_limite_reducao_duracao(self):
        """Teste que redução por duração não passa do limite."""
        params_muito_longa = self.parametros_base.copy()
        params_muito_longa['duracao_estadia'] = 100  # Duração muito longa
        params_muito_longa['limite_reducao_duracao'] = 0.2  # Limite de 20%
        
        resultado = calcular_impacto_economico(params_muito_longa)
        
        # Redução não deve passar de 20%
        reducao = resultado['detalhes']['reducao_duracao']
        self.assertLessEqual(reducao, 0.2)
    
    def test_parametros_customizados(self):
        """Teste com parâmetros personalizados."""
        params_custom = self.parametros_base.copy()
        params_custom.update({
            'multiplicador_base': 3.5,
            'fator_sazonal': 1.5,
            'ajuste_custom': 0.9,
            'elasticidade_cidades': 0.25
        })
        
        resultado = calcular_impacto_economico(params_custom)
        
        # Verificar que parâmetros custom foram aplicados
        detalhes = resultado['detalhes']
        self.assertEqual(detalhes['multiplicador_base'], 3.5)
        self.assertEqual(detalhes['fator_sazonal'], 1.5)
        self.assertEqual(detalhes['ajuste_custom'], 0.9)
    
    def test_arredondamento_valores(self):
        """Teste que valores são arredondados corretamente."""
        resultado = calcular_impacto_economico(self.parametros_base)
        
        # Verificar que valores têm no máximo 2 casas decimais
        impacto_decimais = len(str(resultado['impacto_total']).split('.')[-1])
        gasto_decimais = len(str(resultado['gasto_direto']).split('.')[-1])
        
        # Aceitar valores inteiros (0 casas) ou com até 2 casas decimais
        self.assertLessEqual(impacto_decimais, 2)
        self.assertLessEqual(gasto_decimais, 2)


class TestCalculoCOP30Especial(TestCase):
    """Testes para cálculo específico da COP 30."""
    
    def setUp(self):
        self.parametros_base = {
            'numero_turistas': 50,
            'gasto_medio': 300.0,
            'duracao_estadia': 7,
            'cidades_visitadas': ['Belém']
        }
    
    def test_calculo_cop30_tem_multiplicadores_especiais(self):
        """Teste que COP 30 aplica multiplicadores especiais."""
        resultado_normal = calcular_impacto_economico(self.parametros_base)
        resultado_cop30 = calcular_impacto_cop30_especial(self.parametros_base)
        
        # COP 30 deve ter impacto maior
        self.assertGreater(resultado_cop30['impacto_total'], resultado_normal['impacto_total'])
        
        # Deve ter campos específicos da COP 30
        self.assertIn('evento_especial', resultado_cop30)
        self.assertIn('ajustes_cop30', resultado_cop30)
        self.assertEqual(resultado_cop30['evento_especial'], 'COP30')
    
    def test_cop30_usa_cenario_otimista_por_padrao(self):
        """Teste que COP 30 usa cenário otimista por padrão."""
        resultado = calcular_impacto_cop30_especial(self.parametros_base)
        
        self.assertEqual(resultado['detalhes']['cenario'], 'otimista')


# Teste de integração com models (opcional)
class TestIntegracaoModels(TestCase):
    """Testes de integração com modelos Django."""
    
    def test_modelo_pode_armazenar_resultado_calculo(self):
        """Teste que modelos podem armazenar resultado do cálculo."""
        from .models import Cidade, Turista, Simulacao, Relatorio
        
        # Criar dados de teste
        cidade = Cidade.objects.create(
            nome="Belém",
            estado="PA",
            populacao=1500000,
            pib_per_capita=25000
        )
        
        turista = Turista.objects.create(
            nome="Test User",
            email="test@test.com"
        )
        
        simulacao = Simulacao.objects.create(
            turista=turista,
            cidade=cidade,
            duracao_dias=5,
            parametros={
                'numero_turistas': 10,
                'gasto_medio': 200,
                'duracao_estadia': 5,
                'cidades_visitadas': ['Belém']
            }
        )
        
        # Calcular impacto
        resultado = calcular_impacto_economico(simulacao.parametros)
        
        # Criar relatório com resultado
        relatorio = Relatorio.objects.create(
            simulacao=simulacao,
            resultado=resultado,
            economia_local_impacto=resultado['impacto_total']
        )
        
        # Verificar que foi salvo corretamente
        self.assertEqual(relatorio.economia_local_impacto, resultado['impacto_total'])
        self.assertIn('impacto_total', relatorio.resultado)
