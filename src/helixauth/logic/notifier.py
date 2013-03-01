from helixauth.logic import message as m


class NotificationProcessing(object):
    def __init__(self):
        self.is_sent = False
        self.processing_steps = []

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

    def register_user(self):
        n_p = NotificationProcessing()
        n_p.add_step('NOT_IMPLEMENTED')
        return n_p.to_dict()