import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("database_url")

engine = create_engine(database_url)

with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES"))
    for row in result.fetchall():
        print(row)
