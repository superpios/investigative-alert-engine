"""Test per rank_leads (determinismo, fail-closed, ranking derivato dai dati)."""

import json
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.rank_leads import (
    compute_score,
    derive_ranking_date,
    load_leads,
    rank_leads,
)


SAMPLE_RULES = {
    "version": "0.1",
    "weights": {
        "concentration": 30,
        "repeated_direct_awards": 25,
        "renewals": 20,
        "high_amount": 15,
        "persistence": 10,
    },
    "thresholds": {
        "concentration_min_count": 3,
        "repeated_direct_awards_min_count": 2,
        "renewals_min_count": 2,
        "high_amount_percentile": 0.90,
        "persistence_min_runs": 2,
    },
    "behavior": {
        "include_zero_score": True,
        "disclaimer": "Questo non dimostra alcun illecito. Indica solo una concentrazione di segnali quantitativi che merita verifica umana.",
    },
}


def _lead(lid, facts, data_through="2026-08-12"):
    return {
        "id": lid,
        "title": f"Test {lid}",
        "observed_facts": facts,
        "rule_id": "R1",
        "period": "2025",
        "why_worth_checking": "test",
        "what_cannot_be_claimed": [],
        "sources": [],
        "data_through": data_through,
        "disclaimer": "test",
    }


def test_compute_score_concentration():
    lead = _lead("TEST-001", ["5 incarichi distinti su enti diversi"])
    score, reasons = compute_score(lead, SAMPLE_RULES, history=[])
    assert score > 0
    assert any("concentrazione" in r for r in reasons)


def test_compute_score_differentiates_counts():
    low = _lead("A", ["9 affidamenti diretti"])
    high = _lead("B", ["12 affidamenti diretti"])
    s_low, _ = compute_score(low, SAMPLE_RULES, history=[])
    s_high, _ = compute_score(high, SAMPLE_RULES, history=[])
    assert s_high > s_low


def test_rank_is_deterministic():
    leads = [_lead("A", ["4 incarichi"]), _lead("B", ["2 incarichi"])]
    r1 = rank_leads(leads, SAMPLE_RULES, [], ranking_date="2026-08-12")
    r2 = rank_leads(leads, SAMPLE_RULES, [], ranking_date="2026-08-12")
    assert [x["id"] for x in r1] == [x["id"] for x in r2]
    assert [x["priority_score"] for x in r1] == [x["priority_score"] for x in r2]


def test_ranking_date_is_data_derived_not_today():
    leads = [_lead("A", ["4 incarichi"], data_through="2026-08-12")]
    r = rank_leads(leads, SAMPLE_RULES, [], ranking_date=derive_ranking_date(leads))
    assert r[0]["ranking_date"] == "2026-08-12"


def test_load_leads_skips_manifest():
    import tempfile

    d = Path(tempfile.mkdtemp())
    leads_file = d / "leads_v0.1.json"
    leads_file.write_text(json.dumps([_lead("X", ["3 incarichi"])]), encoding="utf-8")
    manifest = d / "manifest.json"
    manifest.write_text(
        json.dumps({"status": "ok", "inputs": [], "leads_count": 1}), encoding="utf-8"
    )
    found = load_leads(d)
    assert len(found) == 1
    assert found[0]["id"] == "X"


def test_persistence_bonus():
    lead = _lead("P", ["3 affidamenti diretti"])
    # servono >= 2 esecuzioni precedenti (persistence_min_runs: 2)
    history = [
        {"date": "2026-01-01", "leads": [lead]},
        {"date": "2026-02-01", "leads": [lead]},
    ]
    s0, _ = compute_score(lead, SAMPLE_RULES, history=[])
    s1, reasons = compute_score(lead, SAMPLE_RULES, history=history)
    assert any("persistenza" in r for r in reasons)
    assert s1 > s0


def test_extract_ignores_year_in_company_name():
    # "2020-2026" nella ragione sociale non deve essere scambiato per il conteggio
    lead = _lead("C", ["ente infrastrutture milano cortina 2020-2026 s.p.a.", "Numero di affidamenti diretti: 12"])
    score, reasons = compute_score(lead, SAMPLE_RULES, history=[])
    assert any("12" in r for r in reasons)
