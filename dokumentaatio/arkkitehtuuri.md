# Arkkitehtuuri

TaskBoard on kerrosarkkitehtuuria noudattava Python-sovellus. Sovelluksen ensisijainen käyttöliittymä on Tkinterillä toteutettu graafinen käyttöliittymä. Sen lisäksi sovelluksessa on vaihtoehtoinen komentorivikäyttöliittymä.

![Arkkitehtuurikaavio](./architecture.png)

## Pakkausrakenne

Sovelluksen koodi on jaettu seuraaviin pakkauksiin:

- `gui`: Tkinter-käyttöliittymä
- `ui`: komentorivikäyttöliittymä
- `services`: sovelluslogiikka ja validointi
- `repositories`: SQLite-tietokannan käsittely
- `entities`: sovelluksen tietomallit

```mermaid
classDiagram
    class TaskBoardApp
    class GuiHomeView
    class GuiProjectView
    class GuiTaskView
    class GuiUserProfileView
    class CliHomeView
    class AuthService
    class SessionService
    class TaskService
    class ProjectService
    class LabelService
    class UserProfileService
    class UserRepository
    class TaskRepository
    class ProjectRepository
    class LabelRepository
    class User
    class Task
    class Project
    class Label

    TaskBoardApp --> GuiHomeView
    TaskBoardApp --> AuthService
    TaskBoardApp --> SessionService
    TaskBoardApp --> TaskService
    TaskBoardApp --> ProjectService
    TaskBoardApp --> LabelService
    TaskBoardApp --> UserProfileService

    GuiHomeView --> TaskService
    GuiHomeView --> ProjectService
    GuiHomeView --> LabelService
    GuiProjectView --> ProjectService
    GuiProjectView --> TaskService
    GuiTaskView --> TaskRepository
    GuiUserProfileView --> UserProfileService

    CliHomeView --> TaskService
    CliHomeView --> ProjectService
    CliHomeView --> LabelService
    CliHomeView --> UserProfileService

    AuthService --> UserRepository
    TaskService --> TaskRepository
    ProjectService --> ProjectRepository
    ProjectService --> TaskRepository
    LabelService --> LabelRepository
    LabelService --> TaskRepository
    UserProfileService --> UserRepository
    UserProfileService --> ProjectRepository
    UserProfileService --> TaskRepository

    UserRepository --> User
    TaskRepository --> Task
    ProjectRepository --> Project
    LabelRepository --> Label
```

## Käyttöliittymäkerros

Graafinen käyttöliittymä sijaitsee `gui`-pakkauksessa. Sen pääluokka on `TaskBoardApp`, joka alustaa repositoriot ja palvelut sekä vaihtaa näkyvissä olevaa Tkinter-näkymää. Graafisen käyttöliittymän näkymiä ovat esimerkiksi kirjautumisnäkymä, kotinäkymä, projektinäkymä, tehtävänäkymä ja käyttäjäsivu.

Komentorivikäyttöliittymä sijaitsee `ui`-pakkauksessa. Se käyttää samoja service- ja repository-luokkia kuin graafinen käyttöliittymä. Tämän vuoksi molemmat käyttöliittymät käyttävät samaa sovelluslogiikkaa ja samaa tietokantaa.

Käyttöliittymäkerros ei vastaa pysyväistallennuksesta eikä varsinaisista liiketoimintasäännöistä. Se kerää käyttäjän syötteet, kutsuu service-luokkia ja näyttää tulokset käyttäjälle.

## Sovelluslogiikka

Kirjautumiseen ja rekisteröintiin liittyvä logiikka on `AuthService`-luokassa. Rekisteröinnissä tarkistetaan pakolliset kentät, sähköpostiosoitteen muoto, salasanan pituus, salasanan vahvistus ja sähköpostiosoitteen yksilöllisyys. Kirjautuneen käyttäjän tilaa ylläpitää `SessionService`.

Tehtäviin liittyvä logiikka on `TaskService`-luokassa. Palvelu vastaa tehtävän luonnin, muokkauksen, valmiiksi merkitsemisen, poistamisen ja haun validoinnista. Tehtävä voidaan luoda itsenäisenä tehtävänä tai projektin sisäisenä tehtävänä. Tehtävän näkyvyys perustuu `task_participants`-tauluun, eli käyttäjä näkee tehtävät, joissa hän on osallistujana.

Projektien hallinta on `ProjectService`-luokan vastuulla. Palvelu vastaa projektin luonnista, projektin tietojen hakemisesta, olemassa olevan tehtävän liittämisestä projektiin, projektin poistamisesta ja projektien hausta. Projektin luoja lisätään aina projektin jäseneksi. Projektin poistaminen on sallittu vain projektin luojalle.

Leimoihin liittyvä logiikka on `LabelService`-luokassa. Palvelu normalisoi leiman nimen, estää tyhjät ja päällekkäiset nimet sekä tarkistaa, että leima lisätään vain tehtävään, joka näkyy kirjautuneelle käyttäjälle.

Käyttäjäsivun tiedot kokoaa `UserProfileService`. Palvelu hakee käyttäjän perustiedot, projektit joissa käyttäjä on jäsenenä sekä tehtävät joissa käyttäjä on osallistujana. Käyttäjäsivua käytetään sekä oman sivun näyttämiseen että projektien ja tehtävien luojien tarkasteluun.

## Haku

Hakutoiminto on jaettu tehtävien ja projektien hakuun. `TaskService` välittää tehtävähakupyynnöt `TaskRepository`-luokalle, joka hakee käyttäjälle näkyviä tehtäviä otsikon ja kuvauksen perusteella. `ProjectService` välittää projektihakupyynnöt `ProjectRepository`-luokalle, joka hakee käyttäjän projektijäsenyyksien kautta näkyviä projekteja nimen perusteella.

Haku ei palauta muiden käyttäjien yksityisiä tehtäviä tai projekteja, vaan se käyttää samoja näkyvyysrajoja kuin tavallinen tehtävä- ja projektilistaus.

## Tietojen pysyväistallennus

Tietojen pysyväistallennus on toteutettu SQLite-tietokannalla. Tietokanta sijaitsee tiedostossa `data/taskboard.db`. Tietokanta alustetaan sovelluksen käynnistyessä `initialize_database`-funktion avulla. Sama funktio luo tarvittavat taulut ja lisää vanhoihin paikallisiin tietokantoihin puuttuvia sarakkeita.

Tietokannan keskeiset taulut ovat:

| Taulu | Tarkoitus |
| --- | --- |
| `users` | Rekisteröidyt käyttäjät |
| `tasks` | Tehtävät, niiden tila, tärkeys, määräpäivä ja mahdollinen projektiliitos |
| `projects` | Projektit |
| `labels` | Tehtäviin liitettävät leimat |
| `task_participants` | Käyttäjien osallistuminen tehtäviin |
| `project_members` | Käyttäjien jäsenyys projekteissa |
| `task_labels` | Tehtävien ja leimojen liitokset |

Tehtävien näkyvyys määräytyy `task_participants`-taulun perusteella. Projektien näkyvyys määräytyy `project_members`-taulun perusteella. Projektitehtävä jaetaan projektin jäsenille lisäämällä projektin jäsenet tehtävän osallistujiksi.

## Keskeiset tietomallit

Sovelluksen keskeiset entity-luokat ovat:

- `User`: käyttäjän nimi, sähköposti, salasanatiiviste ja tunniste
- `Task`: tehtävän otsikko, kuvaus, luoja, tärkeys, määräpäivä, tila ja projektiliitos
- `Project`: projektin nimi, luoja, tärkeys ja määräpäivä
- `Label`: leiman nimi

Entity-luokat ovat yksinkertaisia dataluokkia. Sovelluslogiikka sijaitsee service-luokissa eikä entity-luokissa.

## Sekvenssikaavio: tehtävän luonti

```mermaid
sequenceDiagram
    actor User
    participant HomeView
    participant TaskService
    participant TaskRepository
    participant Database

    User->>HomeView: valitsee uuden tehtävän luonnin
    HomeView->>HomeView: kysyy otsikon, kuvauksen, tärkeyden ja määräpäivän
    HomeView->>TaskService: create_task(title, description, TaskCreationContext)
    TaskService->>TaskService: validoi syöte ja kirjautunut käyttäjä
    TaskService->>TaskRepository: create_task(task)
    TaskRepository->>Database: INSERT INTO tasks
    Database-->>TaskRepository: uusi tehtävän id
    TaskRepository-->>TaskService: luotu Task
    TaskService->>TaskRepository: add_participants(task_id, participant_ids)
    TaskRepository->>Database: INSERT INTO task_participants
    TaskRepository-->>TaskService: ok
    TaskService-->>HomeView: luotu Task
    HomeView-->>User: tehtävä näkyy tehtävälistassa
```

## Sekvenssikaavio: käyttäjäsivun näyttäminen

```mermaid
sequenceDiagram
    actor User
    participant ProfileView
    participant UserProfileService
    participant UserRepository
    participant ProjectRepository
    participant TaskRepository
    participant Database

    User->>ProfileView: avaa käyttäjäsivun
    ProfileView->>UserProfileService: get_profile(user_id)
    UserProfileService->>UserRepository: find_by_id(user_id)
    UserRepository->>Database: SELECT FROM users
    Database-->>UserRepository: käyttäjän tiedot
    UserProfileService->>ProjectRepository: list_projects_for_user(user_id)
    ProjectRepository->>Database: SELECT projects JOIN project_members
    Database-->>ProjectRepository: projektit
    UserProfileService->>TaskRepository: list_all_tasks_for_user(user_id)
    TaskRepository->>Database: SELECT tasks JOIN task_participants
    Database-->>TaskRepository: tehtävät
    UserProfileService-->>ProfileView: UserProfile
    ProfileView-->>User: näyttää projektit ja tehtävät
```
