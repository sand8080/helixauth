from helixcore.json_validator import (Optional, AnyOf, NonNegative,
    Scheme, Text, NullableText, IsoDatetime)
from helixcore.server.api import ApiCall
from helixcore.server.protocol_primitives import (REQUEST_PAGING_PARAMS,
    RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR, RESPONSE_STATUS_ONLY,
    AUTHORIZED_RESPONSE_STATUS_OK, AUTHORIZED_RESPONSE_STATUS_ERROR,
    AUTHORIZED_REQUEST_AUTH_INFO,
    ADDING_OBJECT_RESPONSE,
    PING_REQUEST, PING_RESPONSE,
    LOGIN_REQUEST, LOGIN_RESPONSE,
    LOGOUT_REQUEST, LOGOUT_RESPONSE,
    CHECK_ACCESS_REQUEST, CHECK_ACCESS_RESPONSE)

from helixauth.db import dataobject


GET_API_ACTIONS_REQUEST = {}

GET_API_ACTIONS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'actions': [Text()],}
    ),
    RESPONSE_STATUS_ERROR
)

GET_API_SCHEME_REQUEST = AUTHORIZED_REQUEST_AUTH_INFO

GET_API_SCHEME_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'scheme': Text()}
    ),
    RESPONSE_STATUS_ERROR
)

ADD_ENVIRONMENT_REQUEST = {
    'name': Text(),
    'su_login': Text(),
    'su_password': Text(),
    Optional('custom_actor_info'): NullableText(),
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
            'name': Text(),
        }}
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_ENVIRONMENT_REQUEST = dict(
    {
        'new_name': Text(),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_ENVIRONMENT_RESPONSE = RESPONSE_STATUS_ONLY

RIGHTS_SCHEME = [{'service_id': int, 'properties': [Text()]}]

ADD_GROUP_REQUEST = dict(
    {
        'name': Text(),
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
        Optional('new_name'): Text(),
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
    'name': Text(),
    'is_active': bool,
    'rights': RIGHTS_SCHEME,
}

GET_GROUPS_REQUEST = dict(
    {
        'filter_params': {
            Optional('ids'): [int],
            Optional('name'): Text(),
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
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

ADD_USER_REQUEST = dict(
    {
        'login': Text(),
        'password': Text(),
        Optional('role'): AnyOf(dataobject.User.ROLE_USER),
        Optional('is_active'): bool,
        Optional('groups_ids'): [int],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_USER_RESPONSE = AnyOf(
    dict({'id': int,}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

MODIFY_USERS_REQUEST = dict(
    {
        'ids': [int],
        Optional('new_login'): Text(),
        Optional('new_password'): Text(),
        Optional('new_is_active'): bool,
        Optional('new_groups_ids'): [int],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_USERS_RESPONSE = RESPONSE_STATUS_ONLY

MODIFY_USER_SELF_REQUEST = dict(
    {
        'old_password': Text(),
        'new_password': Text(),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_USER_SELF_RESPONSE = RESPONSE_STATUS_ONLY

GET_USERS_REQUEST = dict(
    {
        'filter_params': {
            Optional('id'): int,
            Optional('ids'): [int],
            Optional('roles'): [AnyOf(dataobject.User.ROLE_SUPER, dataobject.User.ROLE_USER),],
            Optional('login'): Text(),
            Optional('groups_ids'): [int],
            Optional('is_active'): bool
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

USER_INFO = {
    'id': int,
    'login': Text(),
    'role': AnyOf(dataobject.User.ROLE_SUPER, dataobject.User.ROLE_USER),
    'is_active': bool,
    'groups_ids': [int],
}

GET_USERS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'users': [USER_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

ADD_SERVICE_REQUEST = dict(
    {
        'name': Text(),
        'type': Text(),
        'properties': [Text()],
        Optional('is_active'): bool,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_SERVICE_RESPONSE = ADDING_OBJECT_RESPONSE

SERVICE_INFO = {
    'id': int,
    'name': Text(),
    'type': Text(),
    'properties': [Text()],
    'is_active': bool,
    'is_possible_deactiate': bool,
}

GET_SERVICES_REQUEST = dict(
    {
        'filter_params': {
            Optional('ids'): [int],
            Optional('types'): [Text()],
            Optional('type'): Text(),
            Optional('is_active'): bool
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('id', '-id', 'name', '-name')]
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

GET_SERVICES_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'services': [SERVICE_INFO],
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

MODIFY_SERVICE_REQUEST = dict(
    {
        'id': int,
        Optional('new_name'): Text(),
        Optional('new_properties'): [Text()],
        Optional('new_is_active'): bool,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_SERVICE_RESPONSE = RESPONSE_STATUS_ONLY

ACTION_LOG_INFO = {
    'id': int,
    'session_id': NullableText(),
    'custom_actor_info': NullableText(),
    'actor_user_id': AnyOf(int, None),
    'subject_users_ids': [int],
    'action': Text(),
    'request_date': IsoDatetime(),
    'remote_addr': Text(),
    'request': Text(),
    'response': Text(),
}

GET_ACTION_LOGS_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): IsoDatetime(),
            Optional('to_request_date'): IsoDatetime(),
            Optional('action'): Text(),
            Optional('session_id'): Text(),
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
            'total': NonNegative(int),
        }
    ),
    RESPONSE_STATUS_ERROR
)

GET_ACTION_LOGS_SELF_REQUEST = dict(
    {
        'filter_params': {
            Optional('from_request_date'): IsoDatetime(),
            Optional('to_request_date'): IsoDatetime(),
            Optional('action'): Text(),
            Optional('session_id'): Text(),
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
            'rights': [{'service_id': int, 'service_type': Text(),
                'properties': [Text()]}],
        }
    ),
    RESPONSE_STATUS_ERROR
)

CHECK_USER_EXIST_REQUEST = dict(
    {
        'id': int,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

CHECK_USER_EXIST_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{
            'exist': bool,
        }
    ),
    RESPONSE_STATUS_ERROR
)


unauthorized_actions = ('ping', 'get_api_actions', 'add_environment',
    'get_authorized_api_actions')


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
]
