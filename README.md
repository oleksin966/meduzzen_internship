# meduzzen_internship
## Prerequisites

Before starting the application, ensure you have the following installed:

- Python (version 3.8)
- Pip (version 20.2.1)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/oleksin966/meduzzen_internship.git
    ```

2. Navigate to the project directory:
    ```bash
    cd meduzzen_internship
    ```

3. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Unix/Mac
    # or
    .\venv\Scripts\activate   # For Windows
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. To start the application, run the following command:
```bash
python app/main.py
```

## Running the Application with Docker Compose

1. Make sure to configure your environment by creating a .env file with the required variables before running Docker Compose.

To build and start the application using Docker Compose, run the following command:
```bash
docker-compose up --build
```

For subsequent runs, you can use:
```bash
docker-compose up
```

You can access the API endpoints using a web browser.

## Applying Migrations with Alembic

1. If you haven't already installed Alembic, you can do so using pip:

```bash
pip install alembic
```

2. Before using Alembic, you need to configure it to connect to your database. This involves creating an `alembic.ini` file and configuring it with your database connection details:

```bash
sqlalchemy.url = driver://{db_user}:{db_password}@{db_host}/{db_name}
```

3. Run the `alembic revision` command with the `--autogenerate` option to automatically generate migration scripts based on changes in your SQLAlchemy models:

```bash
alembic revision --autogenerate -m "Description of the migration"
```

4. Apply the generated migrations to the database using the alembic upgrade command:

```bash
alembic upgrade head
```

5. Optionally, provide instructions on how to rollback migrations if needed. This can be done using the `alembic downgrade` command.

```bash
alembic downgrade -1
```