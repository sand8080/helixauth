from helixauth.logic import message as m


class Notifier(object):
    def _default_notif_struct(self, event):
        res = {}
        for l in (m.LANG_EN, m.LANG_RU):
            subj = '%s_EMAIL_SUBJ_%s' % (event, l.upper())
            msg = '%s_EMAIL_MSG_%s' % (event, l.upper())
            print "###", subj, msg
            res[l] = {m.EMAIL_SUBJ_FIELD_NAME: getattr(m, subj, None),
                m.EMAIL_MSG_FIELD_NAME: getattr(m, msg, None)}
        return res

    def default_register_user_notif(self, environment_id):
        return self._default_notif_struct(m.REGISTER_USER)
