import logging
import logging.handlers

from rostam.main import LOG_FILENAME

# setup logging
logging.getLogger('').setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=100000, backupCount=5)
format = "%(asctime)s %(name)-20s %(levelname)-8s %(message)s"
handler.setFormatter(logging.Formatter(format))
logging.getLogger('').addHandler(handler)

# add handler to python logger as soon as this module is imported
if len(logging.root.handlers) == 0:
    logging.root.addHandler(handler)
