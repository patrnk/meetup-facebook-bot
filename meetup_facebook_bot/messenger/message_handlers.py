from meetup_facebook_bot.models.talk import Talk
from meetup_facebook_bot.models.speaker import Speaker
from meetup_facebook_bot.messenger import messaging
from meetup_facebook_bot.messenger.message_validators import is_talk_rate_command


def handle_talk_info_command(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    payload = messaging_event['postback']['payload']
    talk_id = int(payload.split(' ')[-1])
    talk = db_session.query(Talk).get(talk_id)
    if not talk:
        return
    return messaging.send_talk_info(access_token, sender_id, talk)


def handle_talk_rate_command(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    payload = messaging_event['postback']['payload']
    talk_id = int(payload.split(' ')[-1])
    talk = db_session.query(Talk).get(talk_id)
    return messaging.send_rate_menu(access_token, sender_id, talk, db_session)


def handle_talk_like_command(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    payload = messaging_event['message']['quick_reply']['payload']
    talk_id = int(payload.split(' ')[-1])
    talk = db_session.query(Talk).get(talk_id)
    talk.revert_like(sender_id, db_session)
    return messaging.send_like_confirmation(access_token, sender_id, talk, db_session)


def handle_message_with_sender_id(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    talks = db_session.query(Talk).all()
    if is_talk_rate_command(messaging_event):
        return
    return messaging.send_schedule(access_token, sender_id, talks, db_session)


def handle_speaker_auth(messaging_event, access_token, db_session):
    sender_id = messaging_event['sender']['id']
    message_text = messaging_event['message']['text']
    speaker = db_session.query(Speaker).filter_by(token=message_text).scalar()
    if not speaker:
        return
    if speaker.page_scoped_id is not None:
        return messaging.send_duplicate_authentication_error(access_token, sender_id)
    speaker.page_scoped_id = sender_id
    db_session.commit()
    return messaging.send_authentication_confirmation(access_token, sender_id, speaker.name)
