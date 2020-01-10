from django.conf import settings
from django.core.mail import send_mail

import logging
import smtplib


def get_email_data_from_weather(loc_weather):
    """Get info from Weather object into dict that will populate email

    Arguments:
        loc_weather {Weather} -- Weather object

    Returns:
        dict -- used to populate email
    """
    weather_data = {}
    weather_data['icon'] = loc_weather.weather_icon
    weather_data['temperature'] = loc_weather.temperature_today
    weather_data['description'] = loc_weather.weather_description
    weather_data['location'] = loc_weather.location

    return weather_data


def send_msg(subject_line, html, email, con):
    """Sends an email

    Arguments:
        subject_line {str}
        html {str} -- Email body
        email {list[str]} -- The addresses to send to
    """
    try:
        send_mail(
            subject_line,
            html,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=html,
            connection=con,
        )
    except smtplib.SMTPSenderRefused:
        logging.error("Unable to authenticate email settings - skipping message.", exc_info=True)
