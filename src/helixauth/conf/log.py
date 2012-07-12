from helixcore.misc.log import init_logger
from settings import log_filename, sess_log_filename, log_level, log_console, log_format


logger = init_logger('helixauth', log_filename, log_level,
    log_console=log_console, log_format=log_format
)

sess_logger = init_logger('helixauth-sess', sess_log_filename, log_level,
    log_console=log_console, log_format=log_format
)
