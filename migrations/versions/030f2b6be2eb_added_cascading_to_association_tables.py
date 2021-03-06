"""added cascading to association tables

Revision ID: 030f2b6be2eb
Revises: 21ca63bde648
Create Date: 2018-05-28 16:48:11.169578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '030f2b6be2eb'
down_revision = '21ca63bde648'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('dest_tags_dest_id_fkey', 'dest_tags', type_='foreignkey')
    op.drop_constraint('dest_tags_tag_id_fkey', 'dest_tags', type_='foreignkey')
    op.create_foreign_key(None, 'dest_tags', 'tags', ['tag_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(None, 'dest_tags', 'destinations', ['dest_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_constraint('explored_dest_id_fkey', 'explored', type_='foreignkey')
    op.drop_constraint('explored_user_id_fkey', 'explored', type_='foreignkey')
    op.create_foreign_key(None, 'explored', 'users', ['user_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(None, 'explored', 'destinations', ['dest_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_constraint('favorites_user_id_fkey', 'favorites', type_='foreignkey')
    op.drop_constraint('favorites_dest_id_fkey', 'favorites', type_='foreignkey')
    op.create_foreign_key(None, 'favorites', 'destinations', ['dest_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(None, 'favorites', 'users', ['user_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'favorites', type_='foreignkey')
    op.drop_constraint(None, 'favorites', type_='foreignkey')
    op.create_foreign_key('favorites_dest_id_fkey', 'favorites', 'destinations', ['dest_id'], ['id'])
    op.create_foreign_key('favorites_user_id_fkey', 'favorites', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'explored', type_='foreignkey')
    op.drop_constraint(None, 'explored', type_='foreignkey')
    op.create_foreign_key('explored_user_id_fkey', 'explored', 'users', ['user_id'], ['id'])
    op.create_foreign_key('explored_dest_id_fkey', 'explored', 'destinations', ['dest_id'], ['id'])
    op.drop_constraint(None, 'dest_tags', type_='foreignkey')
    op.drop_constraint(None, 'dest_tags', type_='foreignkey')
    op.create_foreign_key('dest_tags_tag_id_fkey', 'dest_tags', 'tags', ['tag_id'], ['id'])
    op.create_foreign_key('dest_tags_dest_id_fkey', 'dest_tags', 'destinations', ['dest_id'], ['id'])
    op.alter_column('dest_images', 'img_url',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###
