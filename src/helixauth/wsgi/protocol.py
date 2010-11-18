from helixcore.server.api import ApiCall
from helixcore.json_validator import (Optional, AnyOf, NonNegative,
    Scheme, Text, ArbitraryDict, NullableText)

from helixauth.db import dataobject


REQUEST_PAGING_PARAMS = {
    Optional('limit'): NonNegative(int),
    Optional('offset'): NonNegative(int),
}

AUTHORIZED_REQUEST_AUTH_INFO = {
    Optional('session_id'): Text(),
    Optional('custom_actor_info'): NullableText(),
}

RESPONSE_STATUS_OK = {'status': 'ok'}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'code': Text(),
    'category': Text(),
    'message': Text(),
    'details': [ArbitraryDict()],
}

AUTHORIZED_RESPONSE_STATUS_OK = dict(
    RESPONSE_STATUS_OK,
    **{'session_id': Text()}
)

AUTHORIZED_RESPONSE_STATUS_ERROR = dict(
    RESPONSE_STATUS_ERROR,
    **{'session_id': Text()}
)

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

AUTHORIZED_RESPONSE_STATUS_ONLY = AnyOf(
    AUTHORIZED_RESPONSE_STATUS_OK,
    AUTHORIZED_RESPONSE_STATUS_ERROR
)

PING_REQUEST = {}

PING_RESPONSE = RESPONSE_STATUS_ONLY

GET_API_ACTIONS_REQUEST = {}

GET_API_ACTIONS_RESPONSE = AnyOf(
    dict(
        RESPONSE_STATUS_OK,
        **{'actions': [Text()],}
    ),
    RESPONSE_STATUS_ERROR
)

LOGIN_REQUEST = {
    'login': Text(),
    'password': Text(),
    'environment_name': Text(),
    Optional('custom_actor_info'): NullableText(),
}

LOGIN_RESPONSE = AUTHORIZED_RESPONSE_STATUS_ONLY

ADD_ENVIRONMENT_REQUEST = {
    'name': Text(),
    'su_login': Text(),
    'su_password': Text(),
    Optional('custom_actor_info'): NullableText(),
}

ADD_ENVIRONMENT_RESPONSE = AnyOf(
    dict({'environment_id': int,}, **AUTHORIZED_RESPONSE_STATUS_OK),
    AUTHORIZED_RESPONSE_STATUS_ERROR
)

MODIFY_ENVIRONMENT_REQUEST = dict(
    {
        'new_name': Text(),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_ENVIRONMENT_RESPONSE = RESPONSE_STATUS_ONLY

ADD_USER_REQUEST = dict(
    {
        'login': Text(),
        'password': Text(),
        Optional('role'): AnyOf(dataobject.User.ROLE_SUPER, dataobject.User.ROLE_USER),
        Optional('is_active'): bool,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_USER_RESPONSE = AnyOf(
    dict({'user_id': int,}, **RESPONSE_STATUS_OK),
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

ADD_SERVICE_RESPONSE = AnyOf(
    dict({'service_id': int,}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

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
            Optional('services_ids'): [int],
            Optional('services_types'): [Text()],
            Optional('is_active'): bool
        },
        'paging_params': REQUEST_PAGING_PARAMS,
        Optional('ordering_params'): [AnyOf('name', '-name', 'id', '-id')]
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
        'service_id': int,
        Optional('new_name'): Text(),
        Optional('new_properties'): [Text()],
        Optional('new_is_active'): bool,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_SERVICE_RESPONSE = RESPONSE_STATUS_ONLY

MODIFY_USERS_RIGHTS_REQUEST = dict(
    {
        'subject_users_ids': [int],
        'rights': [{'service_id': int, 'properties': ArbitraryDict()}],# {Text(): bool}}],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

MODIFY_USER_RIGHTS_RESPONSE = RESPONSE_STATUS_ONLY


CHECK_ACCESS_REQUEST = dict(
    {
        Optional('service_id'): int,
        'service_type': Text(),
        'property': Text(),
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

CHECK_ACCESS_RESPONSE = RESPONSE_STATUS_ONLY


unauthorized_actions = ('ping', 'get_api_actions', 'add_environment',
    'get_authorized_api_actions', 'login')


protocol = [

    ApiCall('ping_request', Scheme(PING_REQUEST)),
    ApiCall('ping_response', Scheme(PING_RESPONSE)),

    ApiCall('get_api_actions_request', Scheme(GET_API_ACTIONS_REQUEST)),
    ApiCall('get_api_actions_response', Scheme(GET_API_ACTIONS_RESPONSE)),

    ApiCall('get_authorized_api_actions_request', Scheme(GET_API_ACTIONS_REQUEST)),
    ApiCall('get_authorized_api_actions_response', Scheme(GET_API_ACTIONS_RESPONSE)),

    # login user
    ApiCall('login_request', Scheme(LOGIN_REQUEST)),
    ApiCall('login_response', Scheme(LOGIN_RESPONSE)),

    # environment
    ApiCall('add_environment_request', Scheme(ADD_ENVIRONMENT_REQUEST)),
    ApiCall('add_environment_response', Scheme(ADD_ENVIRONMENT_RESPONSE)),

    ApiCall('modify_environment_request', Scheme(MODIFY_ENVIRONMENT_REQUEST)),
    ApiCall('modify_environment_response', Scheme(MODIFY_ENVIRONMENT_RESPONSE)),

    # user
    ApiCall('add_user_request', Scheme(ADD_USER_REQUEST)),
    ApiCall('add_user_response', Scheme(ADD_USER_RESPONSE)),

    # service
    ApiCall('add_service_request', Scheme(ADD_SERVICE_REQUEST)),
    ApiCall('add_service_response', Scheme(ADD_SERVICE_RESPONSE)),

    ApiCall('modify_service_request', Scheme(MODIFY_SERVICE_REQUEST)),
    ApiCall('modify_service_response', Scheme(MODIFY_SERVICE_RESPONSE)),

    ApiCall('get_services_request', Scheme(GET_SERVICES_REQUEST)),
    ApiCall('get_services_response', Scheme(GET_SERVICES_RESPONSE)),

    # user rights
    ApiCall('modify_users_rights_request', Scheme(MODIFY_USERS_RIGHTS_REQUEST)),
    ApiCall('modify_users_rights_response', Scheme(MODIFY_USER_RIGHTS_RESPONSE)),

    # check access
    ApiCall('check_access_request', Scheme(CHECK_ACCESS_REQUEST)),
    ApiCall('check_access_response', Scheme(CHECK_ACCESS_RESPONSE)),
]
