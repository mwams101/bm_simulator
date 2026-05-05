"""add destination_schema_id to migration_jobs

Revision ID: a1c3e7f92b04
Revises: 35e09cb95575
Create Date: 2026-05-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a1c3e7f92b04'
down_revision: Union[str, Sequence[str], None] = '35e09cb95575'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'migration_jobs',
        sa.Column('destination_schema_id', sa.Integer(), nullable=True)
    )
    with op.batch_alter_table('migration_jobs') as batch_op:
        batch_op.create_foreign_key(
            'fk_migration_jobs_destination_schema_id',
            'destination_schemas',
            ['destination_schema_id'],
            ['id']
        )


def downgrade() -> None:
    with op.batch_alter_table('migration_jobs') as batch_op:
        batch_op.drop_constraint(
            'fk_migration_jobs_destination_schema_id',
            type_='foreignkey'
        )
        batch_op.drop_column('destination_schema_id')