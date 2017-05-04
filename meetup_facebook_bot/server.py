from flask import Flask, request, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from meetup_facebook_bot.messenger import message_validators, message_handlers

app = Flask(__name__)
app.config.from_object('config')
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
db_session = Session()


def is_facebook_challenge_request(request):
    if request.args.get('hub.mode') != 'subscribe':
        return False
    if not request.args.get('hub.challenge'):
        return False
    return True


@app.route('/')
def verify():
    params = {'PAGE_ID': app.config['PAGE_ID'], 'APP_ID': app.config['APP_ID']}
    if not is_facebook_challenge_request(request):
        return render_template('index.html', **params)
    if request.args.get('hub.verify_token') != app.config['VERIFY_TOKEN']:
        return 'Verification token mismatch', 403
    return request.args['hub.challenge'], 200


def extract_messaging_events(entries):
    return [messaging_event for entry in entries for messaging_event in entry['messaging']]


@app.route('/', methods=['POST'])
def webhook():
    facebook_request = request.get_json()
    if facebook_request['object'] != 'page':
        return 'Object is not a page', 400
    messaging_events = extract_messaging_events(facebook_request['entry'])
    message_processors = [
        (
            message_validators.is_talk_info_command,
            message_handlers.handle_talk_info_command
        ),
        (
            message_validators.is_talk_rate_command,
            message_handlers.handle_talk_rate_command
        ),
        (
            message_validators.is_talk_like_command,
            message_handlers.handle_talk_like_command
        ),
        (
            message_validators.is_talk_like_command,
            message_handlers.handle_message_with_sender_id
        ),
        (
            message_validators.has_sender_id,
            message_handlers.handle_message_with_sender_id
        )
    ]
    access_token = app.config['ACCESS_TOKEN']
    for messaging_event in messaging_events:
        for message_validator, message_handler in message_processors:
            if message_validator(messaging_event):
                message_handler(messaging_event, access_token, db_session)
    return 'Success.', 200


if __name__ == '__main__':
    app.run(debug=True)
