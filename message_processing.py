def extract_all_messaging_events(entries):
    messaging_events = []
    for entry in entries:
        for messaging_event in entry['messaging']:
            messaging_events.append(messaging_event)
    return messaging_events


def is_quick_button_pressed(messaging_event):
    if 'message' not in messaging_event:
        return False;
    if 'quick_reply' not in messaging_event['message']:
        return False;
    return True;


def is_schedule_button_pressed(messaging_event):
    if not is_quick_button_pressed(messaging_event):
        return False
    return messaging_event['message']['quick_reply']['payload'] == 'schedule payload'


def is_more_talk_info_button_pressed(messaging_event):
    if 'postback' not in messaging_event:
        return False
    return 'info talk' in messaging_event['postback']['payload']


def is_like_talk_button_pressed(messaging_event):
    if 'postback' not in messaging_event:
        return False
    return 'like talk' in messaging_event['postback']['payload']
