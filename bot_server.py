import os
import json

import flask

import messaging
import messenger_profile
import message_processing


def load_json_from_file(filename):
    with open(filename) as json_file:
        return json.load(json_file)


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

    talks = load_json_from_file('example_talks.json')
    messaging_events = message_processing.extract_all_messaging_events(facebook_request['entry'])
    for messaging_event in messaging_events:
        sender_id = messaging_event['sender']['id']
        if message_processing.is_schedule_button_pressed(messaging_event):
            messaging.send_schedule(access_token, sender_id, talks)
        elif message_processing.is_more_talk_info_button_pressed(messaging_event):
            payload = messaging_event['postback']['payload']
            messaging.send_more_talk_info(access_token, sender_id, payload, talks)
        elif message_processing.is_like_talk_button_pressed(messaging_event):
            payload = messaging_event['postback']['payload']
            # TODO: actually set like
            messaging.send_like_confirmation(access_token, sender_id, payload, talks)

        messaging.send_main_menu(access_token, sender_id)
    return 'Success.', 200


messenger_profile.set_get_started_button(os.environ['ACCESS_TOKEN'], 'get started payload')


if __name__ == '__main__':
    app.run(debug=True)
