from flask import Flask, request, render_template, session, flash, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_babelex import Babel
from flask_admin import Admin
from flask_wtf import Form
from wtforms.fields import StringField, PasswordField
from wtforms import validators
import os
import datetime


from meetup_facebook_bot.messenger import message_validators, message_handlers
from meetup_facebook_bot.models.speaker import Speaker
from meetup_facebook_bot.models.talk import Talk


app = Flask(__name__)
babel = Babel(app)
app.config.from_object('config')
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
db_session = Session()


banned = {}

class TalkView(ModelView):
    list_columns = ['id','speaker_facebook_id', 'speaker', 'title', 'description',  'likes']
    form_base_class = SecureForm


class SpeakerView(ModelView):
    list_columns = ['facebook_id', 'name']
    form_base_class = SecureForm


admin = Admin(app, name='Facebook Meetup Bot', template_mode='bootstrap3')
admin.add_view(TalkView(Talk, db_session))
admin.add_view(SpeakerView(Speaker, db_session))


class LoginForm(Form):
    login = StringField('Login', [validators.DataRequired()])
    passkey = PasswordField('Passkey', [validators.DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        flag = False
        user_ip = request.remote_addr

        if user_ip in banned.keys():
            if banned[user_ip]['count'] >= 3 and datetime.datetime.today == banned[user_ip]['date']:
                return False

        if self.login.data != os.environ['login']:
            self.login.errors.append('Unknown username')
            if  user_ip not in banned.keys():
                banned[user_ip] = {'count': 1,'time': datetime.datetime.today()}
                flag = True
            else:
                banned[user_ip]['count'] += 1
                banned[user_ip]['time'] = datetime.datetime.today()
                flag = True
            return False

        if self.passkey.data != os.environ['passkey']:
            self.passkey.errors.append('Invalid password')
            if user_ip not in banned.keys() and flag == False:
                banned[user_ip] = {'count': 1, 'time': datetime.datetime.today()}
            elif flag == False:
                banned[user_ip]['count'] += 1
                banned[user_ip]['time'] = datetime.datetime.today()
            return False

        return True


@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')


def is_facebook_challenge_request(request):
    if request.args.get('hub.mode') != 'subscribe':
        return False
    if not request.args.get('hub.challenge'):
        return False
    return True


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.validate())
    if form.validate():
        flash('Successfully logged in')
        session['user_id'] = form.login.data
        return redirect(url_for('/'))
    return render_template('login.html', form=form)


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
            message_validators.is_schedule_command,
            message_handlers.handle_schedule_command
        ),
        (
            message_validators.is_talk_info_command,
            message_handlers.handle_talk_info_command
        ),
        (
            message_validators.is_talk_like_command,
            message_handlers.handle_talk_like_command
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
