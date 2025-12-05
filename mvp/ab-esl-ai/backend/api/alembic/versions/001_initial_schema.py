"""Initial schema creation

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create class_sessions table
    op.create_table(
        'class_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('class_code', sa.String(8), unique=True, nullable=False, index=True),
        sa.Column('teacher_name', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('closed_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    
    # Create participants table
    op.create_table(
        'participants',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('class_sessions.id'), nullable=False),
        sa.Column('nickname', sa.String(100), nullable=False),
        sa.Column('l1', sa.String(10), default='en'),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    
    # Create index on session_id for faster lookups
    op.create_index('ix_participants_session_id', 'participants', ['session_id'])
    
    # Create transcripts table
    op.create_table(
        'transcripts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('class_sessions.id'), nullable=False),
        sa.Column('participant_id', sa.Integer(), sa.ForeignKey('participants.id')),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('simplified_text', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create index on session_id for transcripts
    op.create_index('ix_transcripts_session_id', 'transcripts', ['session_id'])
    
    # Create reading_results table
    op.create_table(
        'reading_results',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('class_sessions.id'), nullable=False),
        sa.Column('participant_id', sa.Integer(), sa.ForeignKey('participants.id'), nullable=False),
        sa.Column('passage_id', sa.String(50)),
        sa.Column('passage_text', sa.Text(), nullable=False),
        sa.Column('transcribed_text', sa.Text(), nullable=False),
        sa.Column('wpm', sa.Float()),
        sa.Column('wcpm', sa.Float()),
        sa.Column('accuracy', sa.Float()),
        sa.Column('errors', sa.JSON()),
        sa.Column('audio_url', sa.String(500)),
        sa.Column('duration_seconds', sa.Float()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create indexes for reading_results
    op.create_index('ix_reading_results_session_id', 'reading_results', ['session_id'])
    op.create_index('ix_reading_results_participant_id', 'reading_results', ['participant_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_reading_results_participant_id')
    op.drop_index('ix_reading_results_session_id')
    op.drop_table('reading_results')
    
    op.drop_index('ix_transcripts_session_id')
    op.drop_table('transcripts')
    
    op.drop_index('ix_participants_session_id')
    op.drop_table('participants')
    
    op.drop_table('class_sessions')
