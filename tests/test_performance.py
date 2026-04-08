"""
test_performance.py — Testes de Performance com Locust (Bônus)
Disciplina : Qualidade de Software — INATEL
Professor  : Christopher Lima

Casos:
    PERF-001: Teste de carga — listagem paginada (20 usuários, 30s)
    PERF-002: Teste de estresse — busca por ID aleatório (50 usuários, 30s)

Execução — PERF-001:
    locust -f tests/test_performance.py --headless \
           -u 20 -r 5 -t 30s \
           --host https://pokeapi.co \
           --html reports/locust_report.html \
           --csv  reports/locust

Execução — PERF-002 (ajustar -u para 50):
    locust -f tests/test_performance.py --headless \
           -u 50 -r 10 -t 30s \
           --host https://pokeapi.co \
           --html reports/locust_report_stress.html \
           --csv  reports/locust_stress

Execução interativa (abre dashboard em http://localhost:8089):
    locust -f tests/test_performance.py --host https://pokeapi.co
"""

import random
from locust import HttpUser, task, between, events


# ──────────────────────────────────────────────────────────────────────────────
# Usuário base — configurações compartilhadas
# ──────────────────────────────────────────────────────────────────────────────

class PokeAPIBaseUser(HttpUser):
    """Usuário virtual base para os testes de performance da PokéAPI."""
    abstract = True
    host = "https://pokeapi.co"

    # Espera entre 1 e 2 segundos entre cada requisição
    # Respeita o rate limit da API (~100 req/min por IP)
    wait_time = between(1, 2)

    def on_start(self):
        """Configuração inicial: define Accept header."""
        self.client.headers.update({"Accept": "application/json"})


# ──────────────────────────────────────────────────────────────────────────────
# PERF-001 — Teste de carga: listagem paginada
# Cenário: 20 usuários simultâneos, ramp-up 5s, duração 30s
# Critério: taxa de erro < 5% | P95 < 2000 ms
# ──────────────────────────────────────────────────────────────────────────────

class CargaListagemUser(PokeAPIBaseUser):
    """
    PERF-001: Simula usuários consultando a listagem paginada de Pokémon.
    Usa offsets aleatórios para simular acesso distribuído.
    """

    @task(3)
    def listar_pokemon_pagina_inicial(self):
        """Listagem da primeira página — acesso mais comum."""
        with self.client.get(
            "/api/v2/pokemon",
            params={"limit": 20, "offset": 0},
            name="PERF-001 | GET /pokemon (página inicial)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "results" not in data or len(data["results"]) == 0:
                    response.failure("Resposta sem 'results' ou lista vazia")
                else:
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def listar_pokemon_pagina_aleatoria(self):
        """Listagem com offset aleatório — simula navegação por páginas."""
        offset = random.randint(0, 50) * 20  # Páginas 0 a 50
        with self.client.get(
            "/api/v2/pokemon",
            params={"limit": 20, "offset": offset},
            name="PERF-001 | GET /pokemon (página aleatória)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def listar_tipos(self):
        """Listagem de todos os tipos — endpoint secundário."""
        with self.client.get(
            "/api/v2/type",
            name="PERF-001 | GET /type (listagem)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")


# ──────────────────────────────────────────────────────────────────────────────
# PERF-002 — Teste de estresse: busca por ID aleatório
# Cenário: 50 usuários simultâneos, ramp-up 10s, duração 30s
# Critério: taxa de erro < 10% | P99 < 4000 ms
# ──────────────────────────────────────────────────────────────────────────────

class EstresseBuscaUser(PokeAPIBaseUser):
    """
    PERF-002: Simula carga intensa com buscas por ID e nome aleatórios.
    50 usuários concorrentes para avaliar comportamento sob estresse.
    """

    POKEMON_NAMES = [
        "pikachu", "bulbasaur", "charmander", "squirtle", "mewtwo",
        "eevee", "snorlax", "gengar", "machamp", "alakazam",
        "lapras", "dragonite", "raichu", "vaporeon", "jolteon",
    ]

    @task(4)
    def buscar_pokemon_por_id_aleatorio(self):
        """Busca por ID aleatório entre 1 e 100 — simula acesso intenso."""
        pokemon_id = random.randint(1, 100)
        with self.client.get(
            f"/api/v2/pokemon/{pokemon_id}",
            name="PERF-002 | GET /pokemon/{id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "id" not in data or "name" not in data:
                    response.failure("Campos obrigatórios ausentes: id ou name")
                else:
                    response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def buscar_pokemon_por_nome(self):
        """Busca por nome da lista fixa — simula busca por texto."""
        nome = random.choice(self.POKEMON_NAMES)
        with self.client.get(
            f"/api/v2/pokemon/{nome}",
            name="PERF-002 | GET /pokemon/{name}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def buscar_habilidade(self):
        """Busca de habilidade aleatória — endpoint secundário."""
        ability_id = random.randint(1, 50)
        with self.client.get(
            f"/api/v2/ability/{ability_id}",
            name="PERF-002 | GET /ability/{id}",
            catch_response=True
        ) as response:
            if response.status_code in (200, 404):
                response.success()
            else:
                response.failure(f"HTTP inesperado: {response.status_code}")


# ──────────────────────────────────────────────────────────────────────────────
# Listeners de eventos — log no terminal
# ──────────────────────────────────────────────────────────────────────────────

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "="*60)
    print("  PokéAPI — Teste de Performance iniciado")
    print("  Critérios: PERF-001 (erro < 5%, P95 < 2s)")
    print("             PERF-002 (erro < 10%, P99 < 4s)")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats.total
    print("\n" + "="*60)
    print(f"  Requisições totais : {stats.num_requests}")
    print(f"  Falhas             : {stats.num_failures}")
    if stats.num_requests > 0:
        taxa_erro = (stats.num_failures / stats.num_requests) * 100
        print(f"  Taxa de erro       : {taxa_erro:.2f}%")
    print(f"  Tempo médio (ms)   : {stats.avg_response_time:.0f}")
    print(f"  P95 (ms)           : {stats.get_response_time_percentile(0.95):.0f}")
    print(f"  P99 (ms)           : {stats.get_response_time_percentile(0.99):.0f}")
    print("="*60 + "\n")