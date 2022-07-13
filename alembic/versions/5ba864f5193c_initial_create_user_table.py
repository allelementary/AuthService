"""initial: create user table

Revision ID: 5ba864f5193c
Revises: 
Create Date: 2022-07-12 19:39:40.572621

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import text

# revision identifiers, used by Alembic.
revision = '5ba864f5193c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False,
                  server_default=text("gen_random_uuid()")),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('api_key', sa.String(), nullable=True),
        sa.Column('api_secret', sa.String(), nullable=True),
        sa.Column('chat_id', sa.String(), nullable=True),
        sa.Column('scopes', sa.ARRAY(sa.String), nullable=True, server_default="{}"),

        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )


def downgrade():
    op.drop_table('users')
