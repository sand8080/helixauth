from psycopg2 import IntegrityError

from helixcore.server.exceptions import UnknownActionError, DataIntegrityError
from helixbilling.logic.handler import Handler

def handle_action(action_name, data):
    '''
    Handles API action.
    @param action_name: name of API action
    @param data: dict with supplied data
    @return: response dict
    @raise UnknownActionError: if action with such name is unknown to handler
    @raise DataIntegrityError: if given data is semantically not correct (ie. database raises IntegrityError)
    '''
    try:
        method = getattr(Handler(), action_name)
    except AttributeError, e:
        raise UnknownActionError('Cannot handle action %s: unknown action' % action_name)

    try:
        return method(data)
    except IntegrityError, e:
        raise DataIntegrityError('Cannot handle action %s: %s' % (action_name, e.message))
