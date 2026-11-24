# Flask Payment Service

A Flask API for creating and retrieving payments. Payment processing is currently
backed by a mock provider.

## Requirements

- Python 3.13 or newer
- Poetry 2.x
- PostgreSQL

## Install

Install Python and Poetry if they are not already installed. From the project
directory, install the locked dependencies:

```powershell
poetry env use 3.13
poetry install
```

Poetry is the recommended way to run commands. To also use the direct `.venv`
commands shown below, configure Poetry to create the virtual environment inside
the project before installing:

```powershell
poetry config virtualenvs.in-project true --local
poetry env use 3.13
poetry install
```

Create a PostgreSQL role and database for the service. For example, in `psql`
as a PostgreSQL administrator:

```sql
CREATE USER payment_app WITH PASSWORD 'change-me';
CREATE DATABASE my_flask_db OWNER payment_app;
```

If you already have a PostgreSQL role, use that role instead and set the
matching credentials below.

Create a `.env` file in the project root and set the database connection
details. These values match the defaults in the application, except for the
password:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=my_flask_db
DB_USER=payment_app
DB_PASSWORD=change-me
SECRET_KEY=replace-with-a-random-secret
PAYMENT_PROVIDER_URL=http://localhost
SHOP_ACCOUNT=replace-with-your-shop=account-number
```

`SECRET_KEY`, `PAYMENT_PROVIDER_URL`, and `SHOP_ACCOUNT` are available to the
application configuration. The payment provider implementation is currently a
mock and does not make an external request.

## Create or update the database schema

The project includes an initial migration that creates the `payments` table.
With PostgreSQL running and `.env` configured, apply all migrations with:

```powershell
poetry run flask --app run db upgrade
```

When models change, create a migration and then apply it:

```powershell
poetry run flask --app run db migrate -m "Describe the schema change"
poetry run flask --app run db upgrade
```

Alternatively, run the Flask CLI directly from `.venv` without activating it:

```powershell
.\.venv\Scripts\python.exe -m flask --app run db upgrade
```

For new migrations:

```powershell
.\.venv\Scripts\python.exe -m flask --app run db migrate -m "Describe the schema change"
.\.venv\Scripts\python.exe -m flask --app run db upgrade
```

## Run the service

Start the Flask development server with Poetry:

```powershell
poetry run python run.py
```

Or run it directly from `.venv`:

```powershell
.\.venv\Scripts\python.exe run.py
```

The service listens at `http://127.0.0.1:5000`. The health endpoint is
`GET /`. The payment endpoint is `POST /api/payments/pay`; requests must include
an `Authorization` header and a JSON body containing `cart_id`, `amount`, and
`provider_token`.

## Run tests

The unit tests use SQLite and mocked payment services, so PostgreSQL does not
need to be running. Run the full suite with Poetry:

```powershell
poetry run pytest
```

Alternatively, run the tests directly from the project `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest
```