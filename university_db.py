from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import databases

DATABASE_URL = "sqlite:///./university.db"

# for async queries
database = databases.Database(DATABASE_URL)

# for creating tables only
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_tables():
        with engine.connect() as conn:
            conn.execute(text("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
        )"""))
            conn.commit()
        
        with engine.connect() as conn:
            conn.execute(text("""CREATE TABLE IF NOT EXISTS universities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name text,
        country text,
                              rank integer,
                              score float
        )"""))
            conn.commit()
            
        with engine.connect() as conn:
            conn.execute(text("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        university_id INTEGER NOT NULL,
                              comment varchar(1200),
                              rating float
        )"""))
            conn.commit()
        