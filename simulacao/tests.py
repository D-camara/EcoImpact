from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from .models import Cidade, Simulacao, Relatorio

from .services import calcular_impacto_economico, ParametrosInvalidos
import json


class TestCalculoImpacto(TestCase):
    def setUp(self):
        self.cidade = Cidade.objects.create(nome="Belém", populacao=1000000, pib_per_capita=50000)
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


class TestAPIs(TestCase):
    def setUp(self):
        self.cidade = Cidade.objects.create(nome="Santarém", populacao=300000, pib_per_capita=40000)

    def test_api_simular_cria_simulacao_e_relatorio(self):
        url = reverse('api_simular')
        payload = {
            "cidade_id": self.cidade.id,
            "numero_turistas": 50,
            "gasto_medio": 200,
            "duracao_estadia": 3,
            "cidades_visitadas": 2,
            "cenario": "realista"
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn('simulacao_id', data)
        self.assertIn('resultado', data)
        self.assertTrue(Simulacao.objects.filter(id=data['simulacao_id']).exists())
        self.assertTrue(Relatorio.objects.filter(simulacao_id=data['simulacao_id']).exists())

    def test_api_resultado_retorna_relatorio(self):
        # Primeiro cria
        sim = Simulacao.objects.create(cidade=self.cidade, parametros={"numero_turistas":10,"gasto_medio":100,"duracao_estadia":2,"cidades_visitadas":1})
        Relatorio.objects.create(simulacao=sim, resultado={"impacto_total": 1000})
        url = reverse('api_resultado', args=[sim.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['simulacao_id'], sim.id)

    def test_api_simular_cidade_inexistente(self):
        url = reverse('api_simular')
        payload = {
            "cidade_id": 9999,
            "numero_turistas": 50,
            "gasto_medio": 200,
            "duracao_estadia": 3,
            "cidades_visitadas": 1
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('erro', resp.json())

    def test_api_simular_parametros_invalidos(self):
        url = reverse('api_simular')
        payload = {
            "cidade_id": self.cidade.id,
            "numero_turistas": 0,
            "gasto_medio": 200,
            "duracao_estadia": 3,
            "cidades_visitadas": 1
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('erro', resp.json())
