# Formato obbligatorio dell’output ranking

Ogni elemento in `ranked_leads.json` deve contenere **tutti** i campi seguenti.

## Campi obbligatori

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `id` | string | ID originale della pista |
| `title` | string | Titolo neutro originale |
| `observed_facts` | list | Fatti osservati originali |
| `sources` | list | Fonti originali |
| `period` | string | Periodo di osservazione |
| `rule_id` | string | Regola che ha generato la pista |
| `why_worth_checking` | string | Motivazione originale |
| `what_cannot_be_claimed` | list | Cosa non si può affermare |
| `data_through` | string | Data di riferimento dei dati originali (derivata, non l'orario di esecuzione) |
| `snapshot_created_at` | string | Data di creazione dello snapshot originale (preservata) |
| `explorer_sha` | string | Hash dello snapshot originale (preservato) |
| `disclaimer` | string | Disclaimer fisso |
| `priority_score` | number | Punteggio 0–100 |
| `priority_reasons` | list | Motivi quantitativi del ranking |
| `rank_position` | integer | Posizione nel feed ordinato |
| `ranking_date` | string | Data ISO del ranking |
| `ranking_version` | string | Versione delle regole di ranking usate |

## Disclaimer obbligatorio (testo fisso)

```
Questo non dimostra alcun illecito. Indica solo una concentrazione di segnali quantitativi che merita verifica umana.
```

## Esempio minimo valido

Vedi `templates/ranked_lead_template.json`.
