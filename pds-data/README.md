# Pipeline de Dados - Predição de Quebra de Build
>
> [Universidade Federal do Ceará (UFC)](https://www.ufc.br/)\
> [Departamento de Computação (DC)](https://dc.ufc.br/pt/)\
> Curso: Bacharelado em Ciência de Dados\
> Disciplina: Engenharia de Sistemas Inteligentes (CK0444 – 2025.2)\
> Professor: Lincoln S. Rocha\
> Equipe: Caio Braga, Juan Victor, Vinicius Carvalho  

A pipeline de dados ([pipeline_data.py](./src/pds/pipeline_data.py)) foi desenvolvida para extrair (via [`pymetrix.py`](./src/pds/pymetrix.py)) e processar dados históricos de repositórios críticos do ecossistema Python (**Scikit-learn, Numpy e Keras**). 

O propósito desta pipeline é criar, de forma automática, um dataset rotulado para ser usado no treinamento de modelos de ML capazes de prever a **Quebra de Build (Build Failure)**. Diferente da predição de bugs tradicional, aqui o rótulo é definido objetivamente pelo status de falha (`failure` ou `error`) no sistema de Integração Contínua (CI/CD) do GitHub.

O projeto `pds-data` segue a seguinte estrutura:

```bash
pds-data
├── src
│   └── pds
│       ├── __init__.py
│       ├── pipeline_data.py  
│       └── pymetrix.py     
├── tests
│   └── __init__.py
├── pyproject.toml
└── README.md