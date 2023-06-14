import logging
import os
import socket
from datetime import datetime

logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

time_now = datetime.now()

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

logger.addHandler(console_handler)


def writeLog(data: str, log_level: str = "info") -> None:
    os.system("")

    log_level_map = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error
    }

    time = time_now.strftime("%d/%b/%Y %H:%M:%S")
    clientIp = socket.gethostbyname(socket.gethostname())
    log_func = log_level_map.get(log_level.lower(), logger.info)
    log_func(f"{clientIp} - - [{time}] {data}")

