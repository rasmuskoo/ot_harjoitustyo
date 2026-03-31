# Ohjelmistotekniikka, harjoitustyö

## TaskBoard Desktop

### Dokumentaatio

- [tyoaikakirjanpito](dokumentaatio/tyoaikakirjanpito.md)
- [vaatimusmaarittely](dokumentaatio/vaatimusmaarittely.md)

### Asennus

1. Siirry projektin juureen:
   - `cd /Users/rasmus/HY/Ohjelmistotuotanto/ot_harjoitustyo`
2. Asenna riippuvuudet Poetrylla:
   - `poetry install`

### Sovelluksen käynnistys

- Käynnistä sovellus komennolla:
  - `poetry run python -m src.main`

### Tietokanta

- SQLite-tietokanta luodaan automaattisesti hakemistoon `data/taskboard.db`.
- `users`-taulu luodaan sovelluksen käynnistyksen yhteydessä.

## Tehtävät

### Viikko 2

- [poetry.lock](laskarit/viikko2/maksukortti/poetry.lock)
- [pyproject.toml](laskarit/viikko2/maksukortti/pyproject.toml)
- [maksukortti.py](laskarit/viikko2/maksukortti/src/maksukortti.py)
- [__init__.py](laskarit/viikko2/maksukortti/tests/__init__.py)
- [maksukortti_test.py](laskarit/viikko2/maksukortti/tests/maksukortti_test.py)
