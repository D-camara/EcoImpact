from __future__ import annotations

from django.test import TestCase

from .services import calcular_impacto_economico, ParametrosInvalidos


class TestCalculoImpacto(TestCase):
    def setUp(self):
        self.base = {
            'numero_turistas': 100,
            'gasto_medio': 250,
            'duracao_estadia': 4,
            'cidades_visitadas': ['Belém']
        }

    def test_cenario_realista_default(self):
        res = calcular_impacto_economico(self.base)
        self.assertEqual(res['cenario'], 'realista')
        self.assertTrue(res['impacto_total'] > 0)

    def test_cenarios_diferentes_impacto_crescente(self):
        conservador = calcular_impacto_economico({**self.base, 'cenario': 'conservador'})
        realista = calcular_impacto_economico({**self.base, 'cenario': 'realista'})
        otimista = calcular_impacto_economico({**self.base, 'cenario': 'otimista'})
        self.assertLess(conservador['impacto_total'], realista['impacto_total'])
        self.assertLess(realista['impacto_total'], otimista['impacto_total'])

    def test_multiplicador_custom_sobrescreve_cenario(self):
        custom = calcular_impacto_economico({**self.base, 'cenario': 'conservador', 'multiplicador': 2.5})
        self.assertAlmostEqual(custom['multiplicador'], 2.5, places=3)

    def test_varias_cidades_aumenta_ajuste(self):
        multi = calcular_impacto_economico({**self.base, 'cidades_visitadas': ['Belém', 'Santarém', 'Marabá']})
        self.assertGreater(multi['ajuste_cidades'], 1.0)
        self.assertEqual(multi['n_cidades'], 3)

    def test_duracao_longa_reduz_fator(self):
        longa = calcular_impacto_economico({
            **self.base,
            'duracao_estadia': 20
        })
        self.assertLess(longa['fator_duracao'], 1.0)

    def test_validacoes_parametros(self):
        with self.assertRaises(ParametrosInvalidos):
            calcular_impacto_economico({**self.base, 'numero_turistas': 0})
        with self.assertRaises(ParametrosInvalidos):
            calcular_impacto_economico({**self.base, 'gasto_medio': -10})
        with self.assertRaises(ParametrosInvalidos):
            calcular_impacto_economico({**self.base, 'duracao_estadia': 0})
        with self.assertRaises(ParametrosInvalidos):
            calcular_impacto_economico({**self.base, 'cidades_visitadas': []})
        with self.assertRaises(ParametrosInvalidos):
            calcular_impacto_economico({**self.base, 'cenario': 'foo'})

    def test_cidades_inteiro(self):
        res = calcular_impacto_economico({**self.base, 'cidades_visitadas': 2})
        self.assertEqual(res['n_cidades'], 2)
        self.assertEqual(len(res['cidades_visitadas']), 2)

    def test_limite_ajuste_cidades(self):
        muitas = calcular_impacto_economico({**self.base, 'cidades_visitadas': ['A','B','C','D','E','F']})
        self.assertLessEqual(muitas['ajuste_cidades'], 1.10)
