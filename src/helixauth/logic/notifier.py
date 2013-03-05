from helixauth.logic import message as m
from helixauth.db.filters import NotificatonFilter
from helixauth.conf import settings
from helixauth.db.dataobject import Notification
from helixauth.error import NotificatoinPreparingError, HelixauthError,\
    NotificatonNotFound
from helixauth.conf.log import logger


class NotificationProcessing(object):
    STEP_UNEXPECTED_ERROR = 'STEP_UNEXPECTED_ERROR'

    STEP_NOTIFECATIONS_DISABLED = 'STEP_NOTIFECATIONS_DISABLED'
    STEP_NOTIFECATIONS_ENABLED = 'STEP_NOTIFECATIONS_ENABLED'

    STEP_UNKNOWN_EVENT = 'STEP_UNKNOWN_EVENT'

    STEP_EVENT_NOTIFICATION_DISABLED = 'STEP_EVENT_NOTIFICATION_DISABLED'
    STEP_EVENT_NOTIFICATION_ENABLED = 'STEP_EVENT_NOTIFICATION_ENABLED'

    def __init__(self):
        self.is_sent = False
        self.processing_steps = []
        self.message_data = {}

    def add_step(self, step):
        self.processing_steps.append(step)

    def to_dict(self):
        return dict(self.__dict__)


class Notifier(object):
    def default_email_notif_struct(self, event):
        res = []
        for l in (m.LANG_EN, m.LANG_RU):
            subj = '%s_EMAIL_SUBJ_%s' % (event, l.upper())
            msg = '%s_EMAIL_MSG_%s' % (event, l.upper())
            res.append({m.LANG_FIELD_NAME: l,
                m.EMAIL_SUBJ_FIELD_NAME: getattr(m, subj, None),
                m.EMAIL_MSG_FIELD_NAME: getattr(m, msg, None),})
        return res

    def default_register_user_notif(self, environment_id):
        return self.default_email_notif_struct(m.EVENT_REGISTER_USER)

    def register_user(self, user, session):
        n_p = NotificationProcessing()
        n_p.add_step('NOT_IMPLEMENTED')
        return n_p.to_dict()

    def _check_emailing_enabled(self, n_p):
        if not settings.email_notifications_enabled:
            n_p.add_step(n_p.STEP_NOTIFECATIONS_DISABLED)
            raise NotificatoinPreparingError()
        else:
            n_p.add_step(n_p.STEP_NOTIFECATIONS_ENABLED)

    def _get_notification(self, n_p, env_id, event_name, curs):
        n_f = NotificatonFilter(env_id, {'event': event_name,
            'type': Notification.TYPE_EMAIL}, {}, None)
        try:
            notif = n_f.filter_one_obj(curs)
            if notif.is_active:
                n_p.add_step(n_p.STEP_EVENT_NOTIFICATION_ENABLED)
            else:
                n_p.add_step(n_p.STEP_EVENT_NOTIFICATION_DISABLED)
                raise NotificatoinPreparingError()
            return notif
        except NotificatonNotFound:
            n_p.add_step(n_p.STEP_UNKNOWN_EVENT)
        raise NotificatoinPreparingError()

    def _prepare_notif(self, env_id, event_name, notif_type, lang, curs):
        n_p = NotificationProcessing()
        try:
            self._check_emailing_enabled(n_p)
            notif = self._get_notification(n_p, env_id, event_name, curs)
        except HelixauthError:
            pass
        except Exception, e:
            n_p.add_step(n_p.STEP_UNEXPECTED_ERROR)
            logger.exception("Notification processing error: %s", e)
        finally:
            return n_p


