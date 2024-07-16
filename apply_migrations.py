# apply_migrations.py

import os
import sys
from alembic.config import Config
from alembic import command

def apply_migrations():
    # Create an Alembic configuration object
    alembic_cfg = Config("alembic.ini")

    # Run the upgrade command to apply all pending migrations
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    apply_migrations()
    print("Migrations applied successfully.")