# PokéAPI — Suíte de Testes Automatizados

**Disciplina:** Qualidade de Software — INATEL  
**Professor:** Christopher Lima  
**Sistema sob Teste (SUT):** [PokéAPI v2](https://pokeapi.co/api/v2/)  
**Ferramenta:** pytest + requests + Locust  

---

## Estrutura do Projeto

```
pokeapi_tests/
├── tests/
│   ├── conftest.py          # Fixtures compartilhadas
│   ├── test_pokeapi.py      # TC-001 a TC-020 (testes funcionais)
│   └── test_performance.py  # PERF-001 e PERF-002 (Locust — bônus)
├── reports/                 # Relatórios gerados (criado automaticamente)
│   └── report.json          # Relatório JSON gerado pelo pytest
├── pytest.ini               # Configurações do pytest
├── requirements.txt         # Dependências
└── README.md
```

---

## Pré-requisitos

- Python 3.10 ou superior
- Conexão com a internet (API pública)

---

## Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd pokeapi_tests

# (Opcional) Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Instale as dependências
pip install -r requirements.txt
```

---

## Execução dos Testes Funcionais

### Execução padrão — gera relatório JSON automaticamente
```bash
pytest tests/test_pokeapi.py
```
O relatório é salvo em `reports/report.json` automaticamente (configurado no `pytest.ini`).

### Apenas caminho feliz (TC-001 a TC-010)
```bash
pytest tests/test_pokeapi.py::TestCaminhoFeliz
```

### Apenas dados inválidos (TC-011 a TC-020)
```bash
pytest tests/test_pokeapi.py::TestDadosInvalidos
```

### Com relatório HTML adicional (opcional)
```bash
pytest tests/test_pokeapi.py --html=reports/report.html --self-contained-html
```

---

## Estrutura do Relatório JSON (`reports/report.json`)

O relatório gerado pelo `pytest-json-report` segue esta estrutura:

```json
{
  "created": 1234567890.0,
  "duration": 8.71,
  "exitcode": 0,
  "root": "C:/projeto/pokeapi_tests",
  "environment": { "Python": "3.10.11", "Platform": "Windows-10" },
  "summary": {
    "passed": 20,
    "failed": 0,
    "total": 20,
    "collected": 20
  },
  "tests": [
    {
      "nodeid": "tests/test_pokeapi.py::TestCaminhoFeliz::test_TC001_busca_pokemon_por_id_valido",
      "outcome": "passed",
      "duration": 0.45,
      "keywords": ["TC001", "TestCaminhoFeliz"]
    }
  ]
}
```

Campos principais por teste: `nodeid`, `outcome` (passed/failed), `duration` (segundos), e em caso de falha: `longrepr` com o traceback completo.

---

## Execução dos Testes de Performance (Bônus)

### PERF-001 — Teste de Carga (20 usuários, 30 segundos)
```bash
locust -f tests/test_performance.py --headless -u 20 -r 5 -t 30s --host https://pokeapi.co --html reports/locust_carga.html --csv reports/locust_carga
```

### PERF-002 — Teste de Estresse (50 usuários, 30 segundos)
```bash
locust -f tests/test_performance.py --headless -u 50 -r 10 -t 30s --host https://pokeapi.co --html reports/locust_stress.html --csv reports/locust_stress
```

### Interface web interativa (dashboard em http://localhost:8089)
```bash
locust -f tests/test_performance.py --host https://pokeapi.co
```

---

## Casos de Teste

### Dados válidos — Caminho Feliz (TC-001 a TC-010)

| ID | Nome | Endpoint |
|----|------|----------|
| TC-001 | Busca de Pokémon por ID válido | GET /pokemon/1 |
| TC-002 | Busca de Pokémon por nome válido | GET /pokemon/pikachu |
| TC-003 | ID limite máximo (valor-limite) | GET /pokemon/1025 |
| TC-004 | Listagem paginada padrão | GET /pokemon?limit=10&offset=0 |
| TC-005 | Paginação com offset no meio | GET /pokemon?limit=5&offset=20 |
| TC-006 | Consulta de tipo por nome | GET /type/fire |
| TC-007 | Consulta de habilidade por nome | GET /ability/overgrow |
| TC-008 | Consulta de movimento por nome | GET /move/tackle |
| TC-009 | Consulta de geração válida | GET /generation/1 |
| TC-010 | Tempo de resposta < 3 s | GET /pokemon/25 |

### Dados inválidos / Inoportunos (TC-011 a TC-020)

| ID | Nome | Dado Inválido |
|----|------|---------------|
| TC-011 | ID inexistente além do limite | /pokemon/99999 |
| TC-012 | Nome de Pokémon inexistente | /pokemon/naoexiste |
| TC-013 | ID zero (abaixo do mínimo) | /pokemon/0 |
| TC-014 | ID negativo | /pokemon/-1 |
| TC-015 | limit=0 na paginação | ?limit=0 |
| TC-016 | offset negativo | ?offset=-5 |
| TC-017 | Tipo inexistente | /type/fogo |
| TC-018 | Geração além do limite | /generation/10 |
| TC-019 | limit com valor string | ?limit=abc |
| TC-020 | Endpoint completamente inválido | /naoexiste/rota |

> **Nota TC-020:** A PokéAPI retorna HTTP 400 (Bad Request) para rotas desconhecidas,
> comportamento mais restritivo que um 404 — ambos são aceitos pelo teste.

---

## Uso de IA

Este projeto utilizou assistência de IA (Claude — Anthropic) como apoio para:
- Estruturação do plano de testes
- Revisão de sintaxe e organização do código

Todo o código foi revisado e compreendido pelos integrantes do grupo.  
A autoria e entendimento do trabalho são dos alunos.