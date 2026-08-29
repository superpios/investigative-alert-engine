# Limiti

Documento obbligatorio. Estende i limiti di investigative-explorer-dvns e investigative-leads-generator.

## Limiti metodologici

1. Un punteggio di priorità alto **non** significa che esista un problema. Significa solo che ci sono più segnali quantitativi concentrati.
2. L’assenza di una pista prioritizzata non è un risultato.
3. La copertura dei dati di partenza è parziale (vedi LIMITI.md dell’Explorer).
4. Il ranking non risolve omonimie e non arricchisce con dati esterni.
5. Il sistema non confronta perimetri contabili diversi.

## Trattamento delle persone

Identico all’Explorer e al Generator:
- solo ruolo pubblico documentato
- nessun arricchimento da fonti non ufficiali
- diritto di segnalazione via issue

## Regola di esposizione

Ogni output deve contenere:
- `priority_score`
- `priority_reasons` (solo quantitativi)
- tutti i campi originali della pista
- disclaimer obbligatorio

In assenza anche di uno solo di questi elementi, la pista non viene inclusa nel feed ranking.
