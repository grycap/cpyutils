import logging

_logsetup = False

class Log:
    '''
    This is a class that try to provide a simple utility to the common logging functions.
      * it tries to automate starting logging and setting the logging level to default (by default)
      * it returns the logging messages to enable more one-liners
    '''
    @staticmethod
    def setup(_filename = None, _loglevel = logging.DEBUG):
        logging.basicConfig(filename=_filename,level=_loglevel)
    
    def __init__(self, name = None, loglevel = logging.DEBUG):
        if name is None:
            self._logger = logging.getLogger()
        else:
            self._logger = logging.getLogger("[%s]" % name)
        self._filename = None
        
        global _logsetup
        if not _logsetup:
            Log.setup()
            _logsetup = True
    
    def setup_log(self, loglevel = logging.DEBUG):
        self._logger.setLevel(loglevel)
        
    def log(self, txt, loglevel = logging.DEBUG):
        if loglevel == logging.DEBUG:
            self._logger.debug(txt)
        elif loglevel == logging.INFO:
            self._logger.info(txt)
        elif loglevel == logging.WARNING:
            self._logger.info(txt)
        elif loglevel == logging.ERROR:
            self._logger.error(txt)
        else:
            self._logger.debug(txt)
        return txt
    
    def debug(self, msg):
        return self.log(msg, logging.DEBUG)
        
    def error(self, msg):
        return self.log(msg, logging.ERROR)

    def warning(self, msg):
        return self.log(msg, logging.WARNING)

    def info(self, msg):
        return self.log(msg, logging.INFO)