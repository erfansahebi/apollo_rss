import uuid

import pytest
from apollo_shared.exception import BadRequest, NotFound
from rss.dal import RssDAL
from rss.service import RssService
from rss.models.rss import RssEntity, RssUserEntity
from rss.models.feed import FeedEntity
from unittest.mock import patch, Mock
from unittest import mock


@pytest.fixture
def rss_data_sample() -> dict:
    return {
        'url': 'https://erfan.com',
    }


@pytest.fixture
@mock.patch('rss.service.feedparser.parse')
def rss_model(mock_feedparser_parse, rss_controller, context, rss_data_sample) -> dict:
    mock_feedparser_result = Mock()
    mock_feedparser_result.entries = [{'title': 'Test Feed'}]
    mock_feedparser_parse.return_value = mock_feedparser_result

    rss_controller.subscribe_rss(context, rss_data_sample)


@pytest.fixture
def feed_model(rss_model, rss_controller, context, rss_data_sample, db_session) -> FeedEntity:
    rss = db_session.query(
        RssEntity,
    ).filter(
        RssEntity.id == RssUserEntity.rss_id
    ).filter(
        RssUserEntity.user_id == context['user_id']
    ).first()

    feed = FeedEntity(
        rss_id=rss.id,
        data={"title": "salam"},
        guid="http://guid.com",
    )

    db_session.add(feed)
    db_session.commit()

    return feed


@pytest.fixture
def feed_model_two(rss_model, rss_controller, context, rss_data_sample, db_session) -> FeedEntity:
    rss = db_session.query(
        RssEntity,
    ).filter(
        RssEntity.id == RssUserEntity.rss_id
    ).filter(
        RssUserEntity.user_id == context['user_id']
    ).first()

    feed = FeedEntity(
        rss_id=rss.id,
        data={"title": "salam2"},
        guid="http://guid2.com",
    )

    db_session.add(feed)
    db_session.commit()

    return feed


class TestRss:

    @mock.patch('rss.service.feedparser.parse')
    def test_subscribe_rss(self, mock_feedparser_parse, rss_controller, context, rss_data_sample):
        mock_feedparser_result = Mock()
        mock_feedparser_result.entries = [{'title': 'Test Feed'}]
        mock_feedparser_parse.return_value = mock_feedparser_result

        result = rss_controller.subscribe_rss(context, rss_data_sample)
        assert result['url'] == rss_data_sample['url']

        with pytest.raises(BadRequest, match="user has been subscribe to rss!"):
            rss_controller.subscribe_rss(context, rss_data_sample)

        mock_feedparser_result.entries = []
        mock_feedparser_parse.return_value = mock_feedparser_result
        rss_data_sample['url'] = "http://mamad.com"
        with pytest.raises(BadRequest, match="invalid RRS"):
            rss_controller.subscribe_rss(context, rss_data_sample)

    @mock.patch('rss.service.feedparser.parse')
    def test_get_rsses(self, mock_feedparser_parse, rss_controller, context, rss_data_sample):
        result = rss_controller.get_rsses(context, {})
        assert len(result) == 0

        mock_feedparser_result = Mock()
        mock_feedparser_result.entries = [{'title': 'Test Feed'}]
        mock_feedparser_parse.return_value = mock_feedparser_result

        rss_controller.subscribe_rss(context, rss_data_sample)
        result = rss_controller.get_rsses(context, {})
        assert len(result) > 0

    def test_get_rss(self, rss_model, rss_controller, rss_data_sample, db_session, context):
        rss = db_session.query(
            RssEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssUserEntity.user_id == context['user_id']
        ).first()

        result = rss_controller.get_rss(context, {
            "id": rss.id
        })

        assert result['url'] == rss_data_sample['url']

        context['user_id'] = uuid.uuid4()
        with pytest.raises(NotFound, match="rss not found!"):
            rss_controller.get_rss(context, {
                "id": rss.id
            })

    def test_unsubscribe_rss(self, rss_model, rss_controller, context, db_session):
        rss = db_session.query(
            RssEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssUserEntity.user_id == context['user_id']
        ).first()

        rss_controller.unsubscribe_rss(context, {
            "id": rss.id
        })

        context['user_id'] = uuid.uuid4()
        with pytest.raises(NotFound, match="rss user not found"):
            rss_controller.unsubscribe_rss(context, {
                "id": rss.id
            })

    def test_get_feed_of_subscribed_rss(self, feed_model, rss_controller, context):
        result = rss_controller.get_feed_of_subscribed_rss(context, {
            "id": feed_model.id
        })
        assert result['id'] is not None
        assert result['data']['title'] == "salam"

    def test_get_feeds_of_subscribed_rsses(self, feed_model, feed_model_two, rss_controller, context):
        result = rss_controller.get_feeds_of_subscribed_rsses(
            context,
            {}
        )
        assert len(result) == 2

    def test_get_feeds_of_subscribed_rss(self, db_session, feed_model, feed_model_two, rss_controller, context):
        rss = db_session.query(
            RssEntity,
        ).filter(
            RssEntity.id == RssUserEntity.rss_id
        ).filter(
            RssUserEntity.user_id == context['user_id']
        ).first()

        result = rss_controller.get_feeds_of_subscribed_rss(
            context, {
                "rss_id": rss.id,
            }
        )
        assert len(result) > 0

    # # Test cases for add_comment_on_feed function
    def test_add_comment_on_feed(self, feed_model, rss_controller, context):
        result = rss_controller.add_comment_on_feed(context, {
            "feed_id": feed_model.id,
            "message": "message",
        })
        assert result['message'] == "message"

    def test_get_comments_on_feed(self, feed_model, rss_controller, context):
        rss_controller.add_comment_on_feed(context, {
            "feed_id": feed_model.id,
            "message": "message",
        })

        result = rss_controller.get_comments_on_feed(
            context, {
                "feed_id": feed_model.id,
            }
        )
        assert len(result) > 0

    def test_get_comment_on_feed(self, feed_model, rss_controller, context):
        first_result = rss_controller.add_comment_on_feed(context, {
            "feed_id": feed_model.id,
            "message": "message",
        })

        second_result = rss_controller.get_comment_on_feed(
            context,
            {
                "feed_id": feed_model.id,
                "comment_id": uuid.UUID(first_result['id']),
            }
        )
        assert second_result['id'] == first_result['id']

    def test_delete_comment_on_feed(self, feed_model, rss_controller, context):
        first_result = rss_controller.add_comment_on_feed(context, {
            "feed_id": feed_model.id,
            "message": "message",
        })

        rss_controller.delete_comment_on_feed(
            context,
            {
                "comment_id": uuid.UUID(first_result['id'])
            }
        )

        result = rss_controller.get_comments_on_feed(
            context, {
                "feed_id": feed_model.id,
            }
        )
        assert len(result) == 0

    def test_add_to_bookmarks(self, feed_model, rss_controller, context):
        result = rss_controller.add_to_bookmarks(
            context,
            {
                "feed_id": feed_model.id
            }
        )
        assert result['feed_id'] == str(feed_model.id)

    def test_get_bookmarks(self, feed_model, rss_controller, context):
        rss_controller.add_to_bookmarks(
            context,
            {
                "feed_id": feed_model.id
            }
        )

        result = rss_controller.get_bookmarks(
            context,
            {}
        )
        assert len(result) == 1

    def test_get_bookmark(self, feed_model, rss_controller, context):
        with pytest.raises(NotFound, match="bookmark not found"):
            rss_controller.get_bookmark(
                context,
                {
                    "bookmark_id": uuid.uuid4()
                }
            )

        create_result = rss_controller.add_to_bookmarks(
            context,
            {
                "feed_id": feed_model.id
            }
        )

        result = rss_controller.get_bookmark(
            context,
            {
                "bookmark_id": uuid.UUID(create_result['id'])
            }
        )
        assert result['feed_id'] == str(feed_model.id)

    # # Test cases for delete_from_bookmarks function
    def test_delete_from_bookmarks(self, feed_model, rss_controller, context):
        create_result = rss_controller.add_to_bookmarks(
            context,
            {
                "feed_id": feed_model.id
            }
        )

        result = rss_controller.get_bookmark(
            context,
            {
                "bookmark_id": uuid.UUID(create_result['id'])
            }
        )
        rss_controller.delete_from_bookmarks(
            context,
            {
                "bookmark_id": uuid.UUID(result['id'])
            }
        )

        result = rss_controller.get_bookmarks(
            context,
            {}
        )

        assert len(result) == 0

    @mock.patch('rss.service.feedparser.parse')
    def test_update_feeds(self, mock_feedparser_parse, rss_model, rss_controller, db_session):
        mock_feedparser_result = Mock()
        mock_feedparser_result.entries = [
            {"id": 1, 'title': 'Test Feed1'},
            {"id": 2, 'title': 'Test Feed2'},
            {"id": 3, 'title': 'Test Feed3'},
            {"id": 4, 'title': 'Test Feed4'},
            {"id": 5, 'title': 'Test Feed5'},
        ]
        mock_feedparser_parse.return_value = mock_feedparser_result

        rss_controller.update_feeds()

        feeds = db_session.query(
            FeedEntity,
        ).all()

        assert len(feeds) == 5
