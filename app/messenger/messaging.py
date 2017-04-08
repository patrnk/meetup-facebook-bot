import json

import requests

from app import models


def send_main_menu(access_token, user_id):
    ''' Makes use of Quick Replies: 
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/quick-replies
    '''
    main_menu_message_body = {
            'text': 'Чем могу помочь?',
            'quick_replies': [
                {
                    'content_type': 'text',
                    'title': 'Все доклады',
                    'payload': 'schedule payload'
                },
                {
                    'content_type': 'text',
                    'title': 'Вопрос докладчику',
                    'payload': 'question payload'
                },
                {
                    'content_type': 'text',
                    'title': 'Чат',
                    'payload': 'chat payload'
                }
                ]
            }


    main_menu = {
            'recipient': {
                'id': user_id,
                },
            'message': main_menu_message_body,
            }
    return send_message_to_facebook(access_token, main_menu)


def send_schedule(access_token, user_id):
    ''' Makes use of Generic Template: 
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
    '''
    elements = []
    talks = models.Talk.query.all()
    for talk in talks:
        element = {
                'title': talk.title,
                'subtitle': '%s: %s' % (talk.speaker.name, talk.description or ''),
                'buttons': [
                    {
                        'type': 'postback',
                        'title': 'Описание доклада',
                        'payload': 'info talk %d' % talk.id
                    },
                    {
                        'type': 'postback',
                        'title': 'Лайк',
                        'payload': 'like talk %d' % talk.id
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

    schedule = {
            'recipient': {
                'id': user_id
                },
            'message': schedule_message_body
            }
    send_message_to_facebook(access_token, schedule)


def send_more_talk_info(access_token, user_id, payload):
    ''' Send a simple Facebook message:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    '''
    talk_id = int(payload.split(' ')[-1])
    talk = models.Talk.query.get(talk_id)
    title = talk.title
    speaker = talk.speaker.name
    description = talk.description or 'Нет описания.'
    more_info_text = '"%s"\n\n%s:\n%s' % (title, speaker, description)
    more_info = {
            'recipient': {
                'id': user_id
                },
            'message': {
                'text': more_info_text
                }
            }
    return send_message_to_facebook(access_token, more_info)


def send_like_confirmation(access_token, user_id, payload):
    ''' Send a simple Facebook message:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference/text-message
    '''
    talk_id = int(payload.split(' ')[-1])
    talk = models.Talk.query.get(talk_id)
    title = talk.title
    confirmation_text = 'Вы поставили лайк докладу "%s".' % title
    confirmation = {
            'recipient': {
                'id': user_id
                },
            'message': {
                'text': confirmation_text
                }
            }
    return send_message_to_facebook(access_token, confirmation)


def send_message_to_facebook(access_token, message_data):
    headers = {
            'Content-Type': 'application/json',
            }
    params = {
            'access_token': access_token,
            }
    url = 'https://graph.facebook.com/v2.6/me/messages'
    response = requests.post(url, headers=headers, params=params,
                             data=json.dumps(message_data))
    response.raise_for_status()
    return response.json()
