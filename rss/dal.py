import uuid

from rss.models.rss import RssEntity, RssUserEntity
from rss.models.feed import FeedEntity
from rss.models.bookmark import BookmarkEntity
from rss.models.comment import CommentEntity
from sqlalchemy import func, select


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

    def check_user_attached_to_rss(self, user_id: str, rss_id: uuid.UUID) -> RssEntity | None:
        return self.db_session.query(RssUserEntity).filter(
            RssUserEntity.user_id == user_id,
            RssUserEntity.rss_id == rss_id,
        ).first()

    def attach_rss_to_user(self, entity: RssUserEntity):
        self.db_session.add(entity)
        self.db_session.commit()

    def detach_rss_from_user(self, user_id, rss_id):
        self.db_session.query(RssUserEntity).filter(
            RssUserEntity.rss_id == rss_id,
            RssUserEntity.user_id == user_id,
        ).delete()
        self.db_session.commit()

    def get_rsses(self, user_id):
        return self.db_session.query(
            RssEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssUserEntity.user_id == user_id
        ).all()

    def get_rss_by_rss_id_and_user_id(self, rss_id, user_id) -> RssEntity | None:
        return self.db_session.query(
            RssEntity,
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
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssEntity.id == FeedEntity.rss_id
        ).filter(
            RssUserEntity.user_id == user_id
        ).filter(
            RssEntity.id == rss_id
        ).all()

    def store_bookmark(self, bookmark: BookmarkEntity) -> None:
        self.db_session.add(bookmark)
        self.db_session.commit()

    def fetch_bookmark_by_user_id_and_feed_id(self, user_id, feed_id) -> BookmarkEntity | None:
        return self.db_session.query(
            BookmarkEntity,
        ).filter(
            BookmarkEntity.user_id == user_id,
            BookmarkEntity.feed_id == feed_id,
        ).one_or_none()

    def fetch_bookmarks_by_user_id(self, user_id: str):
        return self.db_session.query(
            BookmarkEntity,
        ).filter(
            BookmarkEntity.user_id == user_id,
        ).all()

    def fetch_bookmark_by_id_and_user_id(self, bookmark_id: str, user_id: str) -> BookmarkEntity | None:
        return self.db_session.query(
            BookmarkEntity,
        ).filter(
            BookmarkEntity.id == bookmark_id,
            BookmarkEntity.user_id == user_id,
        ).one_or_none()

    def delete_bookmark_by_id_and_user_id(self, bookmark_id: str, user_id: str) -> None:
        self.db_session.query(
            BookmarkEntity,
        ).filter(
            BookmarkEntity.id == bookmark_id,
            BookmarkEntity.user_id == user_id,
        ).delete()
        self.db_session.commit()

    def store_comment(self, comment: CommentEntity) -> None:
        self.db_session.add(comment)
        self.db_session.commit()

    def fetch_comments_on_subscribed_feed_by_feed_id(self, feed_id: str, user_id: str):
        return self.db_session.query(
            CommentEntity,
        ).filter(
            CommentEntity.feed_id == feed_id,
        ).filter(
            FeedEntity.id == CommentEntity.feed_id,
        ).filter(
            FeedEntity.rss_id == RssUserEntity.rss_id,
        ).filter(
            RssUserEntity.user_id == user_id,
        ).all()

    def fetch_comment_on_subscribed_feed_by_feed_id(self,
                                                    comment_id: uuid.UUID,
                                                    feed_id: uuid.UUID,
                                                    user_id: uuid.UUID
                                                    ) -> CommentEntity | None:
        return self.db_session.query(
            CommentEntity,
        ).filter(
            CommentEntity.id == comment_id,
            CommentEntity.feed_id == feed_id,
        ).filter(
            FeedEntity.id == CommentEntity.feed_id,
        ).filter(
            FeedEntity.rss_id == RssUserEntity.rss_id,
        ).filter(
            RssUserEntity.user_id == user_id,
        ).one_or_none()

    def delete_comment_by_id_and_user_id(self, comment_id: str, user_id: str) -> None:
        self.db_session.query(
            CommentEntity,
        ).filter(
            CommentEntity.id == comment_id,
            CommentEntity.user_id == user_id,
        ).delete()
        self.db_session.commit()

    def get_all_rsses(self) -> [RssEntity]:
        return self.db_session.query(
            RssEntity,
        ).all()

    def insert_feeds(self, feeds: [FeedEntity]) -> None:
        self.db_session.bulk_save_objects(feeds)
        self.db_session.commit()

    def get_rsses_last_feeds(self) -> [FeedEntity]:
        subquery = self.db_session.query(
            FeedEntity,
            func.rank().over(
                order_by=FeedEntity.created_at.desc(),
                partition_by=FeedEntity.guid,
            ).label('rnk')
        ).subquery()

        return self.db_session.query(
            subquery,
        ).filter(
            subquery.c.rnk == 1,
        ).all()
