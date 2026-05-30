# Bootstrap do Projeto PDS

## 🛠️ Requisitos do Sistema
- Python >= 3.11
- Poetry
- Acesso à Internet (para API do GitHub)
- Docker (futuramente para PostgreSQL)

## 🚀 Como Inicializar
1. Navegue até a pasta de um dos módulos (ex: `pds-data`).
2. Execute `poetry install`.
3. Para rodar a pipeline de dados: `poetry run python -m pds.pipeline <TOKEN_GITHUB>`.

## 🧪 Como Testar
1. Vá para a pasta do módulo (ex: `pds-data`).
2. Execute: `$env:PYTHONPATH = "src"; python -m unittest discover tests`.

## 🧹 Como Limpar o Ambiente
1. Execute: `python cleanup.py` para remover dependências vendadas e arquivos temporários de dados.

## 📌 Estado Atual do Sistema
- O sistema utiliza arquivos CSV para armazenamento.
- A extração é manual via script de pipeline.
- O modelo de ML é gerado localmente em formato `.pkl`.
