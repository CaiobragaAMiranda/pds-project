# Dockerfile compatível com GPU (CUDA)
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala Poetry
RUN pip install poetry

# Copia arquivos de configuração
COPY pds-data/pyproject.toml pds-data/poetry.lock* ./

# Configura Poetry e instala dependências (incluindo as de RL)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copia código fonte
COPY pds-data/src /app/src
COPY .env /app/.env

ENV PYTHONPATH=/app/src

# O comando padrão continua sendo a pipeline
CMD ["python", "-m", "pds.pipeline"]
