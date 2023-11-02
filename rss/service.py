from apollo_shared.schema import rss as rss_schema
from apollo_shared.utils import Context
from .models.rss import RssEntity, RssUserEntity

from .dal import RssDAL


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
            rss_entity = RssEntity(
                url=data['url'],
            )

            self.rss_dal.create_rss(rss_entity)

        if self.rss_dal.fetch_if_user_attach_to_rss(
                user_id=self.context['user_id'],
                rss_id=str(rss_entity.id),
        ):
            raise Exception("User has been subscribe to rss!")

        self.rss_dal.attach_rss_to_user(
            RssUserEntity(
                user_id=self.context['user_id'],
                rss_id=str(rss_entity.id),
            )
        )

        return rss_entity

    def unsubscribe_rss(
            self,
            rss_id,
    ) -> None:

        if self.rss_dal.fetch_if_user_attach_to_rss(
                user_id=self.context['user_id'],
                rss_id=str(rss_id),
        ):
            self.rss_dal.detach_rss_to_user(
                str(rss_id),
            )

    def get_rsses(self):
        user_id = self.context['user_id']

        return self.rss_dal.get_rsses(user_id)

    def get_rss(self, rss_id):
        user_id = self.context['user_id']

        result = self.rss_dal.get_rss_by_rss_id_and_user_id(rss_id, user_id)

        if result is None:
            raise Exception("Rss {} not found!".format(rss_id))

        return result

    def get_feed_of_subscribed_rss(self, feed_id):
        return self.rss_dal.get_feed_by_id_and_user_id(
            feed_id,
            self.context['user_id'],
        )

    def get_feeds_of_subscribed_rss(self):
        return self.rss_dal.get_feeds_by_id_and_user_id(
            self.context['user_id'],
        )

    def get_feeds_of_rss(self, rss_id):
        return self.rss_dal.get_feeds_by_rss_id_and_user_id(
            rss_id,
            self.context['user_id'],
        )
