"""
gerar_relatorio.py — Processa o report.json bruto do pytest e gera
um relatorio_legivel.json limpo e organizado.

Uso:
    python gerar_relatorio.py

Entrada : reports/report.json          (gerado pelo pytest automaticamente)
Saida   : reports/relatorio_legivel.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

INPUT  = Path("reports/report.json")
OUTPUT = Path("reports/relatorio_legivel.json")


def formatar_duracao(segundos: float) -> str:
    if segundos < 1:
        return f"{segundos * 1000:.0f} ms"
    return f"{segundos:.2f} s"


def extrair_mensagem_falha(longrepr) -> str:
    """Extrai só a linha de AssertionError do traceback completo."""
    if not longrepr:
        return None
    if isinstance(longrepr, str):
        for linha in longrepr.splitlines():
            if "AssertionError" in linha or "assert" in linha.lower():
                return linha.strip()
        return longrepr.splitlines()[-1].strip()
    return str(longrepr)


def processar(raw: dict) -> dict:
    criado_ts  = raw.get("created", 0)
    criado_str = datetime.fromtimestamp(criado_ts, tz=timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")

    summary = raw.get("summary", {})
    total   = summary.get("total", 0)
    passou  = summary.get("passed", 0)
    falhou  = summary.get("failed", 0)
    taxa    = f"{(passou / total * 100):.1f}%" if total else "0%"

    testes_raw = raw.get("tests", [])

    testes = []
    for t in testes_raw:
        nodeid   = t.get("nodeid", "")
        # extrai só o nome da função: TestCaminhoFeliz::test_TC001_...
        nome_fn  = nodeid.split("::")[-1]          # test_TC001_busca_pokemon_por_id_valido
        # extrai TC-XXX do nome
        partes   = nome_fn.split("_")
        tc_id    = partes[1].upper().replace("TC", "TC-") if len(partes) > 1 else "?"
        # classe (caminho feliz vs inválido)
        classe   = nodeid.split("::")[-2] if "::" in nodeid else ""
        categoria = "Caminho Feliz" if "CaminhoFeliz" in classe else "Dados Inválidos"

        outcome  = t.get("outcome", "unknown")
        duracao  = formatar_duracao(t.get("duration", 0))

        falha_msg = None
        if outcome == "failed":
            call = t.get("call", {})
            falha_msg = extrair_mensagem_falha(call.get("longrepr"))

        entrada = {
            "id":        tc_id,
            "nome":      nome_fn.replace("test_", "").replace("_", " "),
            "categoria": categoria,
            "resultado": "✓ PASSOU" if outcome == "passed" else "✗ FALHOU",
            "duracao":   duracao,
        }
        if falha_msg:
            entrada["erro"] = falha_msg

        testes.append(entrada)

    # agrupa por categoria
    validos   = [t for t in testes if t["categoria"] == "Caminho Feliz"]
    invalidos = [t for t in testes if t["categoria"] == "Dados Inválidos"]

    return {
        "relatorio": {
            "titulo":    "PokéAPI — Suíte de Testes Automatizados",
            "disciplina": "Qualidade de Software — INATEL",
            "ferramenta": "pytest + requests",
            "gerado_em": criado_str,
            "duracao_total": formatar_duracao(raw.get("duration", 0)),
        },
        "resumo": {
            "total":     total,
            "passou":    passou,
            "falhou":    falhou,
            "taxa_aprovacao": taxa,
            "status_geral": "APROVADO" if falhou == 0 else "REPROVADO",
        },
        "testes": {
            "caminho_feliz": validos,
            "dados_invalidos": invalidos,
        },
    }


def main():
    if not INPUT.exists():
        print(f"[ERRO] Arquivo {INPUT} não encontrado.")
        print("Execute primeiro: pytest tests/test_pokeapi.py")
        sys.exit(1)

    raw = json.loads(INPUT.read_text(encoding="utf-8"))
    resultado = processar(raw)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    r = resultado["resumo"]
    print(f"\n  Relatório gerado: {OUTPUT}")
    print(f"  {r['passou']}/{r['total']} testes passaram — {r['taxa_aprovacao']} — {r['status_geral']}\n")


if __name__ == "__main__":
    main()