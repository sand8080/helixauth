from email.mime.text import MIMEText
import smtplib

from helixauth.conf import settings
from helixauth.conf.log import logger
from helixauth.db.filters import NotificatonFilter, EnvironmentFilter
from helixauth.db.dataobject import Notification
from helixauth.error import NotificatoinPreparingError, HelixauthError,\
    NotificatonNotFound
from helixauth.logic import message as m


class NotificationProcessing(object):
    STEP_UNEXPECTED_ERROR = 'STEP_UNEXPECTED_ERROR'

    STEP_NOTIFICATIONS_DISABLED = 'STEP_NOTIFICATIONS_DISABLED'
    STEP_NOTIFICATIONS_ENABLED = 'STEP_NOTIFICATIONS_ENABLED'

    STEP_UNKNOWN_EVENT = 'STEP_UNKNOWN_EVENT'

    STEP_EVENT_NOTIFICATION_DISABLED = 'STEP_EVENT_NOTIFICATION_DISABLED'
    STEP_EVENT_NOTIFICATION_ENABLED = 'STEP_EVENT_NOTIFICATION_ENABLED'

    STEP_MSG_LANG_FOUND = 'STEP_MSG_LANG_FOUND'
    STEP_MSG_LANG_NOT_FOUND = 'STEP_MSG_LANG_NOT_FOUND'

    STEP_MSG_DFLT_LANG_FOUND = 'STEP_MSG_DFLT_LANG_FOUND'
    STEP_MSG_DFLT_LANG_NOT_FOUND = 'STEP_MSG_DFLT_LANG_NOT_FOUND'

    STEP_NOTIFICATION_SENT = 'STEP_NOTIFICATION_SENT'
    STEP_NOTIFICATION_SENDING_ERROR = 'STEP_NOTIFICATION_SENDING_ERROR'

    def __init__(self):
        self.is_processable = False
        self.is_sent = False
        self.checking_steps = []
        self.message_data = {}

    def add_step(self, step):
        self.checking_steps.append(step)

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

    def _send_email(self, to, n_p, tpl_data):
        if n_p.is_processable:
            try:
                msg_d = n_p.message_data
                msg_text = msg_d[m.EMAIL_MSG_FIELD_NAME] % tpl_data
                msg = MIMEText(msg_text, _charset='utf8')
                msg['Subject'] = msg_d[m.EMAIL_SUBJ_FIELD_NAME]
                msg['From'] = settings.email_notifications_sender
                msg['To'] = to
                s = smtplib.SMTP(settings.email_server)
                s.sendmail(settings.email_notifications_sender, [to],
                    msg.as_string())
                s.quit()
                n_p.add_step(n_p.STEP_NOTIFICATION_SENT)
                n_p.is_sent = True
            except Exception, e:
                n_p.add_step(n_p.STEP_NOTIFICATION_SENDING_ERROR)
                logger.exception("Sending email failed: %s", e)

    def get_env_name(self, curs, env_id):
        f = EnvironmentFilter({'id': env_id}, {}, None)
        env = f.filter_one_obj(curs)
        return env.name

    def register_user(self, curs, user, session):
        env_id = session.environment_id
        env_name = self.get_env_name(curs, env_id)
        n_p = self._get_message_data(env_id, m.EVENT_REGISTER_USER,
            Notification.TYPE_EMAIL, user.lang, curs)
        tpl_data = {'email': user.email, 'env_name': env_name}
        self._send_email(user.email, n_p, tpl_data)
        return n_p.to_dict()

    def _check_emailing_enabled(self, n_p):
        if not settings.email_notifications_enabled:
            n_p.add_step(n_p.STEP_NOTIFICATIONS_DISABLED)
            raise NotificatoinPreparingError()
        else:
            n_p.add_step(n_p.STEP_NOTIFICATIONS_ENABLED)

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

    def _extract_message(self, n_p, notif, lang):
        msgs = notif.deserialized('serialized_messages')
        msgs_lang_idx = {}
        for msg_d in msgs:
            msgs_lang_idx[msg_d['lang']] = msg_d
        if lang in msgs_lang_idx:
            n_p.add_step(n_p.STEP_MSG_LANG_FOUND)
            return msgs_lang_idx[lang]
        else:
            n_p.add_step(n_p.STEP_MSG_LANG_NOT_FOUND)
            dflt_lang = settings.default_notifications_lang
            if dflt_lang not in msgs_lang_idx:
                n_p.add_step(n_p.STEP_MSG_DFLT_LANG_NOT_FOUND)
                raise NotificatoinPreparingError()
            else:
                n_p.add_step(n_p.STEP_MSG_DFLT_LANG_FOUND)
                return msgs_lang_idx[dflt_lang]

    def _get_message_data(self, env_id, event_name, notif_type, lang, curs):
        """
        returns (message_data_dict, NotificationProcessing)
        """
        n_p = NotificationProcessing()
        try:
            self._check_emailing_enabled(n_p)
            notif = self._get_notification(n_p, env_id, event_name, curs)
            n_p.message_data = self._extract_message(n_p, notif, lang)
            n_p.is_processable = True
        except HelixauthError:
            pass
        except Exception, e:
            n_p.add_step(n_p.STEP_UNEXPECTED_ERROR)
            logger.exception("Notification processing error: %s", e)
        finally:
            return n_p
