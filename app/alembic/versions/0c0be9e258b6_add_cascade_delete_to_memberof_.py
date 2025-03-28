"""add cascade delete to memberof relationships

Revision ID: 0c0be9e258b6
Revises: 8ece0e3f8b73
Create Date: 2025-03-27 16:01:13.870002

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '0c0be9e258b6'
down_revision = '8ece0e3f8b73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Drop existing foreign key constraints
    op.drop_constraint('memberof_organization_id_fkey', 'memberof', type_='foreignkey')
    op.drop_constraint('memberof_member_id_fkey', 'memberof', type_='foreignkey')
    
    # Recreate foreign key constraints with ON DELETE CASCADE
    op.create_foreign_key(
        'memberof_organization_id_fkey',
        'memberof',
        'user',
        ['organization_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'memberof_member_id_fkey',
        'memberof',
        'user',
        ['member_id'],
        ['id'],
        ondelete='CASCADE'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Drop cascade foreign key constraints
    op.drop_constraint('memberof_organization_id_fkey', 'memberof', type_='foreignkey')
    op.drop_constraint('memberof_member_id_fkey', 'memberof', type_='foreignkey')
    
    # Recreate original foreign key constraints without cascade
    op.create_foreign_key(
        'memberof_organization_id_fkey',
        'memberof',
        'user',
        ['organization_id'],
        ['id']
    )
    op.create_foreign_key(
        'memberof_member_id_fkey',
        'memberof',
        'user',
        ['member_id'],
        ['id']
    )
    # ### end Alembic commands ###
