from helixcore.misc.log import init_logger
from settings import log_filename, log_level, log_console, log_format


logger = init_logger('helixbilling', log_filename, log_level,
    log_console=log_console, log_format=log_format
)
