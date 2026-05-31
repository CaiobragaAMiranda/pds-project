# Bootstrap do Projeto PDS

## 🛠️ Requisitos do Sistema
- Python >= 3.11 (Local) / Docker 24+
- Poetry
- Docker & Docker Compose
- NVIDIA Driver + NVIDIA Container Toolkit (para suporte a GPU/VRAM)
- Acesso à Internet (para API do GitHub)

## 🚀 Como Inicializar (Arquitetura Distribuída)
1. Configure o arquivo `.env` baseado no `.env.example` (Necessário `GITHUB_TOKEN`).
2. Execute na raiz: `docker-compose up --build -d`.
3. Acesse o Dashboard de Monitoramento: `http://localhost:8501`.
4. (Opcional) Acesse o banco de dados via Host: `localhost:5433` (User/Pass: postgres).

## 🧪 Como Testar e Desenvolver
1. **Testes Unitários:** Vá para `pds-data` e execute `$env:PYTHONPATH = "src"; python -m unittest discover tests`.
2. **Treinamento Supervisionado:** Vá para `pds-model` e execute `poetry run python -m pds.pipeline`. O sistema carregará os dados automaticamente do PostgreSQL (Arquivos CSV residuais são removidos pelo `cleanup.py`).
3. **Treinamento RL:** Vá para `pds-model` e execute `poetry run python -m pds.train`.

## 🧹 Como Limpar o Ambiente
1. Execute: `python cleanup.py` para remover clones temporários locais e datasets CSV obsoletos.
2. Execute: `docker-compose down -v` para remover containers e volumes de dados.

## 📌 Estado Atual do Sistema
- **Persistência:** PostgreSQL 15 (Relacional) com Engenharia de Features via SQL Views.
- **Extração:** Distribuída via Celery/Redis com 4 workers paralelos.
- **IA:** Ambiente Gymnasium configurado para Reinforcement Learning com suporte a GPU/CUDA.
- **Serviço:** `pds-service` integrado com o Agente RL (PPO). O sistema alterna automaticamente entre o modelo supervisionado (Random Forest) e o Agente RL (Bug Hunter) dependendo da presença do arquivo `.zip`. A inferência de RL utiliza contexto histórico diretamente do PostgreSQL.
