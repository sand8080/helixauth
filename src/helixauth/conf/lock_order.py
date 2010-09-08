from helixcore.db import deadlock_detector
from helixauth.db import dataobject #@UnusedImport


deadlock_detector.ALLOWED_TRANSITIONS = [
    (dataobject.Environment, dataobject.User, dataobject.Session), # add environment
#    (objects.Balance.table, objects.Balance.table), #lock list
#    (objects.BalanceLock.table, objects.BalanceLock.table), #unlock list
]
