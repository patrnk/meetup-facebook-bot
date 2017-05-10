from flask import session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm

class TalkView(ModelView):
    list_columns = ['id', 'speaker_facebook_id', 'speaker', 'title', 'description', 'likes']
    form_base_class = SecureForm

    def is_accessible(self):
        if not session.get('logged'):
            return False
        else:
            return True
