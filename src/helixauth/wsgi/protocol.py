from helixcore.server.api import ApiCall
from helixcore.json_validator import (Optional, AnyOf, NonNegative,
    Scheme, Text, ArbitraryDict, NullableText)


RESPONSE_STATUS_OK = {'status': 'ok'}

PAGING_PARAMS = {
    Optional('limit'): NonNegative(int),
    Optional('offset'): NonNegative(int),
}

RESPONSE_STATUS_ERROR = {
    'status': 'error',
    'category': Text(),
    'message': Text(),
    'details': [ArbitraryDict()],
}

RESPONSE_STATUS_ONLY = AnyOf(RESPONSE_STATUS_OK, RESPONSE_STATUS_ERROR)

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

ADD_ENVIRONMENT_REQUEST = {
    'name': Text(),
    'su_login': Text(),
    'su_password': Text(),
    Optional('custom_user_info'): NullableText(),
}

ADD_ENVIRONMENT_RESPONSE = RESPONSE_STATUS_ONLY


protocol = [
    ApiCall('ping_request', Scheme(PING_REQUEST)),
    ApiCall('ping_response', Scheme(PING_RESPONSE)),

    ApiCall('get_api_actions_request', Scheme(GET_API_ACTIONS_REQUEST)),
    ApiCall('get_api_actions_response', Scheme(GET_API_ACTIONS_RESPONSE)),

    ApiCall('get_authorized_api_actions_request', Scheme(GET_API_ACTIONS_REQUEST)),
    ApiCall('get_authorized_api_actions_response', Scheme(GET_API_ACTIONS_RESPONSE)),

    ApiCall('add_environment_request', Scheme(ADD_ENVIRONMENT_REQUEST)),
    ApiCall('add_environment_response', Scheme(ADD_ENVIRONMENT_RESPONSE)),

#    # currencies
#    ApiCall('view_currencies_request', Scheme(VIEW_CURRENCIES)),
#    ApiCall('view_currencies_response', Scheme(VIEW_CURRENCIES_RESPONSE)),
#
#    # operator
#    ApiCall('add_operator_request', Scheme(ADD_OPERATOR)),
#    ApiCall('add_operator_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('modify_operator_request', Scheme(MODIFY_OPERATOR)),
#    ApiCall('modify_operator_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    # balance
#    ApiCall('add_balance_request', Scheme(ADD_BALANCE)),
#    ApiCall('add_balance_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('modify_balance_request', Scheme(MODIFY_BALANCE)),
#    ApiCall('modify_balance_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('delete_balance_request', Scheme(DELETE_BALANCE)),
#    ApiCall('delete_balance_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('get_balance_request', Scheme(GET_BALANCE)),
#    ApiCall('get_balance_response', Scheme(GET_BALANCE_RESPONSE)),
#
#    ApiCall('view_balances_request', Scheme(VIEW_BALANCES)),
#    ApiCall('view_balances_response', Scheme(VIEW_BALANCES_RESPONSE)),
#
#    # receipt
#    ApiCall('enroll_receipt_request', Scheme(ENROLL_RECEIPT)),
#    ApiCall('enroll_receipt_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_receipts_request', Scheme(VIEW_RECEIPTS)),
#    ApiCall('view_receipts_response', Scheme(VIEW_RECEIPTS_RESPONSE)),
#
#    # bonus
#    ApiCall('enroll_bonus_request', Scheme(ENROLL_BONUS)),
#    ApiCall('enroll_bonus_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_bonuses_request', Scheme(VIEW_BONUSES)),
#    ApiCall('view_bonuses_response', Scheme(VIEW_BONUSES_RESPONSE)),
#
#    # lock
#    ApiCall('balance_lock_request', Scheme(BALANCE_LOCK)),
#    ApiCall('balance_lock_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('balance_lock_list_request', Scheme(BALANCE_LOCK_LIST)),
#    ApiCall('balance_lock_list_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_balance_locks_request', Scheme(VIEW_BALANCE_LOCKS)),
#    ApiCall('view_balance_locks_response', Scheme(VIEW_BALANCE_LOCKS_RESPONSE)),
#
#    # unlock
#    ApiCall('balance_unlock_request', Scheme(BALANCE_UNLOCK)),
#    ApiCall('balance_unlock_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('balance_unlock_list_request', Scheme(BALANCE_UNLOCK_LIST)),
#    ApiCall('balance_unlock_list_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    # chargeoff
#    ApiCall('chargeoff_request', Scheme(CHARGEOFF)),
#    ApiCall('chargeoff_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('chargeoff_list_request', Scheme(CHARGEOFF_LIST)),
#    ApiCall('chargeoff_list_response', Scheme(RESPONSE_STATUS_ONLY)),
#
#    ApiCall('view_chargeoffs_request', Scheme(VIEW_CHARGEOFFS)),
#    ApiCall('view_chargeoffs_response', Scheme(VIEW_CHARGEOFFS_RESPONSE)),
#
#    # order
#    ApiCall('order_status_request', Scheme(ORDER_STATUS)),
#    ApiCall('order_status_response', Scheme(ORDER_STATUS_RESPONSE)),
#
#    ApiCall('view_order_statuses_request', Scheme(VIEW_ORDER_STATUSES)),
#    ApiCall('view_order_statuses_response', Scheme(VIEW_ORDER_STATUSES_RESPONSE)),
#
#    # action log
#    ApiCall('view_action_logs_request', Scheme(VIEW_ACTION_LOGS)),
#    ApiCall('view_action_logs_response', Scheme(VIEW_ACTION_LOGS_RESPONSE)),
]
