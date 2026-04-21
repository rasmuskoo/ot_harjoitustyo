# Ohjelmistotekniikka, harjoitustyö

## TaskBoard Desktop

TaskBoard on Pythonilla toteutettu komentorivisovellus tehtävien ja projektien hallintaan. Sovelluksessa voi rekisteröityä, kirjautua sisään, luoda ja hallita tehtäviä sekä luoda projekteja ja liittää käyttäjiä ja tehtäviä niihin.

## Dokumentaatio

- [vaatimusmaarittely](dokumentaatio/vaatimusmaarittely.md)
- [arkkitehtuuri](dokumentaatio/arkkitehtuuri.md)
- [tyoaikakirjanpito](dokumentaatio/tyoaikakirjanpito.md)
- [changelog](dokumentaatio/changelog.md)

## GitHub Release
- [Viiko 5 release](https://github.com/rasmuskoo/ot_harjoitustyo/releases/tag/viikko5)

## Asennus

Asenna riippuvuudet komennolla:

`poetry install`

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
