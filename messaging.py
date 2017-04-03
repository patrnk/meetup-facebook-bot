import json

import requests


def send_main_menu(access_token, user_id):
    main_menu_message_body = {
            'text': 'Чем могу помочь?',
            'quick_replies': [
                {
                    'content_type': 'text',
                    'title': 'Расписание',
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


def send_schedule(access_token, user_id, talks):
    elements = []
    for talk in talks:
        element = {
                'title': talk['title'],
                'image_url': talk.get('image_url'),
                'subtitle': talk.get('speaker'),
                'buttons': [
                    {
                        'type': 'postback',
                        'title': 'Лайк',
                        'payload': 'talk #%d' % talk['id']
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
