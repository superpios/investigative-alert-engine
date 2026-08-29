# Come funziona il ranking

Il punteggio di priorità (0–100) è calcolato **solo** da criteri quantitativi e ripetuti.  
Nessun giudizio qualitativo.

## Componenti del punteggio (v0.1)

| Criterio | Peso max | Descrizione |
|----------|----------|-------------|
| Concentrazione nominativo | 30 | Numero di incarichi distinti sullo stesso nominativo nello stesso periodo |
| Affidamenti diretti ripetuti | 25 | Stesso soggetto riceve più affidamenti diretti dallo stesso ente o da enti diversi |
| Rinnovi / proroghe | 20 | Presenza di rinnovi o proroghe ripetute |
| Importo elevato (soglia relativa) | 15 | Importo superiore a una soglia relativa al dataset (non assoluta) |
| Persistenza nel tempo | 10 | La stessa pista (o variante molto simile) appare in più esecuzioni consecutive |

## Formula semplificata

```
priority_score = min(100, somma_pesata_dei_criteri_attivi)
```

Ogni criterio attivo aggiunge il proprio contributo solo se supera una soglia minima definita in `rules/ranking_v0.1.yaml`.

Il contributo di un criterio scala linearmente dal valore soglia fino al peso massimo (raggiunto a ~12 ripetizioni), poi è cap al peso massimo. Nessun contributo è basato su inferenze: solo conteggi grezzi estratti dai fatti osservati. La data del ranking (`ranking_date`) è derivata dai dati (`data_through`), mai dall'orario di esecuzione, per garantire determinismo.

## Cosa non influenza il punteggio

- Opinioni o etichette
- Inferenze su omonimie
- Confronto tra perimetri contabili diversi
- Dati esterni non presenti nelle piste originali

## Validazione obbligatoria

Ogni nuova regola di ranking deve essere:
1. Documentata in questo file
2. Testata contro falsi positivi
3. Validata manualmente su almeno 20 piste reali prima di essere attivata
