# -*- coding: utf-8 -*-

import json

import requests


def send_rate_menu(access_token, user_id, talk, db_session):
    """ Makes use of Quick Replies:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/quick-replies
    """
    if talk.is_liked_by(user_id, db_session):
        rate_button_title = 'Убрать лайк'
    else:
        rate_button_title = 'Поставить лайк'
    talk_title = talk.title
    rate_menu_message_body = {
        'text': 'Как оценишь доклад? \n %s' % talk_title,
        'quick_replies': [
            {
                'content_type': 'text',
                'title': rate_button_title,
                'payload': 'like talk %d' % talk.id
            },
            {
                'content_type': 'text',
                'title': 'Отменить',
                'payload': 'cancel payload'
            }
        ]
    }
    return send_message_to_facebook(access_token, user_id, rate_menu_message_body)


def send_like_confirmation(access_token, user_id, talk, db_session):
    talk_title = talk.title
    if talk.is_liked_by(user_id, db_session):
        like_text_message = 'Поставил лайк докладу:\n %s' % talk_title
    else:
        like_text_message = 'Убрал лайк c доклада:\n %s' % talk_title
    like_message_body = {
        "text": like_text_message
    }
    return send_message_to_facebook(access_token, user_id, like_message_body)


def send_schedule(access_token, user_id, talks, db_session):
    """ Makes use of Generic Template:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
    """
    elements = []
    for talk in talks:
        number_of_likes = talk.count_likes(db_session)
        if talk.is_liked_by(user_id, db_session):
            like_text = 'Вы лайкнули этот доклад'
        else:
            like_text = 'Вы не оценили этот докад'
        element_subtitle = '%s\nЛайков: %d\nСпикер: %s' % (like_text, number_of_likes, talk.speaker.name)
        element = {
            'title': talk.title,
            'subtitle': element_subtitle,
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Получить подробности',
                    'payload': 'info talk %d' % talk.id
                },
                {
                    'type': 'postback',
                    'title': 'Оценить',
                    'payload': 'rate talk %d' % talk.id
                },
                {
                    'type': 'postback',
                    'title': 'Задать вопрос',
                    'payload': 'ask talk %d' % talk.id
                }
            ]
        }
        elements.append(element)

    schedule_message_body = {
        'attachment': {
            'type': 'template',
            'payload': {
                'template_type': 'generic',
                'elements': elements
            }
        }
    }
    return send_message_to_facebook(access_token, user_id, schedule_message_body)


def send_talk_info(access_token, user_id, talk):
    """ Send a simple Facebook message:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    """
    title = talk.title
    speaker = talk.speaker.name
    description = talk.description or 'Нет описания.'
    more_info_text = '"%s"\n\n%s:\n%s' % (title, speaker, description)
    more_info = {
        'text': more_info_text
    }
    return send_message_to_facebook(access_token, user_id, more_info)


def send_duplicate_authentication_error(access_token, user_id):
    """ Send a simple Facebook message:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    """
    error_message_body = {
        'text': 'Докладчик уже авторизован, повторно не получится.'
    }
    return send_message_to_facebook(access_token, user_id, error_message_body)


def send_authentication_confirmation(access_token, user_id, speaker_name):
    """ Send a simple Facebook message:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    """
    confirmation_message_body = {
        'text': 'Вы зарегистрировались как докладчик %s.' % speaker_name
    }
    return send_message_to_facebook(access_token, user_id, confirmation_message_body)


def send_message_to_facebook(access_token, user_id, message_data):
    headers = {
        'Content-Type': 'application/json',
    }
    params = {
        'access_token': access_token,
    }
    payload = {
        'recipient': {
            'id': user_id,
        },
        'message': message_data,
    }
    url = 'https://graph.facebook.com/v2.6/me/messages'
    response = requests.post(url, headers=headers, params=params,
                             data=json.dumps(payload))
    response.raise_for_status()
    return response.json()
