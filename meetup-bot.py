import os

import flask

import messaging
import messenger_profile


def extract_all_messaging_events(entries):
    messaging_events = []
    for entry in entries:
        for messaging_event in entry['messaging']:
            messaging_events.append(messaging_event)
    return messaging_events


def is_quick_button_pressed(messaging_event):
    if 'message' not in messaging_event:
        return False;
    if 'quick_reply' not in messaging_event['messaging']:
        return False;
    return True;


def is_schedule_button_pressed(messaging_event):
    if not is_quick_button_pressed(messaging_event):
        return False
    return messaging_event['payload'] == 'schedule payload'


app = flask.Flask(__name__)


@app.route('/')
def verify():
    params = {'PAGE_ID': os.environ['PAGE_ID'], 'APP_ID' : os.environ['APP_ID']}
    if flask.request.args.get('hub.mode') != 'subscribe':
        return flask.render_template('index.html', **params)
    if not flask.request.args.get('hub.challenge'):
        return flask.render_template('index.html', **params)
    if flask.request.args.get('hub.verify_token') != os.environ['VERIFY_TOKEN']:
        return 'Verification token mismatch', 403
    return flask.request.args['hub.challenge'], 200


@app.route('/', methods=['POST'])
def webhook():
    facebook_request = flask.request.get_json()
    access_token = os.environ['ACCESS_TOKEN']
    if facebook_request['object'] != 'page':
        return 'Object is not a page', 400

    messaging_events = extract_all_messaging_events(facebook_request['entry'])
    for messaging_event in messaging_events:
        sender_id = messaging_event['sender']['id']
        messaging.send_main_menu(access_token, sender_id)
    return 'Success.', 200


messenger_profile.set_get_started_button(os.environ['ACCESS_TOKEN'], 'get started payload')


if __name__ == '__main__':
    app.run(debug=True)
