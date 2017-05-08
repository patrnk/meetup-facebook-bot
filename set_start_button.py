import os

from meetup_facebook_bot.messenger import messenger_profile


messenger_profile.set_get_started_button(
    os.environ['ACCESS_TOKEN'], 
   'get started payload'
)
