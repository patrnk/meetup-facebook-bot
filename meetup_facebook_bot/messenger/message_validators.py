def is_quick_button(messaging_event):
    if 'message' not in messaging_event:
        return False
    if 'quick_reply' not in messaging_event['message']:
        return False
    return True


def is_schedule_command(messaging_event):
    if not is_quick_button(messaging_event):
        return False
    return messaging_event['message']['quick_reply']['payload'] == 'schedule payload'


def is_talk_info_command(messaging_event):
    if 'postback' not in messaging_event:
        return False
    return 'info talk' in messaging_event['postback']['payload']


def is_talk_like_command(messaging_event):
    if 'postback' not in messaging_event:
        return False
    return 'like talk' in messaging_event['postback']['payload']


def has_sender_id(messaging_event):
    return 'sender' in messaging_event and 'id' in messaging_event['sender']
