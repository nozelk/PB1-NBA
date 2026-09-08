# NBA Analytics

Projekt podatkovnih baz: Python, Bottle in SQLite.


## Zagon

V terminalu odpri mapo, ki vsebuje `main.py`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Odpri http://localhost:8080. Ustavi s Ctrl+C.
Ob nadgradnji ohrani isto virtualno okolje; namestitev ponovi ob spremembi `requirements.txt`.
Na macOS/Linux uporabi `.venv/bin/python` namesto `.\.venv\Scripts\python.exe`.

Prvi ZIP vsebuje `nba.db` iz izvornega projekta. Naslednji paketi baze ne prepisujejo.
Če baze ni, zagon ustvari prazne tabele; za prikaz podatkov uporabi priloženo bazo.
Baza in lokalno okolje sta izključena iz novih Git commitov z `.gitignore`.
Pisave, knjižnice za grafe in nekatere slike se nalagajo z interneta.

## Trenutne funkcionalnosti

- Osnova in podatkovna baza: SQLite shema z 11 tabelami, povezava z bazo, začetna stran, skupni izgled in priloženi podatki.
