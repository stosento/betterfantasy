from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from models.db_models import Base  # Assuming this is where your Base is defined
from models.db_models import Stinker as DBStinker
from sqlalchemy.exc import SQLAlchemyError

def clear_all_tables(db: Session):
    try:
        # Get the metadata
        metadata = Base.metadata

        # Create a list to store table names
        table_names = []

        # Get all tables and their foreign key dependencies
        inspector = inspect(db.get_bind())
        for table_name in inspector.get_table_names():
            fks = inspector.get_foreign_keys(table_name)
            if not fks:
                table_names.append(table_name)
            else:
                # Add tables with foreign keys later
                table_names.append(table_name)

        # Reverse the list to delete from tables without dependencies first
        table_names.reverse()

        # Disable foreign key constraints for the session
        db.execute(text("SET CONSTRAINTS ALL DEFERRED"))

        # Clear each table
        for table_name in table_names:
            db.execute(text(f'DELETE FROM "{table_name}"'))

        # Commit the changes
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"An error occurred while clearing tables: {e}")
        raise
    finally:
        # Re-enable foreign key constraints
        db.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))

    print("All tables have been cleared.")

def update_db_stinker(updated_game, db):
    stinker = db.query(DBStinker).filter(DBStinker.id == updated_game.id).first()
    try:
        if stinker:
            # Update fields individually
            for attr, value in updated_game.__dict__.items():
                if attr != 'id' and hasattr(stinker, attr):
                    setattr(stinker, attr, value)
            db.commit()
        else:
            raise ValueError(f"No Stinker found with id {updated_game.id}")
    except SQLAlchemyError as e:
        print(f"An error occurred while updating the Stinker: {str(e)}")
        db.rollback()
        raise
