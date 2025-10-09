from django.db import migrations


SIMULACAO_EXTRA_COLUMNS = {
    "atividades_sustentaveis",
    "cenario",
    "compensacao_carbono",
    "data_fim",
    "data_viagem",
    "duracao_estadia",
    "gasto_medio",
    "meio_transporte_principal",
    "numero_turistas",
    "orcamento",
    "status",
    "tipo_hospedagem",
    "turista_id",
}


def drop_simulacao_columns(apps, schema_editor):
    Simulacao = apps.get_model("simulacao", "Simulacao")
    table_name = Simulacao._meta.db_table

    connection = schema_editor.connection
    introspection = connection.introspection

    with connection.cursor() as cursor:
        existing_columns = {col.name for col in introspection.get_table_description(cursor, table_name)}

    to_drop = existing_columns & SIMULACAO_EXTRA_COLUMNS
    for column in sorted(to_drop):
        schema_editor.execute(
            f"ALTER TABLE {schema_editor.quote_name(table_name)} DROP COLUMN {schema_editor.quote_name(column)}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("simulacao", "0006_seed_cidades_padrao"),
    ]

    operations = [
        migrations.RunPython(drop_simulacao_columns, migrations.RunPython.noop),
    ]
