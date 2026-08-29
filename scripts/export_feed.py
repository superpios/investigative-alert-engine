#!/usr/bin/env python3
"""Esporta un feed Markdown leggibile dalle piste rankate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    ranked_file = args.input / "ranked_leads.json"
    if not ranked_file.exists():
        print(f"File non trovato: {ranked_file}")
        return

    with ranked_file.open(encoding="utf-8") as f:
        leads = json.load(f)

    lines = [
        "# Feed piste prioritizzate",
        "",
        "> Questo non dimostra alcun illecito. Indica solo una concentrazione di segnali quantitativi che merita verifica umana.",
        "",
        f"Totale piste: **{len(leads)}**",
        "",
        "---",
        "",
    ]

    for lead in leads:
        lines.append(f"## #{lead.get('rank_position')} — score {lead.get('priority_score')}")
        lines.append("")
        lines.append(f"**{lead.get('title', 'Senza titolo')}**")
        lines.append("")
        lines.append(f"- ID: `{lead.get('id')}`")
        lines.append(f"- Regola: `{lead.get('rule_id')}`")
        lines.append(f"- Periodo: {lead.get('period')}")
        if lead.get("priority_reasons"):
            lines.append("- Motivi prioritizzazione:")
            for r in lead["priority_reasons"]:
                lines.append(f"  - {r}")
        lines.append("")
        lines.append(lead.get("disclaimer", ""))
        lines.append("")
        lines.append("---")
        lines.append("")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Feed scritto in {args.output}")


if __name__ == "__main__":
    main()
