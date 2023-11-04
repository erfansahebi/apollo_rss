import typing
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass, field
from apollo_shared.alembic import models as common_models
from sqlalchemy import Table, Column, ForeignKey, JSON, UUID as UUIDField, Text


@dataclass
class CommentEntity:
    user_id: str
    feed_id: str
    message: str

    id: typing.Optional[UUID] = None
    created_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )
    updated_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )


comments = Table(
    'comments', common_models.metadata,
    common_models.uuid_primary_key_column(),
    Column('feed_id', UUIDField(as_uuid=True), ForeignKey('feeds.id')),
    Column('user_id', UUIDField(as_uuid=True)),
    Column('message', Text),
    common_models.created_at_column(),
    common_models.updated_at_column(),
)

common_models.mapper_registry.map_imperatively(CommentEntity, comments)
