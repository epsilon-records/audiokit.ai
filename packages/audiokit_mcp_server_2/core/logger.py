import logging


# Set up a logger with basic configuration.
logger = logging.getLogger("audiokit_mcp_server")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)
