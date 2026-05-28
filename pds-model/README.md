# Pipeline de Modelos para o Sistema de PDS
>
> [Universidade Federal do Ceará (UFC)](https://www.ufc.br/)\
> [Departamento de Computação (DC)](https://dc.ufc.br/pt/)\
> Curso: Bacharelado em Ciência de Dados\
> Disciplina: Engenharia de Sistemas Inteligentes (CK0444 – 2025.2)\
> Professor: [Lincoln S. Rocha](http://lattes.cnpq.br/0656977742590515)\
> E-mail: <lincoln@dc.ufc.br>
>

A pipeline de modelos ([pipeline.py](./pipeline.py)) foi escrita para realizar a tarefa de escolher o modelo de ML de melhor desempenho para a tarefa de Predição de Defeito de Software (PDS) por meio de um experimento de desempenho. A pipeline usa como entrada o dataset rotulado gerado pela pipeline de dados e gera como saída o modelo de ML de melhor performance. O projeto `pds-model` segue a seguinte estrutura:

```bash
pds-model
├── src
│   └── pds
│       ├── __init__.py
│       └── pipeline.py
├── tests
│   └── __init__.py
├── pyproject.toml
└── README.md
```

Instruções para execução da pipeline de modelos são dadas a seguir:

1. Instale o Poetry:

```bash
pip install poetry
```

2. Instale as dependências necessárias para rodar a pipeline de modelos:

```bash
poetry install
```

3. Execute a pipeline e dados:

```bash
poetry run python -u -m pds.pipeline <Dataset File Path>
```
