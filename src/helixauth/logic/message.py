# coding=utf-8
"""
Structure of serialized message:
{lng:{EMAIL_SUBJ_FIELD_NAME: 'subj', EMAIL_MSG_FIELD_NAME: 'msg'},}

"""

LANG_EN = 'en'
LANG_RU = 'ru'

LANG_FIELD_NAME = 'lang'
EMAIL_SUBJ_FIELD_NAME = 'email_subj'
EMAIL_MSG_FIELD_NAME = 'email_msg'

# Register user
EVENT_REGISTER_USER = 'REGISTER_USER'
REGISTER_USER_EMAIL_SUBJ_EN = "Thanks for registration"
REGISTER_USER_EMAIL_MSG_EN = """Good day!

You are registered as user %(email)s at http://localhost:8000/%(env_name)/

Thank you for registration and have a nice day!
"""
REGISTER_USER_EMAIL_SUBJ_RU = "Благодарим за регистрацию"
REGISTER_USER_EMAIL_MSG_RU = """Добрый день!

Вы зарегистрировались на ресурсе http://localhost:8000/%(env_name)/ как пользователь %(email)s

Бдагодарим за регистрацию!
"""

# Restore password
EVENT_RESTORE_PASSWORD = 'REGISTER_USER'
RESTORE_PASSWORD_EMAIL_SUBJ_EN = "Password restoration"
RESTORE_PASSWORD_EMAIL_MSG_EN = """Good day!

Password restoration requested at http://localhost:8000/%(env_name)/.
For changing password please follow http://localhost:8000/restore_password/%(env_name)/?session_id=%(session_id)
Link valid for changing password once and till %(valid_until).

Thank you for using our service and have a nice day!
"""
RESTORE_PASSWORD_EMAIL_SUBJ_RU = "Восстановление пароля"
RESTORE_PASSWORD_EMAIL_MSG_RU = """Добрый день!

На сайте http://localhost:8000/%(env_name)/ было инициирована восстановление пароля.
Для изменения пароля пожалуйста перейдите по ссылке http://localhost:8000/restore_password/%(env_name)/?session_id=%(session_id)
Ссылка можно использовать для одноразового изменения пароля до %(valid_until).

Спасибо за использование нашего сервиса!
"""


# Auto fetching event names and values
import sys
EVENTS_NAMES = filter(lambda x: x.startswith('EVENT_'), dir())
__cur_module = sys.modules[__name__]
EVENTS = [getattr(__cur_module, e_name) for e_name in EVENTS_NAMES]
