# Changelog

## Viikko 3

- Käyttäjän voi luoda
- Käyttäjälle voi kirjautua
- Lisätty AuthService-luokka, joka vastaa rekisteröinti- ja kirjautumislogiikasta
- Lisätty SessionService-luokka, joka hallitsee sovelluksen kirjautumistilaa
- Käyttäjä voi luoda tehtävän (otsikko + kuvaus), ja tehtävä linkitetään automaattisesti luoneeseen käyttäjään
- Lisätty TaskRepository- ja TaskService-luokat tehtävien hakuun ja luontiin
- Kotinäkymä näyttää käyttäjän tehtävät
- Lisätty yksikkötesti, joka testaa rekisteröinnin ja kirjautumisen toimivuuden
- Lisätty invoke-tehtävät: start, test ja coverage-report
- Lisätty .coveragerc testikattavuuden keräämiseen hakemistosta

## Viikko 4

- Lisätty .pylintrc tiedosto
- Tehtäviä voi nyt muokata
- Tehtävän voi merkata valmistuneeksi
- Valmiita tehtäviä voi tarkastella valmiden tehtävien listasta
- Tehtäviä voi myös poistaa
- q-kirjain toimii ohjelman pysäyttämiseksi

## Viikko 5

- Lisätty `lint`-invoke-tehtävä pylint-tarkistusten suorittamiseen
- Lisätty arkkitehtuuridokumentti, jossa on rakennekaavio ja tehtävän luonnin sekvenssikaavio
- Päivitetty vaatimusmäärittelyyn toteutuneille ominaisuuksille `tehty`-merkinnät
- Päivitetty README:hen linkki arkkitehtuuridokumentaatioon ja pylint-ohje
