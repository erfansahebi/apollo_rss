import json

from apollo_shared.schema import rss as rss_schema
from apollo_shared.utils import Context
from nameko.rpc import rpc
from nameko.timer import timer
from apollo_shared.rpc.rss import RssRPC
from nameko_sqlalchemy import Database
from apollo_shared.alembic.models import Base as DeclarativeBase
from .service import RssService
from .dal import RssDAL


class RssController(RssRPC):
    db = Database(DeclarativeBase)

    @rpc
    def subscribe_rss(self,
                      context: Context,
                      data: rss_schema.SubscribeRSSSchemaRPC
                      ) -> rss_schema.SubscribeRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        result = rss_service.subscribe_rss(data)

        return rss_schema.SubscribeRSSSchemaRPCResponse().dump(result)

    @rpc
    def unsubscribe_rss(self, context: Context,
                        data: rss_schema.UnsubscribeRSSSchemaRPC):
        rss_service = self.__get_rss_service(context)
        rss_service.unsubscribe_rss(data)


    @rpc
    def get_rsses(self, context: Context, data: rss_schema.GetRSSesSchemaRPC) -> rss_schema.GetRSSesSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        user_rsses = rss_service.get_rsses()

        return rss_schema.GetRSSesSchemaRPCResponse(many=True).dump(user_rsses)

    @rpc
    def get_rss(self, context: Context, data: rss_schema.GetRSSSchemaRPC) -> rss_schema.GetRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        result = rss_service.get_rss(data)

        return rss_schema.GetRSSSchemaRPCResponse().dump(result)

    @rpc
    def get_feed_of_subscribed_rss(self,
                                   context: Context,
                                   data: rss_schema.GetFeedOfSubscribedRSSSchemaRPC
                                   ) -> rss_schema.GetFeedOfSubscribedRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        feed = rss_service.get_feed_of_subscribed_rss(data)

        return rss_schema.GetFeedOfSubscribedRSSSchemaRPCResponse().dump(feed)

    @rpc
    def get_feeds_of_subscribed_rsses(self,
                                      context: Context,
                                      data: rss_schema.GetFeedsOfSubscribedRSSesSchemaRPC
                                      ) -> rss_schema.GetFeedsOfSubscribedRSSesSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        feeds = rss_service.get_feeds_of_subscribed_rsses()

        return rss_schema.GetFeedsOfSubscribedRSSesSchemaRPCResponse(many=True).dump(feeds)

    @rpc
    def get_feeds_of_subscribed_rss(self,
                                    context: Context,
                                    data: rss_schema.GetFeedsOfSubscribedRSSSchemaRPC
                                    ) -> rss_schema.GetFeedsOfSubscribedRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)

        feeds = rss_service.get_feeds_of_subscribed_rss(data)

        return rss_schema.GetFeedsOfSubscribedRSSSchemaRPCResponse(many=True).dump(feeds)

    @rpc
    def add_comment_on_feed(self,
                            context: Context,
                            data: rss_schema.AddCommentOnFeedSchemaRPC
                            ) -> rss_schema.AddCommentOnFeedSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        comment = rss_service.add_comment_on_feed(data)

        return rss_schema.AddCommentOnFeedSchemaRPCResponse().dump(comment)

    @rpc
    def get_comments_on_feed(self,
                             context: Context,
                             data: rss_schema.GetCommentsOnFeedSchemaRPC
                             ) -> rss_schema.GetCommentsOnFeedSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        comments = rss_service.get_comments_on_subscribed_feed(data)

        return rss_schema.GetCommentsOnFeedSchemaRPCResponse(many=True).dump(comments)

    @rpc
    def get_comment_on_feed(self,
                            context: Context,
                            data: rss_schema.GetCommentOnFeedSchemaRPC
                            ) -> rss_schema.GetCommentOnFeedSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        comment = rss_service.get_comment_on_subscribed_feed(data)

        return rss_schema.GetCommentOnFeedSchemaRPCResponse().dump(comment)

    @rpc
    def delete_comment_on_feed(self,
                               context: Context,
                               data: rss_schema.DeleteCommentOnFeedSchemaRPC
                               ) -> rss_schema.DeleteCommentOnFeedSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        rss_service.delete_user_comment(data)

        return rss_schema.DeleteCommentOnFeedSchemaRPCResponse().dump({})

    @rpc
    def add_to_bookmarks(self,
                         context: Context,
                         data: rss_schema.AddToBookmarksSchemaRPC
                         ) -> rss_schema.AddToBookmarksSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        new_bookmark = rss_service.add_feed_to_bookmarks(data)

        return rss_schema.AddToBookmarksSchemaRPCResponse().dump(new_bookmark)

    @rpc
    def get_bookmarks(self,
                      context: Context,
                      data: rss_schema.GetBookmarksSchemaRPC
                      ) -> rss_schema.GetBookmarksSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        bookmarks = rss_service.get_user_bookmarks()
        return rss_schema.GetBookmarksSchemaRPCResponse(many=True).dump(bookmarks)

    @rpc
    def get_bookmark(self,
                     context: Context,
                     data: rss_schema.GetBookmarkSchemaRPC
                     ) -> rss_schema.GetBookmarkSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        bookmark = rss_service.get_user_bookmark(data)

        return rss_schema.GetBookmarkSchemaRPCResponse().dump(bookmark)

    @rpc
    def delete_from_bookmarks(self,
                              context: Context,
                              data: rss_schema.DeleteFromBookmarksSchemaRPC
                              ) -> rss_schema.DeleteFromBookmarksSchemaRPCResponse:
        rss_service = self.__get_rss_service(context)
        rss_service.delete_user_bookmark(data)

        return rss_schema.DeleteFromBookmarksSchemaRPCResponse().dump({})

    @timer(interval=60)
    def update_feeds(self):
        rss_service = self.__get_rss_service(Context())
        rss_service.update_feeds()

    def __get_rss_service(self, context: Context) -> RssService:
        rss_dal = RssDAL(
            db_session=self.db.session,
        )

        return RssService(
            context=context,
            rss_dal=rss_dal,
        )
