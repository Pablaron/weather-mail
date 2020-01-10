from django.test import TestCase
from unittest.mock import MagicMock, patch
from whether.scripts.send_email import (
    get_or_refresh_con,
    send_city_mail,
    send_no_location_mail,
    UPDATE_INFO_SUBJECT
)
from whether.models import (
    Location,
    Weather,
)
from whether.factories import (
    SubscriberFactory,
    WeatherFactory,
)


class TestGetOrRefreshCon(TestCase):
    def test_returns_con_if_exists(self):
        con = 'connection'
        ret = get_or_refresh_con(con)
        self.assertEquals(con, ret)

    @patch('whether.scripts.send_email.mail.get_connection')
    def test_creates_new_con_if_con_not_passed(self, patch_get_con):
        mock_con = MagicMock()
        patch_get_con.return_value = mock_con
        ret = get_or_refresh_con()
        self.assertEqual(ret, mock_con)

    @patch('whether.scripts.send_email.mail.get_connection')
    def test_creates_new_con_if_con_not_truthy(self, patch_get_con):
        con = ''
        mock_con = MagicMock()
        patch_get_con.return_value = mock_con
        ret = get_or_refresh_con(con)
        self.assertEqual(ret, mock_con)


class TestSendCityMail(TestCase):

    @classmethod
    def setUpTestData(cls):
        Weather.objects.all().delete()

    @patch('whether.scripts.send_email.EMAIL_BODY')
    @patch('whether.scripts.send_email.send_msg')
    @patch('whether.scripts.send_email.get_email_data_from_weather')
    @patch('whether.scripts.send_email.mail.get_connection')
    def test_only_sends_users_for_city(self, patch_get_con, patch_get_weather, patch_send_msg, patch_email_body):
        sub = SubscriberFactory()
        [SubscriberFactory() for i in range(5)]
        [WeatherFactory(location=l) for l in Location.objects.all()]
        send_city_mail(sub.location, 'subject', 'connection')
        patch_send_msg.assert_called_with('subject', patch_email_body.format(), sub.email, 'connection')

    @patch('whether.scripts.send_email.send_no_weather_mail')
    @patch('whether.scripts.send_email.get_email_data_from_weather')
    @patch('whether.scripts.send_email.mail.get_connection')
    def test_sends_backup_email_if_no_weather(self, patch_get_con, patch_get_weather, patch_send_backup):
        sub = SubscriberFactory()
        send_city_mail(sub.location, 'subject', 'connection')
        assert patch_send_backup.called

    @patch('whether.scripts.send_email.send_no_weather_mail')
    @patch('whether.scripts.send_email.get_email_data_from_weather')
    @patch('whether.scripts.send_email.mail.get_connection')
    def test_sends_backup_email_if_missing_data(self, patch_get_con, patch_get_weather, patch_send_backup):
        sub = SubscriberFactory()
        [WeatherFactory(location=l) for l in Location.objects.all()]
        patch_get_weather.side_effect = KeyError
        send_city_mail(sub.location, 'subject', 'connection')
        assert patch_send_backup.called


class TestSendNoLocationMail(TestCase):

    @patch('whether.scripts.send_email.UPDATE_INFO_EMAIL_BODY')
    @patch('whether.scripts.send_email.send_msg')
    @patch('whether.scripts.send_email.get_or_refresh_con')
    def test_only_choose_users_with_no_location(self, patch_get_con, patch_send_msg, patch_email_body):
        sub = SubscriberFactory(location=None)
        [SubscriberFactory() for i in range(5)]
        send_no_location_mail('connection')
        patch_send_msg.assert_called_with(UPDATE_INFO_SUBJECT, patch_email_body.format(), sub.email, patch_get_con())
