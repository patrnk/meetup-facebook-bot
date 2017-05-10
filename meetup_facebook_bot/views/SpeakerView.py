from flask import session
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm

class SpeakerView(ModelView):
    list_columns = ['facebook_id', 'name']
    form_base_class = SecureForm

    def is_accessible(self):
        if not session.get('logged'):
            return False
        else:
            return True
