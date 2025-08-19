"""Serviços de simulação.

Implementa a lógica de cálculo do impacto econômico com base em:
 - número de turistas
 - gasto médio diário
 - duração da estadia (dias)
 - cidades visitadas (com pesos, multiplicadores e taxas de *leakage*)

O desenho foi feito para ser flexível: novos campos podem ser adicionados às
`CityConfig` ou `ScenarioInput` sem quebrar o contrato externo, e existe uma
função de *wrapper* (`calcular_impacto_economico`) que aceita um dicionário
genérico (útil para requests Django / JSON) convertendo para objetos tipados.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from math import isfinite
from typing import Any, Dict, Iterable, List

# ======================================================================
# Data Classes de Configuração
# ======================================================================


@dataclass(frozen=True)
class CityConfig:
    """Parâmetros específicos de uma cidade.

    Atributos
    ---------
    name: Nome da cidade.
    weight: Peso relativo da cidade na distribuição dos "tourist-days".
    daily_spend_multiplier: Multiplicador aplicado ao gasto médio diário base.
    fixed_adjustment: Ajuste absoluto (R$) adicionado ao gasto diário após o multiplicador.
    leakage_rate: Fração (0-1) do gasto bruto que não é retida localmente.
    """

    name: str
    weight: float = 1.0
    daily_spend_multiplier: float = 1.0
    fixed_adjustment: float = 0.0
    leakage_rate: float = 0.0

    def validate(self) -> None:
        if self.weight <= 0:
            raise ValueError(f"City {self.name}: weight deve ser > 0")
        if self.daily_spend_multiplier <= 0:
            raise ValueError(
                f"City {self.name}: daily_spend_multiplier deve ser > 0"
            )
        if not (0 <= self.leakage_rate < 1):
            raise ValueError(f"City {self.name}: leakage_rate deve estar em [0,1)")


@dataclass(frozen=True)
class ScenarioInput:
    """Representa um cenário de simulação.

    tourists: número de turistas (int >= 0)
    average_daily_spend: gasto médio diário base (R$) por turista
    stay_duration_days: duração média da estadia (dias)
    cities: lista de `CityConfig`
    inflation_factor: multiplicador final (ex: 1.05 para +5%)
    global_leakage_rate: fração adicional (0-1) descontada após leakages por cidade
    scenario_name: identificador opcional
    """

    tourists: int
    average_daily_spend: float
    stay_duration_days: float
    cities: List[CityConfig]
    inflation_factor: float = 1.0
    global_leakage_rate: float = 0.0
    scenario_name: str | None = None

    def validate(self) -> None:
        if self.tourists < 0:
            raise ValueError("tourists deve ser >= 0")
        if self.average_daily_spend < 0:
            raise ValueError("average_daily_spend deve ser >= 0")
        if self.stay_duration_days < 0:
            raise ValueError("stay_duration_days deve ser >= 0")
        if not self.cities:
            raise ValueError("Lista de cities não pode estar vazia")
        if self.inflation_factor <= 0:
            raise ValueError("inflation_factor deve ser > 0")
        if not (0 <= self.global_leakage_rate < 1):
            raise ValueError("global_leakage_rate deve estar em [0,1)")
        for c in self.cities:
            c.validate()
        for v in (self.tourists, self.average_daily_spend, self.stay_duration_days):
            if not isfinite(v):
                raise ValueError("Valores numéricos devem ser finitos")


# ======================================================================
# Funções núcleo
# ======================================================================


def _normalize_weights(cities: Iterable[CityConfig]) -> Dict[str, float]:
    total = sum(c.weight for c in cities)
    if total <= 0:
        raise ValueError("Soma dos pesos das cidades deve ser > 0")
    return {c.name: c.weight / total for c in cities}


def compute_economic_impact(scenario: ScenarioInput) -> Dict[str, Any]:
    """Calcula impacto econômico agregado e por cidade.

    Retorna dicionário serializável
    (adequado para JSON / persistência em JSONField).
    """

    scenario.validate()

    # Cenário trivial -> tudo zero
    if (
        scenario.tourists == 0
        or scenario.stay_duration_days == 0
        or scenario.average_daily_spend == 0
    ):
        return {
            "scenario": scenario.scenario_name,
            "inputs": asdict(scenario),
            "summary": {
                "gross_spend": 0.0,
                "net_spend_after_city_leakage": 0.0,
                "net_spend_after_global_leakage": 0.0,
                "retention_rate_effective": 0.0,
            },
            "cities": [],
        }

    weight_map = _normalize_weights(scenario.cities)
    base_daily = scenario.average_daily_spend
    total_tourist_days = scenario.tourists * scenario.stay_duration_days

    cities_output: List[Dict[str, Any]] = []
    gross_total = 0.0
    net_after_city_total = 0.0

    for city in scenario.cities:
        share = weight_map[city.name]
        city_tourist_days = total_tourist_days * share

        # Gasto diário ajustado (multiplicador + ajuste fixo)
        adj_daily = (base_daily * city.daily_spend_multiplier) + city.fixed_adjustment
        city_gross = adj_daily * city_tourist_days
        city_leakage = city_gross * city.leakage_rate
        city_net = city_gross - city_leakage

        gross_total += city_gross
        net_after_city_total += city_net

        cities_output.append(
            {
                "city": city.name,
                "weight_share": share,
                "tourist_days": city_tourist_days,
                "adjusted_daily_spend": adj_daily,
                "gross_spend": city_gross,
                "leakage_rate_city": city.leakage_rate,
                "leakage_amount_city": city_leakage,
                "net_spend_after_city_leakage": city_net,
            }
        )

    # Ajuste inflação
    gross_total *= scenario.inflation_factor
    net_after_city_total *= scenario.inflation_factor

    # Leakage global adicional
    global_leakage_amount = net_after_city_total * scenario.global_leakage_rate
    net_after_global = net_after_city_total - global_leakage_amount

    retention_rate_effective = (
        net_after_global / gross_total if gross_total > 0 else 0.0
    )

    return {
        "scenario": scenario.scenario_name,
        "inputs": {
            "tourists": scenario.tourists,
            "average_daily_spend": scenario.average_daily_spend,
            "stay_duration_days": scenario.stay_duration_days,
            "inflation_factor": scenario.inflation_factor,
            "global_leakage_rate": scenario.global_leakage_rate,
        },
        "summary": {
            "gross_spend": gross_total,
            "net_spend_after_city_leakage": net_after_city_total,
            "global_leakage_amount": global_leakage_amount,
            "net_spend_after_global_leakage": net_after_global,
            "retention_rate_effective": retention_rate_effective,
        },
        "cities": cities_output,
    }


def simulate_batch(scenarios: List[ScenarioInput]) -> List[Dict[str, Any]]:
    """Executa múltiplos cenários em sequência."""

    return [compute_economic_impact(s) for s in scenarios]


# ======================================================================
# Helper / Wrapper público para integração com views
# ======================================================================


def quick_scenario(
    tourists: int,
    average_daily_spend: float,
    stay_duration_days: float,
    city_weights: Dict[str, float],
    city_multipliers: Dict[str, float] | None = None,
    city_fixed_adjustments: Dict[str, float] | None = None,
    city_leakage_rates: Dict[str, float] | None = None,
    inflation_factor: float = 1.0,
    global_leakage_rate: float = 0.0,
    scenario_name: str | None = None,
) -> Dict[str, Any]:
    """Cria e computa rapidamente um cenário via dicionários simples."""

    cities = []
    for name, weight in city_weights.items():
        cities.append(
            CityConfig(
                name=name,
                weight=weight,
                daily_spend_multiplier=(city_multipliers or {}).get(name, 1.0),
                fixed_adjustment=(city_fixed_adjustments or {}).get(name, 0.0),
                leakage_rate=(city_leakage_rates or {}).get(name, 0.0),
            )
        )
    scenario = ScenarioInput(
        tourists=tourists,
        average_daily_spend=average_daily_spend,
        stay_duration_days=stay_duration_days,
        cities=cities,
        inflation_factor=inflation_factor,
        global_leakage_rate=global_leakage_rate,
        scenario_name=scenario_name,
    )
    return compute_economic_impact(scenario)


def calcular_impacto_economico(parametros: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper genérico usado por camadas superiores (ex: view / API).

    Aceita um dicionário com chaves esperadas (snake_case). Exemplo mínimo:

        {
          "tourists": 50000,
          "average_daily_spend": 650.0,
          "stay_duration_days": 5.5,
          "cities": [
             {"name": "Belém", "weight": 3, "daily_spend_multiplier": 1.1, "leakage_rate": 0.08},
             {"name": "Santarém", "weight": 1.5, "daily_spend_multiplier": 0.95, "leakage_rate": 0.05}
          ],
          "inflation_factor": 1.04,
          "global_leakage_rate": 0.03,
          "scenario_name": "Base COP30"
        }
    """

    try:
        raw_cities = parametros.get("cities") or []
        if not isinstance(raw_cities, list) or not raw_cities:
            raise ValueError("'cities' deve ser lista não vazia")

        cities: List[CityConfig] = []
        for item in raw_cities:
            if not isinstance(item, dict):
                raise ValueError("Cada cidade deve ser um dict")
            cities.append(
                CityConfig(
                    name=str(item.get("name")),
                    weight=float(item.get("weight", 1.0)),
                    daily_spend_multiplier=float(
                        item.get("daily_spend_multiplier", 1.0)
                    ),
                    fixed_adjustment=float(item.get("fixed_adjustment", 0.0)),
                    leakage_rate=float(item.get("leakage_rate", 0.0)),
                )
            )

        scenario = ScenarioInput(
            tourists=int(parametros.get("tourists", 0)),
            average_daily_spend=float(parametros.get("average_daily_spend", 0.0)),
            stay_duration_days=float(parametros.get("stay_duration_days", 0.0)),
            cities=cities,
            inflation_factor=float(parametros.get("inflation_factor", 1.0)),
            global_leakage_rate=float(parametros.get("global_leakage_rate", 0.0)),
            scenario_name=parametros.get("scenario_name"),
        )

        return compute_economic_impact(scenario)
    except Exception as exc:  # Captura ampla para uniformizar retorno (pode logar depois)
        return {"error": str(exc), "ok": False}

