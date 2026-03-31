from src.repositories.database import initialize_database


def main() -> None:
    """Start the application."""
    initialize_database()
    print("TaskBoard Desktop version is running")


if __name__ == "__main__":
    main()
