# Testausdokumentti

## Automaattinen testaus

Sovelluksen automaattiset testit suoritetaan komennolla:

```bash
poetry run invoke test
```

Testikattavuusraportti luodaan komennolla:

```bash
poetry run invoke coverage-report
```

Raportti muodostuu hakemistoon `htmlcov`.

Automaattiset testit keskittyvät sovelluslogiikkaan ja tietokantakerrokseen. Graafista Tkinter-käyttöliittymää ja komentorivikäyttöliittymää ei lasketa coverage-raporttiin, koska käyttöliittymiä testataan pääasiassa manuaalisesti ja varsinainen sovelluslogiikka sijaitsee service- ja repository-kerroksissa.

## Yksikkötestaus

Yksikkötesteissä testataan erityisesti service-luokkien toimintaa valekomponenttien avulla:

- `AuthService`: rekisteröinti, kirjautuminen ja virheelliset tunnukset
- `SessionService`: kirjautumistilan hallinta
- `TaskService`: tehtävien luonti, muokkaus, valmistuminen, poistaminen, prioriteetti, määräpäivä ja haku
- `ProjectService`: projektien luonti, jäsenyys, tehtävien liittäminen projektiin, poistaminen ja haku
- `LabelService`: leimojen luonti, duplikaattien esto ja leimojen liittäminen tehtäviin
- `UserProfileService`: käyttäjäsivun tietojen kokoaminen

Testeissä tarkistetaan sekä onnistuneita käyttötapauksia että virheellisiä syötteitä.

## Integraatiotestaus

Repository-kerroksen testit käyttävät erillistä väliaikaista SQLite-testitietokantaa. Testeissä ei käytetä sovelluksen varsinaista `data/taskboard.db`-tietokantaa.

Integraatiotesteissä testataan muun muassa:

- käyttäjien luonti, haku ja listaus
- tehtävän elinkaari tietokannassa
- tehtävien käyttöoikeusrajaukset osallistujien perusteella
- projektien luonti, jäsenyys, haku ja poistaminen
- tehtävien liittäminen projektiin
- leimojen luonti, haku ja liittäminen tehtäviin
- käyttäjän kaikkien aktiivisten ja valmiiden tehtävien hakeminen käyttäjäsivua varten

## Järjestelmätestaus

Sovellusta on testattu manuaalisesti ajamalla graafinen käyttöliittymä komennolla:

```bash
poetry run invoke gui
```

Manuaalisesti tarkastettuja käyttötapauksia:

- uuden käyttäjän rekisteröinti
- kirjautuminen ja uloskirjautuminen
- tehtävän luominen, muokkaaminen, valmiiksi merkitseminen ja poistaminen
- projektin luominen ja poistaminen
- käyttäjien lisääminen projektiin
- projektitehtävän luominen
- olemassa olevan tehtävän lisääminen projektiin
- leiman luominen ja liittäminen tehtävään
- tehtävien ja projektien haku
- oman käyttäjäsivun avaaminen
- projektin luojan käyttäjäsivun avaaminen projektinäkymästä
- tehtävän luojan käyttäjäsivun avaaminen tehtävänäkymästä

Komentorivikäyttöliittymää on testattu vaihtoehtoisena käyttötapana komennolla:

```bash
poetry run invoke start
```

## Testikattavuus

Viimeisin testiajo:

```text
67 passed
```

Viimeisin coverage-raportti sovelluslogiikalle ja tietokantakerrokselle:

```text
TOTAL 84%
```

Coverage-raportista on rajattu pois:

- `src/ui/**`
- `src/gui/**`
- `src/tests/**`
- `__init__.py`-tiedostot

Rajaus on tehty, koska käyttöliittymäkerrosten toiminta testataan manuaalisesti ja automaattiset testit kohdistuvat sovelluksen sääntöihin, validointiin ja tietokantatoimintoihin.

## Laatuongelmat ja testauksen puutteet

Graafiselle käyttöliittymälle ei ole automaattisia käyttöliittymätestejä. Tkinter-näkymät on testattu manuaalisesti.

Sovelluksen tietokantatiedoston sijainti on määritelty koodissa. Jatkokehityksessä tietokannan polku olisi hyvä siirtää konfiguraatiotiedostoon tai ympäristömuuttujaan.

Graafinen käyttöliittymä sijaitsee yhdessä suuressa tiedostossa. Jatkokehityksessä näkymät olisi hyvä jakaa pienempiin moduuleihin.
