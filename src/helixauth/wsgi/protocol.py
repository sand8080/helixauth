from helixcore.json_validator import (Optional, AnyOf, NON_NEGATIVE_INT,
    Scheme, ISO_DATETIME, TEXT, NULLABLE_TEXT, ID, BOOLEAN, EMAIL)
from helixcore.server.api import ApiCall
from helixcore.server.protocol_primitives import (REQUEST_PAGING_PARAMS,
    RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR, RESPONSE_STATUS_ONLY,
    AUTHORIZED_RESPONSE_STATUS_OK, AUTHORIZED_RESPONSE_STATUS_ERROR,
    AUTHORIZED_REQUEST_AUTH_INFO,
    ADDING_OBJECT_RESPONSE,
    PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE,
    LOGOUT_REQUEST, LOGOUT_RESPONSE,
    CHECK_ACCESS_REQUEST, CHECK_ACCESS_RESPONSE,
    NOTIFICATION_PROCESSING,
    authorized_req, resp, RESPONSE_STATUS_WITH_NOTIFICATION)

from helixauth.db import dataobject
from helixauth.logic import message


GET_API_ACTIONS_REQUEST = {}

GET_API_ACTIONS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'actions': [TEXT],}
    ),
    RESPONSE_STATUS_ERROR
)

GET_API_SCHEME_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

GET_API_SCHEME_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'scheme': TEXT}
    ),
    RESPONSE_STATUS_ERROR
)

ADD_ENVIRONMENT_REQUEST = {
    'name': TEXT,
    'su_email': TEXT,
    'su_password': TEXT,
    Optional('custom_actor_info'): NULLABLE_TEXT,
}

ADD_ENVIRONMENT_RESPONSE = AnyOf(
    dict(
        {'environment_id': int, 'user_id': int},
        **AUTHORIZED_RESPONSE_STATUS_OK
    ),
    AUTHORIZED_RESPONSE_STATUS_ERROR
)

GET_ENVIRONMENT_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

GET_ENVIRONMENT_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'environment': {
            'id': int,
            'name': TEXT,
        }}
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_ENVIRONMENT_REQUEST = dict(
    {
        'new_name': TEXT,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_ENVIRONMENT_RESPONSE = RESPONSE_STATUS_ONLY

RIGHTS_SCHEME = [{'service_id': int, 'properties': [TEXT]}]

ADD_GROUP_REQUEST = dict(
    {
        'name': TEXT,
        Optional('is_active'): bool,
        'rights': RIGHTS_SCHEME,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_GROUP_RESPONSE = ADDING_OBJECT_RESPONSE

MODIFY_GROUP_REQUEST = dict(
    {
        'id': int,
        Optional('new_is_active'): bool,
        Optional('new_name'): TEXT,
        Optional('new_rights'): RIGHTS_SCHEME,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_GROUP_RESPONSE = RESPONSE_STATUS_ONLY

DELETE_GROUP_REQUEST = dict(
    {'id': int},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

DELETE_GROUP_RESPONSE = RESPONSE_STATUS_ONLY

GROUP_INFO = {
    'id': int,
    'name': TEXT,
    'is_active': bool,
    'rights': RIGHTS_SCHEME,
}

GET_GROUPS_REQUEST = dict(
    {
        'filter_params': {
            Optional('ids'): [int],
            Optional('name'): TEXT,
            Optional('is_active'): bool
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('name', '-name', 'id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_GROUPS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'groups': [GROUP_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

USER_LANG = AnyOf(*dataobject.User.LANGS)

ADD_USER_REQUEST = dict(
    {
        'email': EMAIL,
        'password': TEXT,
        Optional('role'): AnyOf(dataobject.User.ROLE_USER),
        Optional('is_active'): bool,
        Optional('groups_ids'): [int],
        Optional('lang'): USER_LANG,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_USER_RESPONSE = AnyOf(
    dict({'id': int, Optional('notification'): NOTIFICATION_PROCESSING}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

MODIFY_USERS_REQUEST = dict(
    {
        'ids': [ID],
        Optional('new_email'): TEXT,
        Optional('new_password'): TEXT,
        Optional('new_is_active'): BOOLEAN,
        Optional('new_groups_ids'): [ID],
        Optional('new_lang'): USER_LANG,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_USERS_RESPONSE = RESPONSE_STATUS_ONLY

MODIFY_USER_SELF_REQUEST = dict(
    {
        Optional('old_password'): TEXT,
        Optional('new_password'): TEXT,
        Optional('new_lang'): USER_LANG,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_USER_SELF_RESPONSE = RESPONSE_STATUS_ONLY

SET_PASSWORD_SELF_REQUEST = dict(
    {'new_password': TEXT,},
    **AUTHORIZED_REQUEST_AUTH_INFO
)

SET_PASSWORD_SELF_RESPONSE = RESPONSE_STATUS_WITH_NOTIFICATION

GET_USERS_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('roles'): [AnyOf(dataobject.User.ROLE_SUPER, dataobject.User.ROLE_USER),],
            Optional('email'): TEXT,
            Optional('groups_ids'): [int],
            Optional('is_active'): bool
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

USER_INFO = {
    'id': ID,
    'email': EMAIL,
    'role': AnyOf(dataobject.User.ROLE_SUPER, dataobject.User.ROLE_USER),
    'is_active': BOOLEAN,
    'groups_ids': [ID],
    'lang': USER_LANG,
}

GET_USERS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'users': [USER_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

ADD_SERVICE_REQUEST = authorized_req({
    'name': TEXT,
    'type': TEXT,
    'properties': [TEXT],
    Optional('is_active'): BOOLEAN,
})

ADD_SERVICE_RESPONSE = ADDING_OBJECT_RESPONSE

SERVICE_INFO = {
    'id': ID,
    'name': TEXT,
    'type': TEXT,
    'properties': [TEXT],
    'is_active': BOOLEAN,
    'is_possible_deactiate': BOOLEAN,
}

GET_SERVICES_REQUEST = authorized_req({
    'filter_params': {
        Optional('id'): ID,
        Optional('ids'): [ID],
        Optional('types'): [TEXT],
        Optional('type'): TEXT,
        Optional('is_active'): BOOLEAN
    },
    'paging_params': REQUEST_PAGING_PARAMS,
    Optional('ordering_params'): [AnyOf('id', '-id', 'name', '-name')]
})

GET_SERVICES_RESPONSE = resp({
    'services': [SERVICE_INFO],
    'total': NON_NEGATIVE_INT,
})

MODIFY_SERVICE_REQUEST = authorized_req({
    'id': ID,
    Optional('new_name'): TEXT,
    Optional('new_properties'): [TEXT],
    Optional('new_is_active'): BOOLEAN,
})

MODIFY_SERVICE_RESPONSE = RESPONSE_STATUS_ONLY

DELETE_SERVICE_REQUEST = authorized_req({'id': ID})

DELETE_SERVICE_RESPONSE = RESPONSE_STATUS_ONLY

ACTION_LOG_INFO = {
    'id': int,
    'session_id': NULLABLE_TEXT,
    'custom_actor_info': NULLABLE_TEXT,
    'actor_user_id': AnyOf(int, None),
    'subject_users_ids': [int],
    'action': TEXT,
    'request_date': ISO_DATETIME,
    'remote_addr': TEXT,
    'request': TEXT,
    'response': TEXT,
}

GET_ACTION_LOGS_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): ISO_DATETIME,
            Optional('to_request_date'): ISO_DATETIME,
            Optional('action'): TEXT,
            Optional('session_id'): TEXT,
            Optional('user_id'): int,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('request_date', '-request_date', 'id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'action_logs': [ACTION_LOG_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_ACTION_LOGS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): ISO_DATETIME,
            Optional('to_request_date'): ISO_DATETIME,
            Optional('action'): TEXT,
            Optional('session_id'): TEXT,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('request_date', '-request_date', 'id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_ACTION_LOGS_SELF_RESPONSE = GET_ACTION_LOGS_RESPONSE

GET_USER_RIGHTS_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

GET_USER_RIGHTS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'rights': [{'service_id': ID, 'service_type': TEXT,
                'properties': [TEXT]}],
        }
    ),
    RESPONSE_STATUS_ERROR
)

CHECK_USER_EXIST_REQUEST = dict(
    {
        'id': ID,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

CHECK_USER_EXIST_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'exist': BOOLEAN,
        }
    ),
    RESPONSE_STATUS_ERROR
)

NOTIFICATIONS_TYPES = AnyOf(dataobject.Notification.TYPE_EMAIL)

GET_NOTIFICATIONS_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): ID,
            Optional('ids'): [ID],
            Optional('type'): NOTIFICATIONS_TYPES,
            Optional('event'): TEXT,
            Optional('is_active'): BOOLEAN,
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

EMAIL_MESSAGE = {message.LANG_FIELD_NAME: USER_LANG,
    message.EMAIL_SUBJ_FIELD_NAME: TEXT,
    message.EMAIL_MSG_FIELD_NAME: TEXT}

NOTIFICATION_INFO = {
    'id': ID,
    'event': TEXT,
    'is_active': BOOLEAN,
    'type': NOTIFICATIONS_TYPES,
    'messages': [AnyOf(EMAIL_MESSAGE)],
}

GET_NOTIFICATIONS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'notifications': [NOTIFICATION_INFO],
            'total': NON_NEGATIVE_INT,
        }
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_NOTIFICATIONS_REQUEST = dict(
    {
        'ids': [ID],
        Optional('new_is_active'): BOOLEAN,
        Optional('new_messages'): [AnyOf(EMAIL_MESSAGE)],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_NOTIFICATIONS_RESPONSE = RESPONSE_STATUS_ONLY

RESET_NOTIFICATIONS_REQUEST = dict(
    {
        'ids': [ID],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

RESET_NOTIFICATIONS_RESPONSE = RESPONSE_STATUS_ONLY


unauthorized_actions = ('ping', 'get_api_actions', 'add_environment',
    'get_authorized_api_actions', 'login', 'logout')


protocol = [

    ApiCall('ping_request', Scheme(PING_REQUEST)),
    ApiCall('ping_response', Scheme(PING_RESPONSE)),

    # api actions
    ApiCall('get_api_actions_request', Scheme(GET_API_ACTIONS_REQUEST)),
    ApiCall('get_api_actions_response', Scheme(GET_API_ACTIONS_RESPONSE)),

    ApiCall('get_authorized_api_actions_request', Scheme(GET_API_ACTIONS_REQUEST)),
    ApiCall('get_authorized_api_actions_response', Scheme(GET_API_ACTIONS_RESPONSE)),

    ApiCall('get_api_scheme_request', Scheme(GET_API_SCHEME_REQUEST)),
    ApiCall('get_api_scheme_response', Scheme(GET_API_SCHEME_RESPONSE)),

    # login user
    ApiCall('login_request', Scheme(LOGIN_REQUEST)),
    ApiCall('login_response', Scheme(LOGIN_RESPONSE)),

    # logout user
    ApiCall('logout_request', Scheme(LOGOUT_REQUEST)),
    ApiCall('logout_response', Scheme(LOGOUT_RESPONSE)),

    # environment
    ApiCall('add_environment_request', Scheme(ADD_ENVIRONMENT_REQUEST)),
    ApiCall('add_environment_response', Scheme(ADD_ENVIRONMENT_RESPONSE)),

    ApiCall('get_environment_request', Scheme(GET_ENVIRONMENT_REQUEST)),
    ApiCall('get_environment_response', Scheme(GET_ENVIRONMENT_RESPONSE)),

    ApiCall('modify_environment_request', Scheme(MODIFY_ENVIRONMENT_REQUEST)),
    ApiCall('modify_environment_response', Scheme(MODIFY_ENVIRONMENT_RESPONSE)),

    # service
    ApiCall('add_service_request', Scheme(ADD_SERVICE_REQUEST)),
    ApiCall('add_service_response', Scheme(ADD_SERVICE_RESPONSE)),

    ApiCall('modify_service_request', Scheme(MODIFY_SERVICE_REQUEST)),
    ApiCall('modify_service_response', Scheme(MODIFY_SERVICE_RESPONSE)),

    ApiCall('delete_service_request', Scheme(DELETE_SERVICE_REQUEST)),
    ApiCall('delete_service_response', Scheme(DELETE_SERVICE_RESPONSE)),

    ApiCall('get_services_request', Scheme(GET_SERVICES_REQUEST)),
    ApiCall('get_services_response', Scheme(GET_SERVICES_RESPONSE)),

    # group
    ApiCall('add_group_request', Scheme(ADD_GROUP_REQUEST)),
    ApiCall('add_group_response', Scheme(ADD_GROUP_RESPONSE)),

    ApiCall('modify_group_request', Scheme(MODIFY_GROUP_REQUEST)),
    ApiCall('modify_group_response', Scheme(MODIFY_GROUP_RESPONSE)),

    ApiCall('delete_group_request', Scheme(DELETE_GROUP_REQUEST)),
    ApiCall('delete_group_response', Scheme(DELETE_GROUP_RESPONSE)),

    ApiCall('get_groups_request', Scheme(GET_GROUPS_REQUEST)),
    ApiCall('get_groups_response', Scheme(GET_GROUPS_RESPONSE)),

    # user
    ApiCall('add_user_request', Scheme(ADD_USER_REQUEST)),
    ApiCall('add_user_response', Scheme(ADD_USER_RESPONSE)),

    ApiCall('get_users_request', Scheme(GET_USERS_REQUEST)),
    ApiCall('get_users_response', Scheme(GET_USERS_RESPONSE)),

    ApiCall('get_user_rights_request', Scheme(GET_USER_RIGHTS_REQUEST)),
    ApiCall('get_user_rights_response', Scheme(GET_USER_RIGHTS_RESPONSE)),

    ApiCall('modify_users_request', Scheme(MODIFY_USERS_REQUEST)),
    ApiCall('modify_users_response', Scheme(MODIFY_USERS_RESPONSE)),

    ApiCall('modify_user_self_request', Scheme(MODIFY_USER_SELF_REQUEST)),
    ApiCall('modify_user_self_response', Scheme(MODIFY_USER_SELF_RESPONSE)),

    ApiCall('set_password_self_request', Scheme(SET_PASSWORD_SELF_REQUEST)),
    ApiCall('set_password_self_response', Scheme(SET_PASSWORD_SELF_RESPONSE)),

    # action log
    ApiCall('get_action_logs_request', Scheme(GET_ACTION_LOGS_REQUEST)),
    ApiCall('get_action_logs_response', Scheme(GET_ACTION_LOGS_RESPONSE)),

    ApiCall('get_action_logs_self_request', Scheme(GET_ACTION_LOGS_SELF_REQUEST)),
    ApiCall('get_action_logs_self_response', Scheme(GET_ACTION_LOGS_SELF_RESPONSE)),

    # check access
    ApiCall('check_access_request', Scheme(CHECK_ACCESS_REQUEST)),
    ApiCall('check_access_response', Scheme(CHECK_ACCESS_RESPONSE)),

    # check user
    ApiCall('check_user_exist_request', Scheme(CHECK_USER_EXIST_REQUEST)),
    ApiCall('check_user_exist_response', Scheme(CHECK_USER_EXIST_RESPONSE)),

    # notifications
    ApiCall('get_notifications_request', Scheme(GET_NOTIFICATIONS_REQUEST)),
    ApiCall('get_notifications_response', Scheme(GET_NOTIFICATIONS_RESPONSE)),

    ApiCall('modify_notifications_request', Scheme(MODIFY_NOTIFICATIONS_REQUEST)),
    ApiCall('modify_notifications_response', Scheme(MODIFY_NOTIFICATIONS_RESPONSE)),

    ApiCall('reset_notifications_request', Scheme(RESET_NOTIFICATIONS_REQUEST)),
    ApiCall('reset_notifications_response', Scheme(RESET_NOTIFICATIONS_RESPONSE)),
]
