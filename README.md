# Meetup Facebook Bot

[![Build Status][build-badge]][build]
[![Coverage Status][coverage-badge]][coverage]
[![Code Climate][code-climate-badge]][code-climate]
[![License: MIT][license-badge]][license]

[build-badge]: https://travis-ci.org/Stark-Mountain/meetup-facebook-bot.svg?branch=master
[build]: https://travis-ci.org/Stark-Mountain/meetup-facebook-bot
[coverage-badge]: https://coveralls.io/repos/github/Stark-Mountain/meetup-facebook-bot/badge.svg?branch=master
[coverage]: https://coveralls.io/github/Stark-Mountain/meetup-facebook-bot
[code-climate-badge]: https://codeclimate.com/github/Stark-Mountain/meetup-facebook-bot.png?branch=master
[code-climate]: https://codeclimate.com/github/Stark-Mountain/meetup-facebook-bot
[license-badge]: https://img.shields.io/badge/License-MIT-yellow.svg?branch=master
[license]: https://opensource.org/licenses/MIT

An easy-to-setup bot that helps you to communicate with your meetup attendees.

With the carousel consisting of talks, it allows the users:
- receive detailed description of a talk
- rate a talk
- ask the speaker questions

The interface is currently in Russian (see [#101](https://github.com/Stark-Mountain/meetup-facebook-bot/issues/101))
![bot conversation](http://i.imgur.com/56efUoA.png)
# How to use

Once you've set the bot up (see below), just go to `https://(yourdomain)/login` and fill out the Speaker and Talk tables. (Ignore the `token` field of Speaker table).
![/admin screenshot](http://i.imgur.com/Gsf04UA.png)

# How to setup
Prerequisites: a computer with Ubuntu 16.04 and an associated domain name; registered [Facebook app](https://developers.facebook.com/docs/messenger-platform/guides/setup).

1. Get the code: `git clone https://github.com/Stark-Mountain/meetup-facebook-bot && cd meetup-facebook-bot`.
2. Put the address of Ubuntu 16.04 computer [here](https://github.com/Stark-Mountain/meetup-facebook-bot/blob/master/fabfile.py#L9).
3. You may want to activate virtual environment: `python3 -m venv venv && source venv/bin/activate`.
4. Install deployment dependencies: `pip install -r requirements-deploy.txt`.
5. Run `fab bootstrap` and follow further instructions. This will install and configure uWSGI with nginx; acquire SSL certificate for your domain and setup an automatic renewal.
6. Go to your domain and make sure everything's working.

# How to run tests
After all dependencies are installed (`pip install -r requirements.txt`), run the following command from the root folder of the project:

`$ python3 -m pytest tests`
