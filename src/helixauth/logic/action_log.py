import cjson
from helixcore.mapping import insert
from helixbilling.domain.objects import ActionLog

def logged(func):
    def decorated(obj, data, curs):
        client_id = data.get('client_id')
        client_ids = [client_id] if client_id else []

        result = func(obj, data, curs)

        insert(curs, ActionLog(
            client_ids=client_ids,
            action=func.__name__,
            request=cjson.encode(data),
            response=cjson.encode(result)
        ))
        return result
    return decorated

def logged_bulk(func):
    def decorated(obj, data, curs):
        client_ids = []
        for lst in data.values():
            client_ids += [d['client_id'] for d in lst if 'client_id' in d]

        result = func(obj, data, curs)

        insert(curs, ActionLog(
            client_ids=client_ids,
            action=func.__name__,
            request=cjson.encode(data),
            response=cjson.encode(result)
        ))
        return result
    return decorated
