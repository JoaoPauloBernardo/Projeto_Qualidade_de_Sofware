"""
test_pokeapi.py — Suíte de testes automatizados da PokéAPI
Disciplina : Qualidade de Software — INATEL
Professor  : Christopher Lima
Ferramenta : pytest + requests

Execução:
    pytest tests/test_pokeapi.py -v --html=report.html --self-contained-html

Casos de teste:
    TC-001 a TC-010 — Dados válidos / Caminho Feliz
    TC-011 a TC-020 — Dados inválidos / Inoportunos
"""

import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pytest
import requests

BASE_URL = "https://pokeapi.co/api/v2"
TIMEOUT  = 10  # segundos por requisição


# ──────────────────────────────────────────────────────────────────────────────
# DADOS DE TESTE (separados do código conforme boas práticas)
# ──────────────────────────────────────────────────────────────────────────────

VALID_POKEMON_ID   = 1          # Bulbasaur
VALID_POKEMON_NAME = "pikachu"
MAX_POKEMON_ID     = 1025       # Iron Leaves — último ID documentado
VALID_TYPE         = "fire"
VALID_ABILITY      = "overgrow"
VALID_MOVE         = "tackle"
VALID_GENERATION   = 1

INVALID_POKEMON_ID   = 99999
INVALID_POKEMON_NAME = "naoexiste"
ZERO_ID              = 0
NEGATIVE_ID          = -1
INVALID_TYPE         = "fogo"       # Português — inexistente na API
INVALID_GENERATION   = 10           # Apenas gerações 1-9 existem
RESPONSE_TIME_LIMIT  = 3.0          # segundos


# ──────────────────────────────────────────────────────────────────────────────
# TC-001 a TC-010 — CAMINHO FELIZ (dados válidos)
# ──────────────────────────────────────────────────────────────────────────────

class TestCaminhoFeliz:
    """TC-001 a TC-010: cenários com entradas corretas e fluxos de sucesso."""

    def test_TC001_busca_pokemon_por_id_valido(self):
        """TC-001: GET /pokemon/1 deve retornar HTTP 200 com id=1 e name='bulbasaur'."""
        response = requests.get(f"{BASE_URL}/pokemon/{VALID_POKEMON_ID}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 200, (
            f"TC-001 FALHOU: esperado 200, recebido {response.status_code}"
        )
        data = response.json()
        assert data["id"] == 1,               "TC-001: campo 'id' deve ser 1"
        assert data["name"] == "bulbasaur",   "TC-001: campo 'name' deve ser 'bulbasaur'"
        assert "types" in data,               "TC-001: campo 'types' deve existir"
        assert isinstance(data["types"], list), "TC-001: 'types' deve ser uma lista"

    def test_TC002_busca_pokemon_por_nome_valido(self):
        """TC-002: GET /pokemon/pikachu deve retornar HTTP 200 com id=25."""
        response = requests.get(f"{BASE_URL}/pokemon/{VALID_POKEMON_NAME}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 25,              "TC-002: id do pikachu deve ser 25"
        assert data["name"] == "pikachu",     "TC-002: name deve ser 'pikachu'"
        assert "base_experience" in data,     "TC-002: campo 'base_experience' deve existir"
        assert "abilities" in data,           "TC-002: campo 'abilities' deve existir"

    def test_TC003_pokemon_id_limite_maximo(self):
        """TC-003: GET /pokemon/1025 (valor-limite máximo) deve retornar HTTP 200."""
        response = requests.get(f"{BASE_URL}/pokemon/{MAX_POKEMON_ID}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 200, (
            f"TC-003 FALHOU: ID {MAX_POKEMON_ID} deve existir, recebido {response.status_code}"
        )
        data = response.json()
        assert data["id"] == MAX_POKEMON_ID, f"TC-003: id deve ser {MAX_POKEMON_ID}"

    def test_TC004_listagem_paginada_padrao(self):
        """TC-004: GET /pokemon?limit=10&offset=0 deve retornar 10 resultados."""
        response = requests.get(
            f"{BASE_URL}/pokemon", params={"limit": 10, "offset": 0}, timeout=TIMEOUT, verify=False
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data,                    "TC-004: campo 'results' deve existir"
        assert len(data["results"]) == 10,           "TC-004: deve retornar exatamente 10 itens"
        assert "count" in data,                      "TC-004: campo 'count' deve existir"
        assert data["count"] > 0,                    "TC-004: count deve ser positivo"
        assert all("name" in p for p in data["results"]), \
            "TC-004: cada item deve ter campo 'name'"

    def test_TC005_paginacao_com_offset_no_meio(self):
        """TC-005: GET /pokemon?limit=5&offset=20 deve retornar 5 itens com offset correto."""
        response = requests.get(
            f"{BASE_URL}/pokemon", params={"limit": 5, "offset": 20}, timeout=TIMEOUT, verify=False
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 5,  "TC-005: deve retornar exatamente 5 itens"
        assert data["count"] > 0,          "TC-005: count total deve ser positivo"
        # O next link deve conter offset=25
        if data.get("next"):
            assert "offset=25" in data["next"], "TC-005: próximo offset deve ser 25"

    def test_TC006_consulta_tipo_por_nome(self):
        """TC-006: GET /type/fire deve retornar HTTP 200 com name='fire'."""
        response = requests.get(f"{BASE_URL}/type/{VALID_TYPE}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "fire",              "TC-006: name deve ser 'fire'"
        assert "damage_relations" in data,          "TC-006: damage_relations deve existir"
        assert "pokemon" in data,                   "TC-006: lista de pokemon do tipo deve existir"
        assert isinstance(data["pokemon"], list),   "TC-006: pokemon deve ser lista"

    def test_TC007_consulta_habilidade_por_nome(self):
        """TC-007: GET /ability/overgrow deve retornar HTTP 200 com name='overgrow'."""
        response = requests.get(f"{BASE_URL}/ability/{VALID_ABILITY}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "overgrow",        "TC-007: name deve ser 'overgrow'"
        assert "effect_entries" in data,          "TC-007: effect_entries deve existir"
        assert "pokemon" in data,                 "TC-007: lista de pokemon deve existir"

    def test_TC008_consulta_movimento_por_nome(self):
        """TC-008: GET /move/tackle deve retornar HTTP 200 com campos obrigatórios."""
        response = requests.get(f"{BASE_URL}/move/{VALID_MOVE}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "tackle",         "TC-008: name deve ser 'tackle'"
        assert "power" in data,                  "TC-008: campo 'power' deve existir"
        assert "accuracy" in data,               "TC-008: campo 'accuracy' deve existir"
        assert "type" in data,                   "TC-008: campo 'type' deve existir"

    def test_TC009_consulta_geracao_valida(self):
        """TC-009: GET /generation/1 deve retornar HTTP 200 com name='generation-i'."""
        response = requests.get(
            f"{BASE_URL}/generation/{VALID_GENERATION}", timeout=TIMEOUT, verify=False
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "generation-i",       "TC-009: name deve ser 'generation-i'"
        assert "pokemon_species" in data,            "TC-009: pokemon_species deve existir"
        assert isinstance(data["pokemon_species"], list), \
            "TC-009: pokemon_species deve ser lista"
        assert len(data["pokemon_species"]) > 0,    "TC-009: deve ter ao menos um Pokémon"

    def test_TC010_tempo_de_resposta_aceitavel(self):
        """TC-010: GET /pokemon/25 deve responder em menos de 3 segundos."""
        inicio = time.time()
        response = requests.get(f"{BASE_URL}/pokemon/25", timeout=TIMEOUT, verify=False)
        elapsed = time.time() - inicio

        assert response.status_code == 200, "TC-010: deve retornar HTTP 200"
        assert elapsed < RESPONSE_TIME_LIMIT, (
            f"TC-010 FALHOU: resposta levou {elapsed:.2f}s "
            f"(limite: {RESPONSE_TIME_LIMIT}s)"
        )


# ──────────────────────────────────────────────────────────────────────────────
# TC-011 a TC-020 — DADOS INVÁLIDOS / INOPORTUNOS
# ──────────────────────────────────────────────────────────────────────────────

class TestDadosInvalidos:
    """TC-011 a TC-020: cenários com entradas incorretas, limites e dados malformados."""

    def test_TC011_id_pokemon_inexistente(self):
        """TC-011: GET /pokemon/99999 (ID além do limite) deve retornar HTTP 404."""
        response = requests.get(
            f"{BASE_URL}/pokemon/{INVALID_POKEMON_ID}", timeout=TIMEOUT, verify=False
        )

        assert response.status_code == 404, (
            f"TC-011 FALHOU: esperado 404, recebido {response.status_code}"
        )
        # Não deve ser erro interno do servidor
        assert response.status_code != 500, "TC-011: não deve retornar HTTP 500"

    def test_TC012_nome_pokemon_inexistente(self):
        """TC-012: GET /pokemon/naoexiste deve retornar HTTP 404."""
        response = requests.get(
            f"{BASE_URL}/pokemon/{INVALID_POKEMON_NAME}", timeout=TIMEOUT, verify=False
        )

        assert response.status_code == 404, (
            f"TC-012 FALHOU: esperado 404, recebido {response.status_code}"
        )

    def test_TC013_id_zero_fora_do_dominio(self):
        """TC-013: GET /pokemon/0 (valor-limite abaixo do mínimo) deve retornar HTTP 404."""
        response = requests.get(f"{BASE_URL}/pokemon/{ZERO_ID}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 404, (
            f"TC-013 FALHOU: ID 0 está fora do domínio válido (1–1025), "
            f"esperado 404, recebido {response.status_code}"
        )

    def test_TC014_id_negativo(self):
        """TC-014: GET /pokemon/-1 (ID negativo) deve retornar HTTP 404."""
        response = requests.get(
            f"{BASE_URL}/pokemon/{NEGATIVE_ID}", timeout=TIMEOUT, verify=False
        )

        assert response.status_code == 404, (
            f"TC-014 FALHOU: ID negativo inválido, esperado 404, "
            f"recebido {response.status_code}"
        )
        assert response.status_code != 500, "TC-014: não deve retornar HTTP 500"

    def test_TC015_paginacao_limit_zero(self):
        """TC-015: GET /pokemon?limit=0 — comportamento com limit inválido."""
        response = requests.get(
            f"{BASE_URL}/pokemon", params={"limit": 0}, timeout=TIMEOUT, verify=False
        )

        # A API pode retornar 400 (inválido) ou 200 com lista vazia — ambos aceitáveis
        assert response.status_code in (200, 400), (
            f"TC-015 FALHOU: esperado 200 ou 400, recebido {response.status_code}"
        )
        assert response.status_code != 500, "TC-015: não deve retornar HTTP 500"

        if response.status_code == 200:
            data = response.json()
            assert "results" in data, "TC-015: campo 'results' deve existir mesmo com limit=0"

    def test_TC016_paginacao_offset_negativo(self):
        """TC-016: GET /pokemon?limit=10&offset=-5 — offset negativo é dado inoportuno."""
        response = requests.get(
            f"{BASE_URL}/pokemon", params={"limit": 10, "offset": -5}, timeout=TIMEOUT, verify=False
        )

        # A API pode tratar graciosamente (200) ou rejeitar (400) — sem 500
        assert response.status_code in (200, 400), (
            f"TC-016 FALHOU: esperado 200 ou 400, recebido {response.status_code}"
        )
        assert response.status_code != 500, "TC-016: não deve retornar HTTP 500"

    def test_TC017_tipo_pokemon_inexistente(self):
        """TC-017: GET /type/fogo — tipo em português não existe na API (inglês apenas)."""
        response = requests.get(f"{BASE_URL}/type/{INVALID_TYPE}", timeout=TIMEOUT, verify=False)

        assert response.status_code == 404, (
            f"TC-017 FALHOU: tipo '{INVALID_TYPE}' não existe, "
            f"esperado 404, recebido {response.status_code}"
        )

    def test_TC018_geracao_alem_do_limite(self):
        """TC-018: GET /generation/10 — apenas gerações 1-9 existem."""
        response = requests.get(
            f"{BASE_URL}/generation/{INVALID_GENERATION}", timeout=TIMEOUT, verify=False
        )

        assert response.status_code == 404, (
            f"TC-018 FALHOU: geração {INVALID_GENERATION} não existe, "
            f"esperado 404, recebido {response.status_code}"
        )

    def test_TC019_limit_com_valor_string(self):
        """TC-019: GET /pokemon?limit=abc — parâmetro com tipo errado (string em vez de int)."""
        response = requests.get(
            f"{BASE_URL}/pokemon", params={"limit": "abc"}, timeout=TIMEOUT, verify=False
        )

        # Aceita 400 (rejeição explícita) ou 200 (ignorou e usou padrão) — sem 500
        assert response.status_code in (200, 400), (
            f"TC-019 FALHOU: esperado 200 ou 400, recebido {response.status_code}"
        )
        assert response.status_code != 500, (
            "TC-019: API não deve retornar HTTP 500 para parâmetro malformado"
        )

    def test_TC020_endpoint_completamente_inexistente(self):
        """TC-020: GET /naoexiste/rota — rota inválida deve retornar 400 ou 404, nunca 500.

        A PokéAPI retorna HTTP 400 (Bad Request) para rotas completamente
        desconhecidas — comportamento válido e mais restritivo que um 404.
        Ambos os códigos indicam erro do cliente e ausência de erro interno.
        """
        response = requests.get(f"{BASE_URL}/naoexiste/rota", timeout=TIMEOUT, verify=False)

        assert response.status_code in (400, 404), (
            f"TC-020 FALHOU: esperado 400 ou 404, recebido {response.status_code}"
        )
        assert response.status_code != 500, "TC-020: não deve retornar HTTP 500"