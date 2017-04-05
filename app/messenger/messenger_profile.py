import os
import sys
import json
import argparse

import requests


ALLOWED_FIELDS = ['get_started', 'greeting']


def send_messenger_profile_request(access_token, request_type, params=None, data=None):
    allowed_request_types = ['GET', 'POST', 'DELETE']
    if request_type not in allowed_request_types:
        raise ValueError('This request_type is not allowed: %s' % request_type)
    headers = {
            'Content-Type': 'application/json'
            }
    params = params or {}
    params['access_token'] = access_token
    url = 'https://graph.facebook.com/v2.6/me/messenger_profile'
    response = requests.request(request_type, url=url, headers=headers,
                                params=params, data=json.dumps(data))
    response.raise_for_status()
    return response.json()


def set_get_started_button(access_token, payload):
    get_started_button = {
            'get_started': {
                'payload': payload,
                },
            }
    response = send_messenger_profile_request(access_token, 'POST', data=get_started_button)
    return response


def set_greeting(access_token, greeting_text):
    greeting = {
            'greeting': [
                {
                'locale': 'default',
                'text': greeting_text,
                }
            ]
    }
    response = send_messenger_profile_request(access_token, 'POST', data=greeting)
    return response


def get_field(access_token, field):
    if field not in ALLOWED_FIELDS:
        raise ValueError('This field is not allowed: %s' % field)
    params = {'fields': field}
    response = send_messenger_profile_request(access_token, 'GET', params=params)
    return response


def delete_field(access_token, field):
    if field not in ALLOWED_FIELDS:
        raise ValueError('This field is not allowed: %s' % field)
    payload = {'fields': [field]}
    response = send_messenger_profile_request(access_token, 'DELETE', data=payload)
    return response
    

def get_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('field', type=str,
                        help='Either "get_started or greeting".')
    parser.add_argument('-g', '--get', action='store_true',
                        help='Ask facebook the current value of the field.')
    parser.add_argument('-s', '--set', type=str,
                        help='Set new value of the field to facebook')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='Ask facebook to delete the current value of the field.')
    return parser.parse_args()
                        

if __name__ == '__main__':
    args = get_cli_args()
    access_token = os.environ['ACCESS_TOKEN']
    
    if args.field not in ALLOWED_FIELDS:
        sys.exit('Unknown field parameter\n')

    if args.get:
        print('Get:')
        print(get_field(access_token, args.field))
    elif args.delete:
        print('Delete:')
        print(delete_field(access_token, args.field))
    elif args.set:
        print('Set:')
        if args.field == 'get_started':
            print(set_get_started_button(access_token, args.set))
        elif args.field == 'greeting':
            print(set_greeting(access_token, args.set))
        else:
            raise NotImplemented()
    else:
        print('Get:')
        print(get_field(access_token, args.field))
