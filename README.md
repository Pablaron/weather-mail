# Weathermail
A basic web app that collects email + location from users, and send them a tailored email each morning.
Original problem description and spec [here](https://www.klaviyo.com/weather-app).

## Features
- Dynamically loads 100 largest cities every time server is reloaded
- Users can sign up with their email to receive weather from one of those locations
	- Only acccepts one instance of an email
	- Hinted autocomplete suggests location based on what the user is typing.
- Grabs weather data only once per day to limit API calls
- Email send function sends user a different subject line based on the weather in their city
	- Email includes daily weather forecast
	- Email includes a link to change the location that the email is tied to
	- All users get sent, regardless of whether they have weather defined for their location or even if they don't have a location assigned at all


## Installation
1. Clone this repo
1. You'll probably want to make a new virtual environment to run this in.
I recommend [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/index.html).
1. `pip install -r requirements.txt` from the root of this repo. 
If you don't have pip installed, you can find it [here](https://pip.pypa.io/en/stable/installing/)
1. Create a local Postgres database named `weathermail`.
1. You will need three environment variables set in order to get email sending functionality:
	- `export EMAIL_HOST_USER='youremail@gmail.com'`
	- `export EMAIL_HOST_PASSWORD='your email password'`
	- Generate a WeatherBit API [here](https://www.weatherbit.io/account/create) and then
`export WEATHERBIT_KEY='your key here'`.
1. Are you using gmail? If so, you can skip this step - otherwise, you'll need to navigate to `weathermail/weathermail/settings.py` and update `EMAIL_HOST`, `EMAIL_USE_TLS`, and `EMAIL_PORT`. [This page](https://docs.djangoproject.com/en/3.0/topics/email/) should answer any questions you have about how to get set up.

## Usage
1. Navigate to the `weathermail/` folder and run `./manage.py runserver` to get the server set up.
This will run the server on port 8000 by default. 
Be sure to have the server running if you try to click the link in the email

#### How to sign up:
`localhost:8000/whether/subscribe`: Enter your email and your location, this information is saved to the server.

#### How to send yourself mail:
`./manage.py runscript send_email` will send messages from the email credentials defined earlier to all emails ethat are stored in the database.

#### Run unit tests:
`./manage.py test` from `/weathermail/` will run all the unit tests.

#### Suggested flow:
This flow should introduce you to all the features that Weathermail offers.

1. Start your server `./manage.py runserver`.
1. Sign up with an email at `localhost:8000/whether/subscribe/`
1. Send yourself an email using `./manage.py runscript send_email`
1. Click the link in the email, and change your location to something with a different weather state.
1. Send yourself a new email.
1. Create a superuser for yourself `./manage.py createsuperuser`.
1. Use those credentials to log into the admin site at `localhost:8000/admin`.
1. Delete all the Location objects using the admin interface.
1. Now, your Subscriber object should not be linked to a Location.
1. In order to re-grab cities, relaunch the server.
1. Send yourself another email - this one should inform you that there is no location set, and will prompt you to update that.
1. Update your location to "Boise City."
1. Send yourself one more email, so you can experience the [Boise Bug](#boise-bug), and notice how you are sent an email even though there is no weather data for your location.

## Design notes

#### On loading the 100 largest cities:
The problem definition requests that the top 100 cities be made available to users for autocompletion.
In order to do this, a dataset of the top 100 cities is downloaded, and loaded into the db every time the database is started up.
This is down by calling the function from `urls.py`. 
Calling it from this file ensures that it will be called exactly once, since that file is loaded exactly once on server startup/reload.

This script is allowed to fail relatively silently, because the list of the 100 largest cities likely does not change frequently - and even if it did, missing locations near the bottom of that list for a server cycle is not a critical error.

Locations are not deleted from the database as the 100 largest cities changes, as that would alter the experience of users that already signed up. 
The side effect of this is that over time, more and more locations will be stored in the database.

However, if a user's location becomes set to Null, the user will receive an email prompting them to choose a new location, and a link to a page to do so.

#### Signing up:
Only one instsance of each email is accepted on the signup page.
However, this unique constraint is NOT case or punctuation sensitive.
Each ISP has its own rules about email uniqueness, so I erred on the side of being less rigid with validation.

#### Defining good and poor weather:
Based on the spec, it is possible for a location to be both "good" and "bad" weather. 
As a reminder, good weather is:

- today's temp >= tomorrow's temp + 5 OR
- sunny weather 

while bad weather is:

- today's temp <= tomorrow's temp - 5 OR
- precipitation

A location could fall into both groups.
For example, if today is 6* warmer than tomorrow, but it is raining, it could be classified as either category.
Since I am a "glass half full" kind of guy, I chose to evaluate in this order:

- Good weather locations
- Bad weather locations
- All other locations

#### What is "sunny" and "precipitation"?
One component of "good weather" is the. state of sunniness. 
Sunniness, for the purpose of this app, is defined as weather codes:

- 800, Clear Sky
- 801, Few Clouds
- 802, Scattered Clouds

All other codes that are not in the 800s are considered precipitation weather codes.

[weather code reference](https://www.weatherbit.io/api/codes)

#### Forecast vs current weather observation
Another component of the weather states is comparing today's temperature to tomorrow's temperature.
There are two strategies that could be employed: 

1. Check current temperature vs tomorrow's projected high
1. Check today's projected high vs tomorrow's projected high

I chose to employ the second strategy, as this makes location status less dependent on what time the emails are sent.

A side effect of choosing the second strategy is that weather only needs to be updated once a day.
The free API level that I signed up for on Weatherbit only allows for 500 calls a day, so it is esecially important to limit API calls.

#### When there is no weather data
In the event that there is no weather data retrieved for a city, the user is still sent an email - just because we don't have weather for the location doesn't mean they don't want their daily discount!

## Email design
#### Unsubscribe
A key component of mass mailing is the inclusion of an unsubscribe link to remove users from the list.
I did not include that feature here.
If I were deploying this app in production, I would likely use an ESP to handle list management and email delivery - something like SendGrid or Mailgun. 

#### Icons
In each weather email, there is an icon included that corresponds to the weather code of the location of the user. 
Currently, these images are hosted by the weatherbit website.
Ideally, I would be hosting these images myself.
If this app were going to scale, this is one of the first tasks that would need to be done.

#### Mass mailing
Django has two built in mailing functions - `send_mail` and `send_mass_mail`. 
I elected not to use `send_mass_mail` because I wanted to include a link in each persons' email that they could click to update their info. 
Since this requires sending user-level specific data, I had to send each one separately.
Besides, the main performance gain comes from limiting the number of connections to the mail server, which I can do by managing the connection myself.

#### Accessibility
Accessibility is important, and one area that frequently gets overlooked is alt text tags on images.
Notice that the alt text tags in these emails are backed by a verbose description of the icon, pertaining to the weather that it describes.

## Known Bugs and Vulnerabilities

#### Django secret key
I currently have my Django secret key stored directly in `settings.py`.
That is because I do not plan on deploying this "IRL."
If I were going to, I'd use a secrets management platform like Vault.

#### Boise Bug
When downloading weather the data, the API is queried with city and state. 
However, there aren't always results for a given query, because the city stored in the "largest cities" dataset doesn't correspond to a city in the weatherbit API.

As of this writing, the only such city in the top 100 is "Boise City, Idaho" in the dataset, which does not return any results from Weatherbit.
The result is that users signing up for Boise weather will always receive the "no weather data" email.

A potential solution to this problem is to save city codes the Location model when downloading the weather, and if a query returns no results, an alert can be raised so that the end user can manually enter the city code.

#### URLs
`/whether/<pk>/success` and `/whether/<pk>/update` both use basic `pk` to personalize the page. 
This makes the structure of the pages very easy to access, regardless of who is making the request.
Using this formula, anybody can access and update data.

There are two potential fixes for this:
1. Create a full user object for the subscriber, and require them to be authenicated to access those pages
2. Hash the pk before passing it into the URL

#### Unverified emails
The only protections in place for email submissions are the ones provided out of the box by Django.
It's worth noting that these are relatively comprehensive, but they still leave open the opportunity for users to send us "bad" email addresses - either addresses that don't resolve, or are spam traps.

To fix this, we could use an email verification sservice, or attempt a send when the user signs up, and have them perform a double opt in to validate their email.

#### Autocomplete
When searching the autocomplete location field, you can search for either city or state, but not both at once.
Querying "Boston M" will return no cities.

## Other future improvements
What I would like to do if I had more time:

- Improve the UI. As I'm sure you can tell, this is not my strong suit.
- Add some flags to the email send script - for example:
	- a `--force-weather` flag that would re-get weather, regardless of how recently it was updated
	- a `--city` tag that will only send mail for one city
- There are almost certainly edge cases that I haven't considered in testing
## Acknowledgements
Thanks to django-autocomplete-light for writing a great autocomplete function, and to django girls for providing some great basic, reusable HTML.