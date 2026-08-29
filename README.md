# Investigative Alert Engine · DVNS

Motore di **monitoraggio continuo e prioritizzazione** delle piste investigative generato da [investigative-leads-generator](https://github.com/superpios/investigative-leads-generator).

Ogni output rimane un **segnale quantitativo che merita verifica**.  
Nessuna conclusione, nessuna etichetta di frode, spreco o responsabilità.

Progetto collegato a:
- [investigative-explorer-dvns](https://github.com/superpios/investigative-explorer-dvns)
- [investigative-leads-generator](https://github.com/superpios/investigative-leads-generator)
- [DoveVannoINostriSoldi](https://github.com/Italian-Builders-Org/DoveVannoINostriSoldi)

## Cosa fa

- Rileva e confronta le piste generate nel tempo
- Assegna un **punteggio di priorità** basato solo su criteri quantitativi e ripetuti
- Produce un feed ordinato di piste prioritizzate (JSON + Markdown)
- Mantiene storico e provenienza completa
- È deterministico e fail-closed

## Cosa non fa

- Non stabilisce responsabilità, illeciti o sprechi
- Non risolve omonimie
- Non somma perimetri contabili diversi
- Non usa etichette valutative
- Non inventa collegamenti assenti nei dati

## Filosofia (vincolante)

> Una pista prioritizzata è solo un segnale quantitativo che merita verifica umana.  
> Nessun output di questo sistema dimostra, suggerisce o implica illecito, spreco, frode o responsabilità individuale.

## Architettura

```
Explorer → Leads Generator → Alert Engine
                ↓
         piste grezze
                ↓
         ranking + storico
                ↓
         feed prioritizzato
```

## Avvio rapido

```bash
# 1. Installa
pip install -r requirements.txt

# 2. Copia le piste generate dal Leads Generator in data/input/
#    (es. leads_v0.1.json)

# 3. Esegui ranking
python scripts/rank_leads.py \
  --input data/input \
  --output data/ranked \
  --history data/history \
  --rules rules/ranking_v0.1.yaml

# 4. (Opzionale) genera feed Markdown
python scripts/export_feed.py --input data/ranked --output data/ranked/feed.md
```

## Output

In `data/ranked/`:

- `ranked_leads.json` — lista ordinata per priorità
- `feed.md` — report leggibile (generato da `export_feed.py`)

In `data/history/`:

- `run_<data_through>.json` — snapshot di ogni esecuzione (per confronto nel tempo e calcolo della persistenza)

Ogni pista ranking contiene sempre:
- `priority_score` (0–100)
- `priority_reasons` (lista di motivi quantitativi)
- `rank_position`
- tutti i campi originali della pista
- disclaimer obbligatorio

## Documentazione

| File | Contenuto |
|------|-----------|
| [docs/PRINCIPI.md](docs/PRINCIPI.md) | Principi vincolanti |
| [docs/RANKING.md](docs/RANKING.md) | Come funziona il punteggio |
| [docs/LIMITI.md](docs/LIMITI.md) | Limiti metodologici |
| [docs/FORMATO_OUTPUT.md](docs/FORMATO_OUTPUT.md) | Schema dell'output |

## Requisiti

- Python 3.11+
- Dipendenze: `pip install -r requirements.txt`

## Licenza

GNU Affero General Public License v3.0
