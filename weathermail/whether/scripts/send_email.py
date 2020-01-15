from django.core.exceptions import ObjectDoesNotExist
from django.core import mail
from whether.models import Subscriber, Weather
from whether.utils.email_content import (
    CRUMMY_WEATHER_SUBJECT,
    EMAIL_BODY,
    NEUTRAL_WEATHER_SUBJECT,
    NICE_WEATHER_SUBJECT,
    UPDATE_INFO_EMAIL_BODY,
    UPDATE_INFO_SUBJECT,
    NO_WEATHER_EMAIL_BODY,
    NO_WEATHER_SUBJECT,
)
from whether.utils.email_utils import (
    get_email_data_from_weather,
    send_msg,
)
from whether.utils.weather import (
    get_all_other_cities,
    get_cities_with_crummy_weather,
    get_cities_with_good_weather,
    update_weather,
    weather_valid,
)

import logging


def get_or_refresh_con(con=None):
    """If the connection breaks, make a new one so mailing can continue
    
    Arguments:
        con  -- django mail server connection
    """
    if not con:
        con = mail.get_connection()
        con.open()
    return con


def send_no_weather_mail(subs, con):
    """Send users an email saying that we don't have
    weather for their city, but we will have it back soon

    Arguments:
        subs {list of Subcribers} -- The list of emails we want to inform
    """
    for s in subs:
        subscriber_id = s.pk
        email_body = NO_WEATHER_EMAIL_BODY.format(subscriber_id=subscriber_id)
        subject_line = NO_WEATHER_SUBJECT
        send_msg(subject_line, email_body, s.email, con)
    logging.info('Done sending backup mail for location with no weather found.')


def send_city_mail(l, subject_line, con):
    """Send mail with weather to all subscribers for a given city

    Arguments:
        l {Location} -- Location to send mail for
        subject_line {str} -- Subject line for city - varies based on weather
    """
    con = get_or_refresh_con(con)
    logging.info(f'Sending mail for {l}')

    # Get Subscribers, and weather for a city
    subs = Subscriber.objects.filter(location=l)
    try:
        loc_weather = Weather.objects.get(location=l)
        if not weather_valid(loc_weather):
            raise ObjectDoesNotExist()
    except ObjectDoesNotExist:
        logging.error(f'No weather object found for {l}. Sending those users an error email', exc_info=False)
        send_no_weather_mail(subs, con)
        return

    # Get info from Weather object to populate email
    try:
        weather_data = get_email_data_from_weather(loc_weather)
    except KeyError:
        logging.error(f'Missing weather data found for {l}. Sending those users an error email', exc_info=False)
        send_no_weather_mail(subs, con)
        return

    # Populate and send email
    for s in subs:
        subscriber_id = s.pk
        email_body = EMAIL_BODY.format(subscriber_id=subscriber_id, **weather_data)
        send_msg(subject_line, email_body, s.email, con)
    logging.info('Sent all mail for {l}')


def send_no_location_mail(con):
    """Send to all users who have no location, informing them that they need to update
    their location so we can send them the best mail
    """
    con = get_or_refresh_con(con)
    subs = Subscriber.objects.filter(location__isnull=True)
    for s in subs:
        subscriber_id = s.pk
        email_body = UPDATE_INFO_EMAIL_BODY.format(subscriber_id=subscriber_id)
        subject_line = UPDATE_INFO_SUBJECT
        send_msg(subject_line, email_body, s.email, con)


def run():
    logging.info('Updating weather')
    update_weather()
    logging.info('Segmenting cities by weather status')
    good_weather_cities = get_cities_with_good_weather()
    poor_weather_cities = get_cities_with_crummy_weather(good_weather_cities)
    other_cities = get_all_other_cities(good_weather_cities, poor_weather_cities)

    # Manually open the connection since we are sending many messages
    con = get_or_refresh_con()
    logging.info('Beginning email send process')
    for l in good_weather_cities:
        send_city_mail(l, NICE_WEATHER_SUBJECT, con)
    for l in poor_weather_cities:
        send_city_mail(l, CRUMMY_WEATHER_SUBJECT, con)
    for l in other_cities:
        send_city_mail(l, NEUTRAL_WEATHER_SUBJECT, con)
    logging.info('Sending email update template to users with no location')
    send_no_location_mail(con)
    con.close()
    logging.info('Email send process complete')
