import typing
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass, field
from apollo_shared.alembic import models as common_models
from sqlalchemy import Table, Column, ForeignKey, JSON, UUID as UUIDField, Text


@dataclass
class FeedEntity:
    rss_id: str
    data: dict
    guid: str

    id: typing.Optional[UUID] = None
    created_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )
    updated_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )


feeds = Table(
    'feeds', common_models.metadata,
    common_models.uuid_primary_key_column(),
    Column('rss_id', UUIDField(as_uuid=True), ForeignKey('rsses.id'), nullable=False),
    Column('data', JSON, default={}),
    Column("guid", Text),
    common_models.created_at_column(),
    common_models.updated_at_column(),
)

common_models.mapper_registry.map_imperatively(FeedEntity, feeds)
