# -*- coding: utf-8 -*-

from Util.LogHandler import LogHandler


# noinspection PyPep8Naming
def testLogHandler():
    """
    test function LogHandler  in Util/LogHandler
    :return:
    """
    log = LogHandler('test')
    log.info('this is a log from test')

    log.resetName(name='test1')
    log.info('this is a log from test1')

    log.resetName(name='test2')
    log.info('this is a log from test2')


if __name__ == '__main__':
    testLogHandler()
