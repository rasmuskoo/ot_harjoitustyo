# Changelog

## Viikko 3

- Käyttäjä voi rekisteröityä sovellukseen (etunimi, sukunimi, sähköposti, salasana, salasanan vahvistus)
- Käyttäjä voi kirjautua sisään sähköpostilla ja salasanalla sekä kirjautua ulos
- Kirjautumattomassa tilassa käyttäjä näkee kirjautumisnäkymän, josta voi siirtyä rekisteröitymiseen
- Rekisteröitymisen jälkeen käyttäjä palautetaan takaisin kirjautumisnäkymään
- Lisätty `AuthService`-luokka, joka vastaa rekisteröinti- ja kirjautumislogiikasta
- Lisätty `SessionService`-luokka, joka hallitsee sovelluksen kirjautumistilaa
- Lisätty `TaskRepository`- ja `TaskService`-luokat tehtävien hakuun ja luontiin
- Kotinäkymä näyttää käyttäjän tehtävät, joihin käyttäjä on liitetty osallistujaksi
- Käyttäjä voi luoda tehtävän (otsikko + kuvaus), ja tehtävä linkitetään automaattisesti luoneeseen käyttäjään
- Lisätty yksikkötesti, joka testaa rekisteröinnin ja kirjautumisen toimivuuden
- Lisätty `invoke`-tehtävät: `start`, `test` ja `coverage-report`
- Lisätty `.coveragerc` testikattavuuden keräämiseen hakemistosta `src` (testikoodi rajattu pois)
