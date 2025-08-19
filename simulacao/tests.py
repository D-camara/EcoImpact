from __future__ import annotations

from django.test import SimpleTestCase

from .services import (
    CityConfig,
    ScenarioInput,
    compute_economic_impact,
    quick_scenario,
    calcular_impacto_economico,
)


class EconomicImpactTests(SimpleTestCase):
    def test_zero_values_return_zeroes(self):
        scenario = ScenarioInput(
            tourists=0,
            average_daily_spend=500.0,
            stay_duration_days=5,
            cities=[CityConfig("Belém")],
        )
        result = compute_economic_impact(scenario)
        self.assertEqual(result["summary"]["gross_spend"], 0.0)

    def test_basic_scenario_positive(self):
        scenario = ScenarioInput(
            tourists=100,
            average_daily_spend=100.0,
            stay_duration_days=2,
            cities=[CityConfig("Belém", weight=2), CityConfig("Santarém", weight=1)],
        )
        result = compute_economic_impact(scenario)
        gross = result["summary"]["gross_spend"]
        self.assertGreater(gross, 0)
        # 100 turistas * 2 dias * 100 R$ = 20.000 R$ (inflation 1.0)
        self.assertAlmostEqual(gross, 20000.0)

    def test_quick_scenario_wrapper(self):
        result = quick_scenario(
            tourists=50,
            average_daily_spend=80.0,
            stay_duration_days=1.5,
            city_weights={"Belém": 1, "Santarém": 1},
        )
        self.assertIn("summary", result)
        self.assertGreater(result["summary"]["gross_spend"], 0)

    def test_dict_wrapper_success(self):
        result = calcular_impacto_economico(
            {
                "tourists": 10,
                "average_daily_spend": 50,
                "stay_duration_days": 1,
                "cities": [{"name": "Belém", "weight": 1}],
            }
        )
        self.assertIn("summary", result)

    def test_dict_wrapper_error(self):
        result = calcular_impacto_economico({"tourists": 10})  # faltam cidades
        self.assertIn("error", result)
