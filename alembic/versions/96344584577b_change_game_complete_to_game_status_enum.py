"""Change game_complete to game_status enum

Revision ID: 96344584577b
Revises: 58ada70297c9
Create Date: 2024-06-30 12:03:05.011118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96344584577b'
down_revision: Union[str, None] = '58ada70297c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create the enum type
    game_status = postgresql.ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETE', name='gamestatus')
    game_status.create(op.get_bind())
    
    # Add the new column
    op.add_column('stinkers', sa.Column('game_status', game_status, nullable=True))
    
    # Update the new column based on the old one, with proper casting
    op.execute("UPDATE stinkers SET game_status = CASE WHEN game_complete THEN 'COMPLETE'::gamestatus ELSE 'NOT_STARTED'::gamestatus END")
    
    # Make the new column not nullable
    op.alter_column('stinkers', 'game_status', nullable=False)
    
    # Drop the old column
    op.drop_column('stinkers', 'game_complete')

def downgrade():
    # Create the enum type (in case it doesn't exist in the downgrade scenario)
    game_status = postgresql.ENUM('NOT_STARTED', 'IN_PROGRESS', 'COMPLETE', name='gamestatus')
    game_status.create(op.get_bind(), checkfirst=True)

    # Add back the old column
    op.add_column('stinkers', sa.Column('game_complete', sa.Boolean(), nullable=True))
    
    # Update the old column based on the new one
    op.execute("UPDATE stinkers SET game_complete = (game_status = 'COMPLETE'::gamestatus)")
    
    # Make the old column not nullable
    op.alter_column('stinkers', 'game_complete', nullable=False)
    
    # Drop the new column
    op.drop_column('stinkers', 'game_status')
    
    # Drop the enum type
    op.execute('DROP TYPE gamestatus')
