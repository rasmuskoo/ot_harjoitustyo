# Ohjelmistotekniikka, harjoitustyö

## TaskBoard Desktop

### Dokumentaatio

- [tyoaikakirjanpito](dokumentaatio/tyoaikakirjanpito.md)
- [vaatimusmaarittely](dokumentaatio/vaatimusmaarittely.md)

### Asennus

Asenna riippuvuudet komennolla:

`poetry install`

### Sovelluksen käynnistys

Käynnistä sovellus komennolla:

`poetry run invoke start`

### Komentorivitoiminnot

Ohjelman suorittaminen:

`poetry run invoke start`

Testaus:

`poetry run invoke test`

Testikattavuusraportti:

`poetry run invoke coverage-report`

Raportti generoituu `htmlcov`-hakemistoon.

### Tietokanta

- SQLite-tietokanta luodaan automaattisesti hakemistoon `data/taskboard.db`.
- `users`, `tasks` ja `task_participants` -taulut luodaan sovelluksen käynnistyksen yhteydessä.

## Tehtävät

### Viikko 2

- [poetry.lock](laskarit/viikko2/maksukortti/poetry.lock)
- [pyproject.toml](laskarit/viikko2/maksukortti/pyproject.toml)
- [maksukortti.py](laskarit/viikko2/maksukortti/src/maksukortti.py)
- [__init__.py](laskarit/viikko2/maksukortti/tests/__init__.py)
- [maksukortti_test.py](laskarit/viikko2/maksukortti/tests/maksukortti_test.py)
