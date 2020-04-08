import logging
import sys

log = logging.getLogger('amv')
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
log.addHandler(ch)


def debug_print(message):
    log.debug(message)


def error_print(message):
    log.error(message)
