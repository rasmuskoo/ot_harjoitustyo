# Käyttöohje

Tämä ohje kuvaa TaskBoard-sovelluksen käytön. Suositeltu käyttötapa on graafinen käyttöliittymä. Sovellusta voi käyttää myös vanhalla komentorivikäyttöliittymällä.

## Sovelluksen käynnistäminen

Asenna projektin riippuvuudet:

```bash
poetry install
```

Käynnistä graafinen käyttöliittymä:

```bash
poetry run invoke gui
```

Vaihtoehtoisesti komentorivikäyttöliittymän voi käynnistää komennolla:

```bash
poetry run invoke start
```

Sovellus avautuu kirjautumisnäkymään.

## Graafinen käyttöliittymä

### Käyttäjän rekisteröinti

Valitse kirjautumisnäkymässä `Create account`.

Syötä rekisteröintilomakkeelle:

- etunimi
- sukunimi
- sähköpostiosoite
- salasana
- salasanan vahvistus

Salasanan tulee olla vähintään kahdeksan merkkiä pitkä. Onnistuneen rekisteröinnin jälkeen sovellus palaa kirjautumisnäkymään.

### Kirjautuminen

Syötä kirjautumisnäkymässä sähköpostiosoite ja salasana. Valitse `Sign in`.

Onnistuneen kirjautumisen jälkeen avautuu kotinäkymä, jossa näkyvät käyttäjän aktiiviset tehtävät ja projektit.

### Kotinäkymä

Kotinäkymässä näkyy kaksi listaa:

- `Tasks`: käyttäjän aktiiviset tehtävät
- `Projects`: projektit, joissa käyttäjä on jäsenenä

Tehtävälistassa näkyvät tehtävän nimi, tärkeys, leimat, määräpäivä ja tila. Projektilistassa näkyvät projektin nimi, tärkeys ja määräpäivä.

Kotinäkymän yläreunasta voi:

- avata oman käyttäjäsivun valinnalla `My page`
- kirjautua ulos valinnalla `Sign out`
- hakea tehtäviä ja projekteja hakukentällä
- tyhjentää haun valinnalla `Clear`

### Tehtävän luominen

Luo uusi tehtävä valitsemalla tehtävälistan alta `New`.

Anna tehtävälle:

- otsikko
- kuvaus
- tärkeys
- määräpäivä muodossa `YYYY-MM-DD`, tai jätä kenttä tyhjäksi

Tärkeyden sallitut arvot ovat `low`, `medium` ja `high`.

### Tehtävän tarkastelu, muokkaaminen ja poistaminen

Valitse tehtävä tehtävälistasta. Tehtävän voi avata kaksoisklikkaamalla sitä tai valitsemalla `Open`.

Tehtäväsivulla näkyvät tehtävän tiedot ja painike `View creator`, josta voi avata tehtävän luojan käyttäjäsivun.

Kotinäkymässä valittua tehtävää voi käsitellä seuraavilla painikkeilla:

- `Edit`: muokkaa otsikkoa ja kuvausta
- `Complete`: merkitsee tehtävän valmiiksi
- `Delete`: poistaa tehtävän

Valmiit tehtävät eivät näy kotinäkymän aktiivisten tehtävien listassa, mutta ne näkyvät käyttäjäsivun tehtävälistassa.

### Leimojen luominen ja liittäminen tehtäviin

Luo uusi leima valitsemalla `New label`. Anna leimalle nimi.

Lisää leima tehtävään valitsemalla tehtävä tehtävälistasta ja sen jälkeen `Add label`. Valitse lisättävä leima avautuvasta ikkunasta.

Tehtävään liitetyt leimat näkyvät tehtävälistan `Labels`-sarakkeessa ja tehtäväsivulla.

### Projektin luominen

Luo projekti valitsemalla projektilistan alta `New project`.

Anna projektille:

- nimi
- tärkeys
- määräpäivä muodossa `YYYY-MM-DD`, tai jätä kenttä tyhjäksi
- projektin jäsenet käyttäjälistasta

Projektin luoja lisätään projektin jäseneksi automaattisesti.

### Projektin tarkastelu ja hallinta

Valitse projekti projektilistasta. Projektin voi avata kaksoisklikkaamalla sitä tai valitsemalla `Open`.

Projektisivulla näkyvät:

- projektin nimi
- tärkeys ja määräpäivä
- projektin jäsenet
- projektiin liitetyt tehtävät

Projektisivulta voi:

- avata projektin luojan käyttäjäsivun valinnalla `View creator`
- luoda projektiin uuden tehtävän valinnalla `Create task in project`
- lisätä olemassa olevan tehtävän projektiin valinnalla `Add existing task`
- avata projektin tehtävän valinnalla `Open task`
- poistaa projektin valinnalla `Delete project`

Vain projektin luoja voi poistaa projektin. Projektin poistaminen ei poista tehtäviä, vaan tehtävien projektiliitos poistetaan.

### Haku

Kirjoita hakusana kotinäkymän hakukenttään ja valitse `Search`.

Haku etsii:

- tehtäviä otsikon ja kuvauksen perusteella
- projekteja nimen perusteella

Haku näyttää vain kirjautuneelle käyttäjälle näkyvät tehtävät ja projektit. Tyhjennä haku valinnalla `Clear`.

### Käyttäjäsivu

Oman käyttäjäsivun voi avata kotinäkymästä valinnalla `My page`.

Muiden käyttäjien sivuille pääsee:

- projektisivulta valinnalla `View creator`
- tehtäväsivulta valinnalla `View creator`

Käyttäjäsivulla näkyvät käyttäjän nimi, sähköpostiosoite, projektit joissa käyttäjä on jäsenenä sekä tehtävät joissa käyttäjä on osallistujana.

## Komentorivikäyttöliittymä

Komentorivikäyttöliittymä on vaihtoehtoinen käyttötapa. Sen voi käynnistää komennolla:

```bash
poetry run invoke start
```

### Käyttäjän rekisteröinti

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

### Kirjautuminen

Kirjaudu sisään syöttämällä rekisteröity sähköpostiosoite ja salasana.

Onnistuneen kirjautumisen jälkeen sovellus näyttää kotinäkymän, jossa näkyvät käyttäjän tehtävät ja projektit.

Sovelluksen voi sulkea kirjautumisnäkymässä tai kotinäkymässä kirjoittamalla:

```text
q
```

### Kotinäkymän toiminnot

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
12 = hae tehtäviä ja projekteja
13 = näytä oma käyttäjäsivu
14 = näytä tehtäväsivu
q = sulje sovellus
```

Tehtäviin liittyvät valinnat `4`, `5`, `6`, `11` ja `14` ovat käytettävissä, kun käyttäjällä on vähintään yksi tehtävä.

### Tehtävän luominen

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

### Projektin luominen

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

### Projektien tarkastelu

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

### Tehtävän luominen projektiin

Avaa ensin projektinäkymä valinnalla:

```text
9
```

Valitse projekti ja sen jälkeen projektinäkymässä:

```text
2
```

Sovellus kysyy tehtävälle otsikon, kuvauksen, tärkeyden ja määräpäivän. Projektiin luotu tehtävä näkyy projektin jäsenille.

### Olemassa olevan tehtävän lisääminen projektiin

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

### Projektin poistaminen

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

### Leimojen luominen ja liittäminen tehtäviin

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

### Tehtävien muokkaaminen, valmistuminen ja poistaminen

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

### Haku ja käyttäjäsivu

Hae tehtäviä ja projekteja valitsemalla kotinäkymässä:

```text
12
```

Anna hakusana. Sovellus näyttää hakusanaan sopivat käyttäjälle näkyvät tehtävät ja projektit.

Avaa oma käyttäjäsivu valitsemalla:

```text
13
```

Käyttäjäsivulla näkyvät käyttäjän projektijäsenyydet ja tehtävät, joissa käyttäjä on osallistujana.

Avaa tehtäväsivu valitsemalla:

```text
14
```

Tehtäväsivulta voi avata tehtävän luojan käyttäjäsivun.
