# coding=utf-8
"""
Structure of serialized message:
{lng:{EMAIL_SUBJ_FIELD_NAME: 'subj', EMAIL_MSG_FIELD_NAME: 'msg'},}

"""

LANG_EN = 'en'
LANG_RU = 'ru'

EMAIL_SUBJ_FIELD_NAME = 'email_subj'
EMAIL_MSG_FIELD_NAME = 'email_msg'

# Register user
REGISTER_USER = 'REGISTER_USER'
REGISTER_USER_EMAIL_SUBJ_EN = "Thanks for registration"
REGISTER_USER_EMAIL_MSG_EN = """Hi!

You are registered as user %(login)s at http://localhost:8000

Thank you for registration and have a nice day!
"""
REGISTER_USER_EMAIL_SUBJ_RU = "Благодарим за регистрацию"
REGISTER_USER_EMAIL_MSG_RU = """Добрый день!

Вы зарегистрировались на ресурсе http://localhost:8000 как пользователь %(login)s

Бдагодарим за регистрацию. Приятного пользования!
"""

# Restore password
#RESTORE_PASSWORD = 'RESTORE_PASSWORD'