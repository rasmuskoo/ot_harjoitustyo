# Ohjelmistotekniikka, harjoitustyö

## TaskBoard Desktop

TaskBoard on Pythonilla toteutettu työpöytäsovellus tehtävien hallintaan.

## Dokumentaatio

- [vaatimusmaarittely](dokumentaatio/vaatimusmaarittely.md)
- [arkkitehtuuri](dokumentaatio/arkkitehtuuri.md)
- [tyoaikakirjanpito](dokumentaatio/tyoaikakirjanpito.md)
- [changelog](dokumentaatio/changelog.md)

## Asennus

Asenna riippuvuudet komennolla:

`poetry install`

## Sovelluksen käynnistys

Käynnistä sovellus komennolla:

`poetry run invoke start`

## Komentorivitoiminnot

Ohjelman suorittaminen:

`poetry run invoke start`

Testaus:

`poetry run invoke test`

Testikattavuusraportti:

`poetry run invoke coverage-report`

Raportti generoituu `htmlcov`-hakemistoon.

Pylint-tarkistukset:

`poetry run invoke lint`
