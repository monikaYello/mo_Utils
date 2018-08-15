import logging
import sys

logger = logging.getLogger('root')
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logger.setLevel(logging.DEBUG)

getframe_expr = 'sys._getframe({}).f_code.co_name'
def log_debug(msg='caller'):
	logger.debug('%s: %s' % (eval(getframe_expr.format(2)), msg))
def log_info(msg='caller'):
	logger.info('%s: %s' % (eval(getframe_expr.format(2)), msg))


'''
# this will give current funtion we are in
log_debug('Enter: %s' % eval(getframe_expr.format(1)))
'''