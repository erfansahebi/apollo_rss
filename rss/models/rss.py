import typing
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass, field
from apollo_shared.alembic import models as common_models
from sqlalchemy import Table, Column, Text, ForeignKey, UUID as UUIDField


@dataclass
class RssEntity:
    url: str

    id: typing.Optional[UUID] = None
    created_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )
    updated_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )


rsses = Table(
    'rsses', common_models.metadata,
    common_models.uuid_primary_key_column(),
    Column(name="url", type_=Text),
    common_models.created_at_column(),
    common_models.updated_at_column(),
)

common_models.mapper_registry.map_imperatively(RssEntity, rsses)


@dataclass
class RssUserEntity:
    user_id: UUID
    rss_id: UUID

    id: typing.Optional[UUID] = None
    created_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )
    updated_at: typing.Optional[datetime] = field(
        default_factory=datetime.utcnow
    )


rss_user = Table(
    'rss_user', common_models.metadata,
    common_models.uuid_primary_key_column(),
    Column("user_id", UUIDField(as_uuid=True), nullable=False),
    Column('rss_id', UUIDField(as_uuid=True), ForeignKey('rsses.id'), nullable=False),
    common_models.created_at_column(),
    common_models.updated_at_column(),
)

common_models.mapper_registry.map_imperatively(RssUserEntity, rss_user)
