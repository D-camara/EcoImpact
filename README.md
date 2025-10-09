# EcoImpact

Aplicação Django para simular o impacto econômico e ambiental do turismo na COP 30.

## Visão geral do projeto

O **EcoImpact** é uma plataforma online desenvolvida em Django que permite simular o impacto econômico gerado pela chegada de turistas durante a COP30 no estado do Pará. O usuário pode ajustar variáveis como número de turistas, gasto médio, duração da estadia e cidades visitadas, obtendo relatórios interativos que mostram o potencial de movimentação financeira em diferentes cenários.

## Configuração rápida

1. Crie e ative um ambiente virtual.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Aplique as migrações (elas já criam as cidades padrão automaticamente):
   ```bash
   python manage.py migrate
   ```
4. (Opcional) Recarregue as fixtures caso queira substituir os dados existentes:
   ```bash
   python manage.py loaddata simulacao/fixtures/cidades_iniciais.json
   ```
5. Rode o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

> As fixtures garantem que todos tenham os mesmos registros independentes da `db.sqlite3` local.

## Testes automatizados

Execute a suíte de testes para validar as principais regras de negócio:

```bash
python manage.py test
```

## Sobre o banco de dados

- Continuamos utilizando **SQLite** (`db.sqlite3`) como banco padrão. Como ele está ignorado no Git, cada dev terá sua cópia local.
- Para manter os dados sincronizados entre branches, contamos com:
   - Migrações estruturais versionadas (`simulacao/migrations/`).
   - Migração de dados `0006_seed_cidades_padrao`, que cria automaticamente as cidades básicas sempre que o banco for inicializado.
   - Fixture `simulacao/fixtures/cidades_iniciais.json` para repopular dados facilmente quando necessário.
- Se precisar usar outro banco (ex.: produção), ajuste `DATABASES` em `ecoimpact/settings.py` conforme o ambiente.
