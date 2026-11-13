from getpass import getpass

from sqlalchemy import create_engine, text, URL

password = getpass("PostgreSQL password: ")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password=password,
    host="localhost",
    port=5432,
    database="datastream_db"
    )

engine = create_engine(database_url)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), version()")
        )
        
        database, version = result.one()

        print("Connection successful!")
        print(f"Database: {database}")
        print(f"PostgreSQL: {version.split(',')[0]}")

finally:
    engine.dispose()


