from helixauth.conf import settings


class Notifier(object):
    def register_user(self, login, lang=settings.default_messages_lang):
        n = None # Notification
