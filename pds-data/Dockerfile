# Dockerfile para o Worker de ETL
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configura diretório de trabalho
WORKDIR /app

# Instala Poetry
RUN pip install poetry

# Copia arquivos de configuração
COPY pds-data/pyproject.toml pds-data/poetry.lock* ./

# Configura Poetry para não criar env virtual e instala dependências
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copia o código fonte e o .env da raiz
COPY pds-data/src /app/src
COPY .env /app/.env

# Adiciona src ao PYTHONPATH
ENV PYTHONPATH=/app/src

# Comando para rodar a pipeline
ENTRYPOINT ["python", "-m", "pds.pipeline"]
