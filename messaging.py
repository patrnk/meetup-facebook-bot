import json

import requests


def send_main_menu(access_token, user_id):
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


def form_talk_subtitle(talk):
    speaker = talk.get('speaker', '')
    description = talk.get('description', '')
    return '%s: %s' % (speaker, description)


def send_schedule(access_token, user_id, talks):
    elements = []
    for talk in talks:
        element = {
                'title': talk['title'],
                'image_url': talk.get('image_url'),
                'subtitle': form_talk_subtitle(talk),
                'buttons': [
                    {
                        'type': 'postback',
                        'title': 'Описание доклада',
                        'payload': 'info talk %d' % talk['id']
                    },
                    {
                        'type': 'postback',
                        'title': 'Лайк',
                        'payload': 'like talk %d' % talk['id']
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


def send_more_talk_info(access_token, user_id, payload, talks):
    talk_id = int(payload.split(' ')[-1]) - 1
    title = talks[talk_id]['title']
    speaker = talks[talk_id]['speaker']
    description = talks[talk_id].get('description', 'Нет описания.')
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


def send_like_confirmation(access_token, user_id, payload, talks):
    talk_id = int(payload.split(' ')[-1]) - 1
    title = talks[talk_id]['title']
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
