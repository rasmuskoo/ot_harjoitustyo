# Arkkitehtuuri

![Arkkitehtuurikaavio](./architecture.png)

## Pakkausrakenne

```mermaid
classDiagram
    class SignInView
    class SignUpView
    class HomeView
    class AuthService
    class SessionService
    class TaskService
    class UserRepository
    class TaskRepository
    class User
    class Task

    SignInView --> AuthService
    SignInView --> SessionService
    SignInView --> SignUpView
    SignUpView --> AuthService
    HomeView --> SessionService
    HomeView --> TaskService
    HomeView --> TaskRepository

    AuthService --> UserRepository
    TaskService --> TaskRepository

    UserRepository --> User
    TaskRepository --> Task
```

Sovellus jakautuu kolmeen pääkerrokseen:

- `ui` käsittelee käyttäjän syötteet ja tulostuksen komentoriville
- `services` sisältää sovelluslogiikan ja syötteiden validoinnin
- `repositories` vastaa tietokantaan tallentamisesta ja hakemisesta

## Sekvenssikaavio: tehtävän luonti

```mermaid
sequenceDiagram
    actor User
    participant HomeView
    participant TaskService
    participant TaskRepository
    participant Database

    User->>HomeView: valitsee "create task"
    HomeView->>HomeView: kysyy otsikon ja kuvauksen
    HomeView->>TaskService: create_task(title, description, user_id)
    TaskService->>TaskService: validoi syöte
    TaskService->>TaskRepository: create_task(task)
    TaskRepository->>Database: INSERT INTO tasks
    Database-->>TaskRepository: uusi task id
    TaskRepository-->>TaskService: luotu Task
    TaskService->>TaskRepository: add_participant(task_id, user_id)
    TaskRepository->>Database: INSERT INTO task_participants
    TaskRepository-->>TaskService: ok
    TaskService-->>HomeView: luotu Task
    HomeView-->>User: "Task created"
```
