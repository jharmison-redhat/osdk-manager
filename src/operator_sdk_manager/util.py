#!/usr/bin/env python
import click
import logging
import logging.handlers


def make_logger(verbosity: int = None):
    logger = logging.getLogger('operator-sdk-manager')
    logger.setLevel(logging.DEBUG)

    if len(logger.handlers) == 0:
        _format = '{asctime} {name} [{levelname:^9s}]: {message}'
        formatter = logging.Formatter(_format, style='{')

        stderr = logging.StreamHandler()
        stderr.setFormatter(formatter)
        if verbosity is not None:
            stderr.setLevel(40 - (min(3, verbosity) * 10))
        else:
            stderr.setLevel(40)
        logger.addHandler(stderr)

        syslog = logging.handlers.SysLogHandler(address='/dev/log')
        syslog.setFormatter(formatter)
        syslog.setLevel(logging.INFO)
        logger.addHandler(syslog)
    else:
        if verbosity is not None:
            stderr = logger.handlers[0]
            stderr.setLevel(40 - (min(3, verbosity) * 10))

    return logger


def verbose_opt(func):
    return click.option(
        '-v', '--verbose', count=True,
        help='Increase verbosity (specify multiple times for more)'
    )(func)
