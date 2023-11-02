from apollo_shared.schema import rss as rss_schema
from apollo_shared.utils import Context
from nameko.rpc import rpc
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
        result = rss_service.subscribe_rss(context, data)

        return rss_schema.SubscribeRSSSchemaRPCResponse().dump(result)

    @rpc
    def get_rsses(self, context: Context, data: rss_schema.GetRSSesSchemaRPC) -> rss_schema.GetRSSesSchemaRPCResponse:
        rss_service = self.__get_rss_service()
        result = rss_service.subscribe_rss(context, data)

        return rss_schema.GetRSSesSchemaRPCResponse(many=True).dump(result)

    @rpc
    def get_rss(self, context: Context, data: rss_schema.GetRSSSchemaRPC) -> rss_schema.GetRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service()
        result = rss_service.subscribe_rss(context, data)

        return rss_schema.GetRSSSchemaRPCResponse().dump(result)

    @rpc
    def unsubscribe_rss(self, context: Context,
                        data: rss_schema.UnsubscribeRSSSchemaRPC):
        rss_service = self.__get_rss_service()
        rss_service.unsubscribe_rss(context, data['id'])

    @rpc
    def get_feed_of_subscribed_rss(self, context: Context,
                                   data: rss_schema.GetFeedOfSubscribedRSSSchemaRPC) -> rss_schema.GetFeedOfSubscribedRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service()
        result = rss_service.get_feed_of_subscribed_rss(context, data['id'])

        return rss_schema.GetFeedOfSubscribedRSSSchemaRPCResponse().dump(result)

    @rpc
    def get_feeds_of_subscribed_rss(self, context: Context,
                                    data: rss_schema.GetFeedsOfSubscribedRSSSchemaRPC) -> rss_schema.GetFeedsOfSubscribedRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service()
        result = rss_service.subscribe_rss(context, data)

        return rss_schema.SubscribeRSSSchemaRPCResponse().dump(result)

    @rpc
    def get_feeds_of_rss(self, context: Context,
                         data) -> rss_schema.GetFeedsOfSubscribedRSSSchemaRPCResponse:
        rss_service = self.__get_rss_service()
        result = rss_service.subscribe_rss(context, data)

        return rss_schema.SubscribeRSSSchemaRPCResponse().dump(result)

    @rpc
    def health_check(self):
        return {}

    def __get_rss_service(self, context: Context) -> RssService:
        rss_dal = RssDAL(
            db_session=self.db.session,
        )

        return RssService(
            context=context,
            rss_dal=rss_dal,
        )
