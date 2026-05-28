# Serviço do Sistema de PDS
>
> [Universidade Federal do Ceará (UFC)](https://www.ufc.br/)\
> [Departamento de Computação (DC)](https://dc.ufc.br/pt/)\
> Curso: Bacharelado em Ciência de Dados\
> Disciplina: Engenharia de Sistemas Inteligentes (CK0444 – 2025.2)\
> Professor: [Lincoln S. Rocha](http://lattes.cnpq.br/0656977742590515)\
> E-mail: <lincoln@dc.ufc.br>
>

O serviço de Predição de Defeito de Software (PDS) faz uso do modelo de ML de melhor desempenho definido pela pipeline de modelos. Ele recebe como entrada uma lista de de valores para métricas extraídas de um arquivo `.py` (`LOC`, `COM`, `BLK`, `NOF`, `NOC`, `APF`, `AMC`, `NER`, `NEH`, `CYC` e `MAD`) e retorna uma lista unitária indicando se, para aquelas métricas, o arquivo está propenso (`[1]`) ou não (`[0]`) a conter um bug. O código abaixo acessa o serviço de do Sistema de PDS:

```python
import requests

data_tuple = [559, 47, 70, 9, 2, 0.89, 3.0, 3, 2, 48, 13] #buggy
data_tuple = [float(element) for element in data_tuple]
response = requests.post('http://127.0.0.1:5000/predict', json={'data_tuple': data_tuple})
print(response.json())
```

O projeto `pds-service` segue a seguinte estrutura:

```bash
pds-service
├── src
│   └── pds
│       ├── __init__.py
│       ├── app.py
│       └── service.py
├── tests
│   ├── __init__.py
│   └── test_app.py
├── pyproject.toml
├── README.md
└── service_client.ipynb
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

3. Inicialize o serviço:

```bash
poetry run python -u -m pds.app
```

4. Teste o serviço:

```bash
poetry run python -u -m unittest discover tests
```