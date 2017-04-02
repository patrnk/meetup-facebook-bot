import os

import flask

import hooks
import messenger_profile


app = flask.Flask(__name__)


@app.route('/')
def verify():
    params = {'page_id': os.environ['PAGE_ID'], 'app_id' : os.environ['APP_ID']}
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
    for entry in facebook_request['entry']:
        for messaging_event in entry['messaging']:
            hooks.send_main_menu(access_token, messaging_event)
    return 'Success.', 200


messenger_profile.set_get_started_button(os.environ['ACCESS_TOKEN'], 'get started payload')


if __name__ == '__main__':
    app.run(debug=True)
