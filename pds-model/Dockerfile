# Dockerfile para Treinamento de RL (GPU Support)
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

WORKDIR /app

# Instala Poetry
RUN pip install poetry

# Copia arquivos de configuração do Poetry
COPY pds-model/pyproject.toml pds-model/poetry.lock* ./

# Configura Poetry e instala dependências
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copia código fonte
COPY pds-model/src /app/src
COPY .env /app/.env

ENV PYTHONPATH=/app/src

# O comando padrão é o Orquestrador de Treino
CMD ["python", "-m", "pds.orchestrator"]
