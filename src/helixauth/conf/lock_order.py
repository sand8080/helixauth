from helixcore.db import deadlock_detector
from helixauth.db import dataobject #@UnusedImport


deadlock_detector.ALLOWED_TRANSITIONS = [
    (dataobject.UserRights.table, dataobject.Session.table), # modify rights
]
