from rss.models.rss import RssEntity, RssUserEntity
from rss.models.feed import FeedEntity


class RssDAL:

    def __init__(self, db_session):
        self.db_session = db_session

    def fetch_rss_by_url_or_none(self, url: str) -> RssEntity | None:
        return self.db_session.query(RssEntity).filter(
            RssEntity.url == url
        ).one_or_none()

    def create_rss(self, entity: RssEntity) -> None:
        self.db_session.add(entity)
        self.db_session.commit()

    def fetch_if_user_attach_to_rss(self, user_id: str, rss_id: str) -> RssEntity | None:
        return self.db_session.query(RssUserEntity).filter(
            RssUserEntity.user_id == user_id,
            RssUserEntity.rss_id == rss_id,
        ).first()

    def attach_rss_to_user(self, entity: RssUserEntity):
        self.db_session.add(entity)
        self.db_session.commit()

    def detach_rss_to_user(self, rss_id):
        self.db_session.query(RssUserEntity).filter(
            RssUserEntity.id == rss_id,
        ).delete()

    def get_rsses(self, user_id):
        return self.db_session.query(
            RssEntity,
            RssUserEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssUserEntity.user_id == user_id
        ).all()

    def get_rss_by_rss_id_and_user_id(self, rss_id, user_id):
        return self.db_session.query(
            RssEntity,
            RssUserEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssUserEntity.user_id == user_id
        ).filter(
            RssEntity.id == rss_id
        ).first()

    def get_feed_by_id_and_user_id(self, feed_id, user_id):
        return self.db_session.query(
            FeedEntity,
            RssUserEntity,
        ).filter(
            FeedEntity.rss_id == RssUserEntity.rss_id
        ).filter(
            RssUserEntity.user_id == user_id
        ).filter(
            FeedEntity.id == feed_id
        ).first()

    def get_feeds_by_user_id(self, user_id):
        return self.db_session.query(
            FeedEntity,
            RssEntity,
            RssUserEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssEntity.id == FeedEntity.rss_id
        ).filter(
            RssUserEntity.user_id == user_id
        ).all()

    def get_feeds_by_rss_id_and_user_id(self, rss_id, user_id):
        return self.db_session.query(
            FeedEntity,
            RssEntity,
            RssUserEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssEntity.id == FeedEntity.rss_id
        ).filter(
            RssUserEntity.user_id == user_id
        ).filter(
            RssEntity.id == rss_id
        ).all()
