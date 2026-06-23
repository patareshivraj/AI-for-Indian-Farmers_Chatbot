import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("database_url"))

with engine.connect() as conn:
    print("Users:")
    users = conn.execute(text("SELECT user_id, role_id FROM user_master LIMIT 5")).fetchall()
    print(users)
