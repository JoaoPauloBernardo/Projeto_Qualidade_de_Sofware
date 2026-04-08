"""
conftest.py — Fixtures compartilhadas para a suíte PokéAPI
"""
import pytest
import requests
import urllib3

# Suprime o aviso de SSL quando verify=False é usado
# Necessário em redes com proxy institucional (ex: INATEL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://pokeapi.co/api/v2"
TIMEOUT  = 10  # segundos


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def timeout():
    return TIMEOUT


@pytest.fixture(scope="session")
def session():
    """Sessão HTTP reutilizada por todos os testes (melhora performance)."""
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    s.verify = False  # contorna proxy SSL institucional
    yield s
    s.close()