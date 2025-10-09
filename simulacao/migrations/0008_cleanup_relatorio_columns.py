from django.db import migrations


RELATORIO_EXTRA_COLUMNS = {
    "alternativas_sustentaveis",
    "atualizado_em",
    "economia_local_impacto",
    "emissao_co2_hospedagem",
    "emissao_co2_total",
    "emissao_co2_transporte",
    "impacto_ambiental",
    "metas_cop30_alinhamento",
    "pontuacao_sustentabilidade",
    "recomendacoes",
}


def drop_relatorio_columns(apps, schema_editor):
    Relatorio = apps.get_model("simulacao", "Relatorio")
    table_name = Relatorio._meta.db_table

    connection = schema_editor.connection
    introspection = connection.introspection

    with connection.cursor() as cursor:
        existing_columns = {col.name for col in introspection.get_table_description(cursor, table_name)}

    to_drop = existing_columns & RELATORIO_EXTRA_COLUMNS
    for column in sorted(to_drop):
        schema_editor.execute(
            f"ALTER TABLE {schema_editor.quote_name(table_name)} DROP COLUMN {schema_editor.quote_name(column)}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("simulacao", "0007_force_drop_simulacao_extra_columns"),
    ]

    operations = [
        migrations.RunPython(drop_relatorio_columns, migrations.RunPython.noop),
    ]
