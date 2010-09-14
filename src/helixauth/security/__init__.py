from hashlib import sha256


PASSWORD_FIELDS = ('password', 'new_password', 'su_password')


def _data_transfromer(d, fields, func):
    result = dict(d)
    for f in fields:
        if result.has_key(f):
            result[f] = func(result[f])
    return result


def sanitize_credentials(d):
    return _data_transfromer(d, PASSWORD_FIELDS, lambda x: '******')


def encrypt_passwords(d):
    return _data_transfromer(d, PASSWORD_FIELDS, encrypt_password)


def encrypt_password(password):
    h = sha256()
    h.update(password)
    return h.hexdigest()
