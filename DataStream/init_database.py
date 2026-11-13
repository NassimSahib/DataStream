from getpass import getpass

from database import (
    create_database_engine,
    initialize_database,
)


def main():
    password = getpass("PostgreSQL password: ")

    engine = create_database_engine(password)

    try:
        initialize_database(engine)
        print("Database tables initialized successfully!")

    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
