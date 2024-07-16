import os
import sys
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

# Add the parent directory to sys.path to allow importing from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models.user import User  # Import all your models here
from models.team import Team
from models.player import Player
# ... import other models as needed

def table_exists(table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def create_tables():
    tables_to_create = [
        (User, "users"),
        (Team, "teams"),
        (Player, "players"),
        # Add other models and their table names here
    ]
    
    for model, table_name in tables_to_create:
        if not table_exists(table_name):
            print(f"Creating table: {table_name}")
            model.__table__.create(engine)
        else:
            print(f"Table {table_name} already exists")

if __name__ == "__main__":
    try:
        create_tables()
        print("Database setup completed successfully.")
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)