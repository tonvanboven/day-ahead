# Day Ahead Optimizer – JSON API (v2)

Alle endpoints hangen onder `/v2/api/` van de dao-webserver
(standaard poort `5000`). De api kent geen eigen authenticatie: draai hem
alleen op een vertrouwd (lokaal) netwerk of achter een reverse proxy die de
authenticatie afhandelt.

Tijdstempels worden - behalve in `/data/`, dat om compatibiliteitsredenen
ongewijzigd is gebleven - teruggegeven als ISO-8601 met tijdzone-offset.
Met de queryparameter `timezone` (bijv. `timezone=Europe/Brussels`) kan een
andere tijdzone dan `Europe/Amsterdam` worden gekozen.

## Data

### `GET /v2/api/data/`

De gemeten (`v`) en voorspelde (`f`) waarden per variabele.

| parameter   | verplicht | omschrijving                                             |
|-------------|-----------|----------------------------------------------------------|
| `start`     | ja        | ISO-datum(tijd), bijv. `2026-09-07T00:00:00`              |
| `end`       | ja        | ISO-datum(tijd), exclusief                                |
| `aggregate` | ja        | `15min`, `hour`, `day`, `week` of `month`                 |
| `fields`    | nee       | komma-gescheiden codes, bijv. `da,cons,prod`; leeg = alle |

```json
[
  {"ts": "2026-09-07 14:00", "da": {"v": 0.1234, "f": null},
                             "cons": {"v": 0.51, "f": 0.48}}
]
```

### `GET /v2/api/vars/`

De variabelen waarvoor daadwerkelijk data aanwezig is: `[{"code", "name"}]`.

### `GET /v2/api/prices/`

De day ahead tarieven per uur, inclusief morgen zodra die gepubliceerd zijn.
Parameters `start` en `end` zijn optionele datums (standaard vandaag t/m
overmorgen).

```json
{
  "dim": "euro/kWh",
  "series": [{"time": "2026-09-07T14:00:00+02:00", "price": 0.1234}],
  "today": {"date": "2026-09-07", "hours": 24, "min": 0.02, "max": 0.31,
            "average": 0.1234,
            "cheapest": {"time": "...", "price": 0.02},
            "most_expensive": {"time": "...", "price": 0.31},
            "cheapest_hours": ["...", "...", "..."]},
  "tomorrow": null
}
```

## Machine learning

### `GET /v2/api/solar-devices/`

De pv-installaties waarvoor `ml_prediction` aanstaat, inclusief of er al een
getraind model aanwezig is.

### `GET /v2/api/solar-ml/`

Per uur de gemeten productie naast de dao-voorspelling en de ml-voorspelling
van één installatie, plus de r²-scores en dagtotalen.

| parameter | verplicht | omschrijving                                       |
|-----------|-----------|-----------------------------------------------------|
| `device`  | nee       | naam van de installatie; leeg = de eerste met ml     |
| `date`    | nee       | dag `YYYY-MM-DD`; leeg = vandaag                     |

### `GET /v2/api/ml-models/`

Per model wanneer het getraind is en - als de training met deze versie is
gedraaid - de trainingsstatistieken (`test_r2`, `test_mae`, `test_rmse`,
`feature_importance`, `best_params`, ...). Deze worden bij het trainen
weggeschreven als `<model>_stats.json` naast het `.pkl`-bestand.

### `GET /v2/api/baseloads/`

De berekende basislast per weekdag (`0` = maandag) met 24 uurwaarden, plus de
reeks van vandaag met tijdstempels. Levert `404` zolang de taak
`calc_baseloads` nog niet gedraaid heeft.

## Taken

### `GET /v2/api/status/`

Versie, huidige tijd en tijdzone, de status van de lopende taak en een
samenvatting van de configuratie.

### `POST /v2/api/task-exec/`

Start een taak asynchroon. Body als json (`{"task": "optimize"}`) of
form-encoded. Antwoordt met `202` bij starten, `409` als er al een taak loopt
en `400` bij een onbekende taak.

Geldige taken: `optimize` (alias `optimize_regular`), `optimize_debug`,
`prices` (`update_prices`), `meteo` (`update_meteo`), `tibber`
(`update_tibber`), `calc_baseloads`, `train_ml`, `consolidate`, `clean`.

### `GET /v2/api/task-state/`

Status van de taak (`idle`, `running`, `done`, `error`, `cancelled`), hoelang
hij loopt en de laatste 8000 tekens van het logbestand.

### `POST /v2/api/task-cancel/`

Breekt de lopende taak af.

### `GET /v2/api/run/<task>`

Draait een taak *synchroon* en geeft de log als platte tekst terug. Bedoeld
voor handmatig gebruik; gebruik voor clients `/task-exec/`, omdat een
optimalisering langer kan duren dan de meeste http-timeouts.
