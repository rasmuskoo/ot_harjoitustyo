# Ohjelmistotekniikka, harjoitustyö

## TaskBoard Desktop

TaskBoard on Pythonilla toteutettu sovellus tehtävien ja projektien hallintaan. Sovelluksessa voi rekisteröityä, kirjautua sisään, luoda ja hallita tehtäviä sekä luoda projekteja ja liittää käyttäjiä ja tehtäviä niihin.

## Dokumentaatio

- [vaatimusmaarittely](dokumentaatio/vaatimusmaarittely.md)
- [arkkitehtuuri](dokumentaatio/arkkitehtuuri.md)
- [kayttoohje](dokumentaatio/kayttoohje.md)
- [testaus](dokumentaatio/testaus.md)
- [tyoaikakirjanpito](dokumentaatio/tyoaikakirjanpito.md)
- [changelog](dokumentaatio/changelog.md)

## GitHub Release
- [Viikko 5 release](https://github.com/rasmuskoo/ot_harjoitustyo/releases/tag/viikko5)
- [Viikko 6 release](https://github.com/rasmuskoo/ot_harjoitustyo/releases/tag/viikko6)
- [Loppupalautus release](https://github.com/rasmuskoo/ot_harjoitustyo/releases/tag/loppupalautus)

## Asennus

Asenna riippuvuudet komennolla:

`poetry install`

## Komentoriviltä suoritettavat komennot

Ohjelman suorittaminen (ensisijainen):

`poetry run invoke gui`

Voit suorittaa ohjelman myös ilman graafista käyttöliittymää (toissijainen):

`poetry run invoke start`

Testaus:

`poetry run invoke test`

Testikattavuusraportti:

`poetry run invoke coverage-report`

Raportti generoituu `htmlcov`-hakemistoon.

Pylint-tarkistukset:

`poetry run invoke lint`
