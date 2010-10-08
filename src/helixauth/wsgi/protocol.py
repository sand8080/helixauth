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
        'role': AnyOf(dataobject.User.ROLE_SUPER, dataobject.User.ROLE_USER),
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
        'properties': [Text()],
        Optional('is_active'): bool,
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_SERVICE_RESPONSE = RESPONSE_STATUS_ONLY

ADD_USER_RIGHTS_REQUEST = dict(
    {
        'subject_user_id': Text(),
        'rights': [{'service_id': int, 'properties': [Text()]}],
    },
    **AUTHORIZED_REQUEST_AUTH_INFO
)

ADD_SERVICE_RESPONSE = AnyOf(
    dict({'service_id': int,}, **RESPONSE_STATUS_OK),
    RESPONSE_STATUS_ERROR
)

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

    # user rights
]
