NICE_WEATHER_SUBJECT = "It's nice out! Enjoy a discount on us."
CRUMMY_WEATHER_SUBJECT = "Not so nice out? That's okay, enjoy a discount on us."
NEUTRAL_WEATHER_SUBJECT = "Enjoy a discount on us."
UPDATE_INFO_SUBJECT = "Uh-oh, looks like something is wrong on our end."
NO_WEATHER_SUBJECT = "No weather today, but please enjoy this discount!"
EMAIL_BODY = """
<html>
    <title>Weathermail</title>
    <body>
        <table border="0" cellpadding="0" cellspacing="0" width="700" bgcolor="#f5fffa" >
            <span style="font-family: 'Arial Black', Gadget, sans-serif; color: cadetblue;"
                <tr align="center"><h1>Weathermail</h1></tr>
            </span>
        </table>
        <table border="0" cellpadding="0" cellspacing="0" width="700" bgcolor="#f5fffa">
            <td>
                <img src="https://www.weatherbit.io/static/img/icons/{icon}.png" alt="Weather icon for {description}">
            </td>
            <td>
                <span style="font-family: 'Arial Black', Gadget, sans-serif; color: #444444;">
                    Hello, here is your daily weather report for <strong>{location}</strong>:
                    <br>Projected high temperature for today is: {temperature}°F.
                    <br>Projected weather for today is: {description}.
                    <br><br>Want weather from another city?
                    <br>Update your preferences here: http://localhost:8000/whether/{subscriber_id}/update/
                    <br>Weather data collected from: weatherbit.io
                </span>
            </td>
        </table>
    </body>
</html>
"""

UPDATE_INFO_EMAIL_BODY = """
<html>
    <title>Weathermail</title>
    <body>
        <table border="0" cellpadding="0" cellspacing="0" width="700" bgcolor="#f5fffa" >
            <span style="font-family: 'Arial Black', Gadget, sans-serif; color: cadetblue;"
                <tr align="center"><h1>Weathermail</h1></tr>
            </span>
        </table>
        <table border="0" cellpadding="0" cellspacing="0" width="700" bgcolor="#f5fffa">
            <td>
                <span style="font-family: 'Arial Black', Gadget, sans-serif; color: #444444;">
                    Uh-oh, something went wrong. It looks like we can't find a city for you.
                    <br>Please update your preferences here: http://localhost:8000/whether/{subscriber_id}/update/
                </span>
            </td>
        </table>
    </body>
</html>
"""

NO_WEATHER_EMAIL_BODY = """
<html>
    <title>Weathermail</title>
    <body>
        <table border="0" cellpadding="0" cellspacing="0" width="700" bgcolor="#f5fffa" >
            <span style="font-family: 'Arial Black', Gadget, sans-serif; color: cadetblue;"
                <tr align="center"><h1>Weathermail</h1></tr>
            </span>
        </table>
        <table border="0" cellpadding="0" cellspacing="0" width="700" bgcolor="#f5fffa">
            <td>
                <span style="font-family: 'Arial Black', Gadget, sans-serif; color: #444444;">
                    Uh-oh, something went wrong. It looks like we were unable to find weather data for you today.
                    Sorry about that!
                    <br><br>Want weather from another city?
                    <br>Update your preferences here: http://localhost:8000/whether/{subscriber_id}/update/
                    <br>Weather data collected from: weatherbit.io
                </span>
            </td>
        </table>
    </body>
</html>
"""
