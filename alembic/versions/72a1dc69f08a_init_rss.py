"""init rss

Revision ID: 72a1dc69f08a
Revises: 
Create Date: 2023-11-01 18:42:21.672474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '72a1dc69f08a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'rsses',
        sa.Column(name='id', type_=sa.UUID(as_uuid=True)),
        sa.Column(name="url", type_=sa.Text),
        sa.Column(name='created_at', type_=sa.DateTime(timezone=True)),
        sa.Column(name='updated_at', type_=sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_table(
        'rss_user',
        sa.Column(name='id', type_=sa.UUID(as_uuid=True)),
        sa.Column(name='user_id', type_=sa.UUID(as_uuid=True), nullable=False),
        sa.Column(name='rss_id', type_=sa.UUID(as_uuid=True), nullable=False),
        sa.Column(name='created_at', type_=sa.DateTime(timezone=True)),
        sa.Column(name='updated_at', type_=sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['rss_id'], ['rsses.id'], name=op.f(
            'fk_rss_user_rss_id_rsses_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_rss_user'))
    )
    op.create_table(
        'feeds',
        sa.Column(name='id', type_=sa.UUID(as_uuid=True)),
        sa.Column(name='rss_id', type_=sa.UUID(as_uuid=True), nullable=False),
        sa.Column(name='guid', type_=sa.Text),
        sa.Column(name='data', type_=sa.JSON(), nullable=False),
        sa.Column(name='created_at', type_=sa.DateTime(timezone=True)),
        sa.Column(name='updated_at', type_=sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['rss_id'], ['rsses.id'], name=op.f(
            'fk_feeds_rss_id_rsses_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_feeds'))
    )
    op.create_table(
        'bookmarks',
        sa.Column(name='id', type_=sa.UUID(as_uuid=True)),
        sa.Column(name='user_id', type_=sa.UUID(as_uuid=True), nullable=False),
        sa.Column(name='feed_id', type_=sa.UUID(as_uuid=True), nullable=False),
        sa.Column(name='created_at', type_=sa.DateTime(timezone=True)),
        sa.Column(name='updated_at', type_=sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['feed_id'], ['feeds.id'], name=op.f(
            'fk_bookmarks_rss_id_rsses_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_bookmarks'))
    )
    op.create_table(
        'comments',
        sa.Column(name='id', type_=sa.UUID(as_uuid=True)),
        sa.Column(name='user_id', type_=sa.UUID(as_uuid=True), nullable=False),
        sa.Column(name='feed_id', type_=sa.UUID(as_uuid=True), nullable=False),
        sa.Column(name='message', type_=sa.Text, nullable=False),
        sa.Column(name='created_at', type_=sa.DateTime(timezone=True)),
        sa.Column(name='updated_at', type_=sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['feed_id'], ['feeds.id'], name=op.f(
            'fk_comments_feed_id_feeds_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_comments'))
    )


def downgrade() -> None:
    op.drop_table('rsses')
    op.drop_table('rss_user')
    op.drop_table('feeds')
    op.drop_table('bookmarks')
    op.drop_table('comments')
