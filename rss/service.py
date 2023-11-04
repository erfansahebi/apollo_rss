import feedparser

from apollo_shared import exception
from apollo_shared.schema import rss as rss_schema
from apollo_shared.utils import Context
from .models.rss import RssEntity, RssUserEntity
from .models.feed import FeedEntity
from .models.bookmark import BookmarkEntity
from .models.comment import CommentEntity
from .dal import RssDAL
from uuid import uuid4

class RssService:

    def __init__(self, context: Context, rss_dal: RssDAL):
        self.context = context
        self.rss_dal = rss_dal

    def subscribe_rss(
            self,
            data: rss_schema.SubscribeRSSSchemaRPC
    ) -> RssEntity:
        rss_entity = self.rss_dal.fetch_rss_by_url_or_none(data['url'])

        if rss_entity is None:
            if len(feedparser.parse(data['url']).entries) == 0:
                raise exception.BadRequest('invalid RRS')

            rss_entity = RssEntity(
                url=data['url'],
            )

            self.rss_dal.create_rss(rss_entity)

        if self.rss_dal.check_user_attached_to_rss(
                user_id=self.context['user_id'],
                rss_id=rss_entity.id,
        ):
            raise exception.BadRequest("user has been subscribe to rss!")

        self.rss_dal.attach_rss_to_user(
            RssUserEntity(
                user_id=self.context['user_id'],
                rss_id=rss_entity.id,
            )
        )

        return rss_entity

    def unsubscribe_rss(
            self,
            data: rss_schema.UnsubscribeRSSSchemaRPC,
    ) -> None:

        if self.rss_dal.check_user_attached_to_rss(
                user_id=self.context['user_id'],
                rss_id=data['id'],
        ) is None:
            raise exception.NotFound('rss user not found')

        self.rss_dal.detach_rss_from_user(
            self.context['user_id'],
            data['id'],
        )

    def get_rsses(self):
        user_id = self.context['user_id']

        return self.rss_dal.get_rsses(user_id)

    def get_rss(self, data: rss_schema.GetRSSSchemaRPC) -> RssEntity:
        user_id = self.context['user_id']

        rss = self.rss_dal.get_rss_by_rss_id_and_user_id(data['id'], user_id)

        if rss is None:
            raise exception.NotFound("rss not found!")

        return rss

    def get_feed_of_subscribed_rss(self, data: rss_schema.GetFeedOfSubscribedRSSSchemaRPC):
        return self.rss_dal.get_feed_by_id_and_user_id(
            data['id'],
            self.context['user_id'],
        )

    def get_feeds_of_subscribed_rsses(self):
        return self.rss_dal.get_feeds_by_user_id(
            self.context['user_id'],
        )

    def get_feeds_of_subscribed_rss(self, data: rss_schema.GetFeedsOfSubscribedRSSSchemaRPC):
        return self.rss_dal.get_feeds_by_rss_id_and_user_id(
            data['rss_id'],
            self.context['user_id'],
        )

    def add_feed_to_bookmarks(self, data: rss_schema.AddToBookmarksSchemaRPC) -> BookmarkEntity:
        if self.rss_dal.fetch_bookmark_by_user_id_and_feed_id(self.context['user_id'], data['feed_id']) is not None:
            raise exception.BadRequest('bookmark exists')

        bookmark = BookmarkEntity(
            user_id=self.context['user_id'],
            feed_id=data['feed_id'],
        )

        self.rss_dal.store_bookmark(bookmark)

        return bookmark

    def get_user_bookmarks(self):
        return self.rss_dal.fetch_bookmarks_by_user_id(self.context['user_id'])

    def get_user_bookmark(self, data: rss_schema.GetBookmarkSchemaRPC) -> BookmarkEntity:
        bookmark = self.rss_dal.fetch_bookmark_by_id_and_user_id(data['bookmark_id'], self.context['user_id'])

        if bookmark is None:
            raise exception.NotFound('bookmark not found')

        return bookmark

    def delete_user_bookmark(self, data: rss_schema.DeleteFromBookmarksSchemaRPC) -> None:
        self.rss_dal.delete_bookmark_by_id_and_user_id(data['bookmark_id'], self.context['user_id'])

    def add_comment_on_feed(self, data: rss_schema.AddCommentOnFeedSchemaRPC) -> CommentEntity:
        comment = CommentEntity(
            user_id=self.context['user_id'],
            feed_id=data['feed_id'],
            message=data['message'],
        )

        self.rss_dal.store_comment(comment)

        return comment

    def get_comments_on_subscribed_feed(self, data: rss_schema.GetCommentsOnFeedSchemaRPC):
        return self.rss_dal.fetch_comments_on_subscribed_feed_by_feed_id(data['feed_id'], self.context['user_id'])

    def get_comment_on_subscribed_feed(self, data: rss_schema.GetCommentOnFeedSchemaRPC) -> CommentEntity:
        comment = self.rss_dal.fetch_comment_on_subscribed_feed_by_feed_id(
            data['comment_id'],
            data['feed_id'],
            self.context['user_id'],
        )

        if comment is None:
            raise exception.NotFound('comment not found')

        return comment

    def delete_user_comment(self, data: rss_schema.DeleteCommentOnFeedSchemaRPC) -> None:
        self.rss_dal.delete_comment_by_id_and_user_id(data['comment_id'], self.context['user_id'])

    def update_feeds(self) -> None:
        rsses = self.rss_dal.get_all_rsses()
        last_feed_guids = {(str(feed.rss_id), feed.guid) for feed in self.rss_dal.get_rsses_last_feeds()}
        new_feeds = []

        for rss in rsses:
            parsed_data = feedparser.parse(rss.url)

            for entry in parsed_data.entries:
                rss_id = rss.id
                guid = entry['id']

                if (str(rss_id), guid) in last_feed_guids:
                    break

                new_feeds.append(
                    FeedEntity(
                        rss_id=rss_id,
                        data=dict(entry),
                        guid=guid,
                    )
                )

        self.rss_dal.insert_feeds(new_feeds)
