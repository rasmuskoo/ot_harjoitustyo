# Käyttöohje

Tämä ohje kuvaa TaskBoard-sovelluksen käyttöä komentoriviltä. Ohje olettaa, että sovellusta suoritetaan palautusrepositoriosta käsin.

## Sovelluksen käynnistäminen

Asenna projektin riippuvuudet:

```bash
poetry install
```

Käynnistä sovellus:

```bash
poetry run invoke start
```

Sovellus avautuu kirjautumisnäkymään.

## Käyttäjän rekisteröinti

Kirjautumisnäkymässä sovellus pyytää sähköpostiosoitetta.

Luo uusi käyttäjä kirjoittamalla:

```text
register
```

Sovellus kysyy seuraavat tiedot:

- etunimi
- sukunimi
- sähköpostiosoite
- salasana
- salasanan vahvistus

Salasanan tulee olla vähintään kahdeksan merkkiä pitkä. Rekisteröinnin jälkeen sovellus palaa kirjautumisnäkymään.

## Kirjautuminen

Kirjaudu sisään syöttämällä rekisteröity sähköpostiosoite ja salasana.

Onnistuneen kirjautumisen jälkeen sovellus näyttää kotinäkymän, jossa näkyvät käyttäjän tehtävät ja projektit.

Sovelluksen voi sulkea kirjautumisnäkymässä tai kotinäkymässä kirjoittamalla:

```text
q
```

## Kotinäkymän toiminnot

Kotinäkymässä sovellus näyttää valikon. Valikon tärkeimmät toiminnot ovat:

```text
1 = päivitä näkymä
2 = kirjaudu ulos
3 = luo tehtävä
4 = muokkaa tehtävää
5 = merkitse tehtävä valmiiksi
6 = poista tehtävä
7 = näytä valmiit tehtävät
8 = luo projekti
9 = näytä projektit
10 = luo leima
11 = lisää leima tehtävään
q = sulje sovellus
```

Tehtäviin liittyvät valinnat `4`, `5`, `6` ja `11` ovat käytettävissä, kun käyttäjällä on vähintään yksi tehtävä.

## Tehtävän luominen

Luo tehtävä valitsemalla kotinäkymässä:

```text
3
```

Sovellus kysyy tehtävälle:

- otsikon
- kuvauksen
- tärkeyden
- määräpäivän

Tärkeyden sallitut arvot ovat:

```text
low
medium
high
```

Jos tärkeys jätetään tyhjäksi, sovellus käyttää arvoa `medium`.

Määräpäivä annetaan muodossa:

```text
YYYY-MM-DD
```

Määräpäivän voi jättää tyhjäksi.

## Projektin luominen

Luo projekti valitsemalla kotinäkymässä:

```text
8
```

Sovellus kysyy projektille:

- nimen
- tärkeyden
- määräpäivän
- projektiin lisättävät käyttäjät

Käyttäjät valitaan numerolistasta. Useita käyttäjiä voi valita kirjoittamalla numerot pilkuilla erotettuna, esimerkiksi:

```text
1,3,4
```

Projektin luoja lisätään projektiin automaattisesti, vaikka häntä ei valittaisi listasta.

## Projektien tarkastelu

Näytä omat projektit valitsemalla kotinäkymässä:

```text
9
```

Sovellus näyttää projektit numerolistana. Valitse projekti kirjoittamalla projektin numero.

Projektinäkymässä näkyvät:

- projektin nimi
- projektin tärkeys ja mahdollinen määräpäivä
- projektin jäsenet
- projektiin liitetyt tehtävät

## Tehtävän luominen projektiin

Avaa ensin projektinäkymä valinnalla:

```text
9
```

Valitse projekti ja sen jälkeen projektinäkymässä:

```text
2
```

Sovellus kysyy tehtävälle otsikon, kuvauksen, tärkeyden ja määräpäivän. Projektiin luotu tehtävä näkyy projektin jäsenille.

## Olemassa olevan tehtävän lisääminen projektiin

Avaa projektinäkymä valinnalla:

```text
9
```

Valitse projekti ja sen jälkeen projektinäkymässä:

```text
3
```

Sovellus näyttää käyttäjän tehtävät, joita ei ole vielä liitetty projektiin. Valitse lisättävä tehtävä kirjoittamalla tehtävän numero.

Kun tehtävä lisätään projektiin, se jaetaan projektin jäsenille.

## Projektin poistaminen

Avaa projektinäkymä valinnalla:

```text
9
```

Valitse projekti ja sen jälkeen projektinäkymässä:

```text
4
```

Sovellus pyytää vahvistuksen ennen projektin poistamista. Vahvista poisto kirjoittamalla:

```text
y
```

Vain projektin luoja voi poistaa projektin. Projektin poistaminen ei poista tehtäviä, vaan tehtävien projektiliitos poistetaan.

## Leimojen luominen ja liittäminen tehtäviin

Luo uusi leima valitsemalla kotinäkymässä:

```text
10
```

Anna leimalle nimi. Sovellus muuttaa leiman nimen pieniksi kirjaimiksi. Samannimistä leimaa ei voi luoda kahdesti.

Lisää leima tehtävään valitsemalla:

```text
11
```

Sovellus pyytää ensin valitsemaan tehtävän ja sen jälkeen leiman. Tehtävään liitetyt leimat näkyvät tehtävälistauksessa.

## Tehtävien muokkaaminen, valmistuminen ja poistaminen

Muokkaa tehtävää valitsemalla:

```text
4
```

Sovellus pyytää valitsemaan tehtävän ja antamaan uuden otsikon sekä kuvauksen.

Merkitse tehtävä valmiiksi valitsemalla:

```text
5
```

Valmiit tehtävät eivät näy aktiivisten tehtävien listassa. Valmiit tehtävät saa näkyviin valinnalla:

```text
7
```

Poista tehtävä valitsemalla:

```text
6
```

Sovellus pyytää valitsemaan poistettavan tehtävän numerolla.
