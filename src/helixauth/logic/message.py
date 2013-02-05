from helixauth.conf.db import transaction
from helixauth.db.dataobject import Notification


class MessageComposer(object):
#    LANGS = (Notification.LANG_EN, Notification.LANG_RU)
#    DEFAULT_LANG = LANGS[0]

    def _compose_message(self, tpl, params):
        tpl % params

    def reset_password(self, lang='en'):
        pass

    def _add_reset_password(self, curs):
        n_ru = Notification

    @transaction()
    def create_messages_in_db(self, curs=None):
        self._add_reset_password()
