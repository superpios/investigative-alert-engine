#!/usr/bin/env python3
"""
Investigative Alert Engine - rank_leads.py

Prende le piste generate dal Leads Generator e produce un feed prioritizzato.
Completamente deterministico e fail-closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


DISCLAIMER = (
    "Questo non dimostra alcun illecito. Indica solo una concentrazione di "
    "segnali quantitativi che merita verifica umana."
)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_leads(input_dir: Path) -> list[dict]:
    """Carica tutte le piste da file JSON presenti in input_dir.

    Sono considerati piste solo gli oggetti che contengono un ``id``.
    File di servizio (es. manifest.json) vengono ignorati.
    """
    leads = []
    for p in sorted(input_dir.glob("*.json")):
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "leads" in data:
            items = data["leads"]
        elif isinstance(data, dict) and "id" in data:
            items = [data]
        else:
            continue  # file di servizio, non è una pista
        for it in items:
            if isinstance(it, dict) and it.get("id"):
                leads.append(it)
    return leads


def extract_count_from_facts(facts: list[str], keywords: list[str]) -> int:
    """Estrae un conteggio grezzo dai fatti osservati (euristica conservativa).

    Cerca il numero piu' vicino alla keyword, mai un numero lontano nel testo
    (es. un anno nella ragione sociale di un ente).
    """
    text = " ".join(facts).lower()
    for kw in keywords:
        if kw not in text:
            continue
        # numero subito dopo la keyword (es. "affidamenti diretti: 12")
        m = re.search(rf"{re.escape(kw)}\D*?(\d+)", text)
        if m:
            return int(m.group(1))
        # numero subito prima della keyword (es. "5 incarichi")
        m = re.search(rf"(\d+)\s+(?:di\s+)?{re.escape(kw)}", text)
        if m:
            return int(m.group(1))
    return 0


def _contrib(count: int, weight: float, threshold: int, full_at: int = 12) -> float:
    """Contributo lineare di un criterio, cap a ``weight``.

    Raggiunge il peso massimo a ``full_at`` ripetizioni, scalando linearmente
    sotto soglia. Nessuna inferenza: solo conteggi grezzi dai fatti.
    """
    if count < threshold:
        return 0.0
    span = max(1, full_at - threshold + 1)
    return min(weight, (count - threshold + 1) * (weight / span))


def compute_score(lead: dict, rules: dict, history: list[dict]) -> tuple[float, list[str]]:
    """Calcola priority_score e reasons in modo deterministico."""
    score = 0.0
    reasons: list[str] = []
    w = rules["weights"]
    t = rules["thresholds"]

    facts = lead.get("observed_facts", [])

    # 1. Concentrazione nominativo
    conc = extract_count_from_facts(facts, ["incarichi", "incarico"])
    if conc >= t["concentration_min_count"]:
        contrib = _contrib(conc, w["concentration"], t["concentration_min_count"])
        score += contrib
        reasons.append(f"concentrazione: {conc} incarichi (soglia {t['concentration_min_count']})")

    # 2. Affidamenti diretti ripetuti
    awards = extract_count_from_facts(facts, ["affidamenti diretti", "affidamento diretto"])
    if awards >= t["repeated_direct_awards_min_count"]:
        contrib = _contrib(awards, w["repeated_direct_awards"], t["repeated_direct_awards_min_count"])
        score += contrib
        reasons.append(f"affidamenti diretti ripetuti: {awards}")

    # 3. Rinnovi / proroghe
    renewals = extract_count_from_facts(facts, ["rinnovi", "proroghe", "rinnovo", "proroga"])
    if renewals >= t["renewals_min_count"]:
        contrib = _contrib(renewals, w["renewals"], t["renewals_min_count"])
        score += contrib
        reasons.append(f"rinnovi/proroghe: {renewals}")

    # 4. Persistenza nel tempo (storico)
    lead_id = lead.get("id", "")
    persistence = sum(1 for h in history if any(x.get("id") == lead_id for x in h.get("leads", [])))
    if persistence >= t["persistence_min_runs"]:
        contrib = min(w["persistence"], persistence * 2)
        score += contrib
        reasons.append(f"persistenza: apparsa in {persistence} esecuzioni")

    # Nota: high_amount richiede statistiche sul dataset intero -> lasciato a 0 in v0.1
    # (attivare solo dopo calibrazione, come da LIMITI.md)

    score = min(100.0, round(score, 1))
    return score, reasons


def derive_ranking_date(leads: list[dict]) -> str:
    """Data deterministica del ranking: derivata dai dati (data_through), mai dall'orario di esecuzione."""
    dates = [l["data_through"] for l in leads if l.get("data_through")]
    if not dates:
        return ""
    return max(dates)


def rank_leads(leads: list[dict], rules: dict, history: list[dict], ranking_date: str) -> list[dict]:
    ranked = []
    for lead in leads:
        score, reasons = compute_score(lead, rules, history)
        ranked_lead = dict(lead)  # copia
        ranked_lead["priority_score"] = score
        ranked_lead["priority_reasons"] = reasons
        ranked_lead["ranking_date"] = ranking_date
        ranked_lead["ranking_version"] = rules.get("version", "0.1")
        ranked_lead["disclaimer"] = rules["behavior"].get("disclaimer", DISCLAIMER)
        ranked.append(ranked_lead)

    # Ordina per score decrescente, poi data_through e id (tie-break deterministico)
    ranked.sort(
        key=lambda x: (-x["priority_score"], x.get("data_through", ""), x.get("id", "")),
    )

    for i, lead in enumerate(ranked, start=1):
        lead["rank_position"] = i

    return ranked


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank investigative leads")
    parser.add_argument("--input", required=True, type=Path, help="Directory con le piste JSON")
    parser.add_argument("--output", required=True, type=Path, help="Directory di output")
    parser.add_argument("--history", type=Path, help="Directory storico (opzionale)")
    parser.add_argument("--rules", required=True, type=Path, help="File YAML regole ranking")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"[fail-closed] Input directory non trovata: {args.input}", file=sys.stderr)
        sys.exit(1)

    rules = load_yaml(args.rules)
    leads = load_leads(args.input)

    if not leads:
        print("[fail-closed] Nessuna pista valida trovata. Nessun output generato.", file=sys.stderr)
        sys.exit(0)

    ranking_date = derive_ranking_date(leads)
    if not ranking_date:
        print(
            "[fail-closed] Nessuna data di riferimento (data_through) nelle piste: "
            "impossibile produrre un ranking deterministico.",
            file=sys.stderr,
        )
        sys.exit(1)

    history: list[dict] = []
    if args.history and args.history.exists():
        for p in sorted(args.history.glob("*.json")):
            with p.open(encoding="utf-8") as f:
                history.append(json.load(f))

    ranked = rank_leads(leads, rules, history, ranking_date)

    args.output.mkdir(parents=True, exist_ok=True)
    out_file = args.output / "ranked_leads.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)

    # Salva anche uno snapshot nello storico (nome deterministico = data dei dati)
    if args.history:
        args.history.mkdir(parents=True, exist_ok=True)
        hist_file = args.history / f"run_{ranking_date}.json"
        with hist_file.open("w", encoding="utf-8") as f:
            json.dump({"date": ranking_date, "leads": ranked}, f, ensure_ascii=False, indent=2)

    print(f"Ranking completato: {len(ranked)} piste -> {out_file}")


if __name__ == "__main__":
    main()
