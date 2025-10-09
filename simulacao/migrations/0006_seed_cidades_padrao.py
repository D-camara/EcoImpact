from decimal import Decimal

from django.db import migrations


CIDADES_INICIAIS = [
    {
        "nome": "Belém",
        "populacao": 1499641,
        "pib_per_capita": Decimal("35987.20"),
    },
    {
        "nome": "Santarém",
        "populacao": 308339,
        "pib_per_capita": Decimal("27645.10"),
    },
    {
        "nome": "Marabá",
        "populacao": 283542,
        "pib_per_capita": Decimal("31200.00"),
    },
    {
        "nome": "Altamira",
        "populacao": 115969,
        "pib_per_capita": Decimal("29875.50"),
    },
]


def criar_cidades(apps, schema_editor):
    Cidade = apps.get_model("simulacao", "Cidade")

    for dados in CIDADES_INICIAIS:
        Cidade.objects.update_or_create(
            nome=dados["nome"],
            defaults={
                "populacao": dados["populacao"],
                "pib_per_capita": dados["pib_per_capita"],
            },
        )


def remover_cidades(apps, schema_editor):
    Cidade = apps.get_model("simulacao", "Cidade")
    nomes = [cidade["nome"] for cidade in CIDADES_INICIAIS]
    Cidade.objects.filter(nome__in=nomes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("simulacao", "0005_cleanup_remaining_columns"),
    ]

    operations = [
        migrations.RunPython(criar_cidades, remover_cidades),
    ]
