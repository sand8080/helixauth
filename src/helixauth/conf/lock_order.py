from helixcore.db import deadlock_detector
from helixauth import dataobject


deadlock_detector.ALLOWED_TRANSITIONS = [
#    (objects.Balance.table, objects.BalanceLock.table), #unlock, chargeoff
#    (objects.Balance.table, objects.Balance.table), #lock list
#    (objects.BalanceLock.table, objects.BalanceLock.table), #unlock list
]
