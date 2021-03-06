import logging
import sys
from PySide2 import QtCore


class Logger(object):
    LOGGER_NAME = "Logger"

    FORMAT_DEFAULT = "[%(name)s]\t [%(levelname)s]\t %(message)s"

    LEVEL_DEFAULT = logging.INFO
    PROPAGATE_DEFAULT = True

    _logger_obj = None

    @classmethod
    def logger_obj(cls):

        if not cls._logger_obj:
            if cls.logger_exists():
                cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)
            else:
                cls._logger_obj = logging.getLogger(cls.LOGGER_NAME)

                cls._logger_obj.setLevel(cls.LEVEL_DEFAULT)
                cls._logger_obj.propagate = cls.PROPAGATE_DEFAULT

                fmt = logging.Formatter(cls.FORMAT_DEFAULT)

                stream_handler = logging.StreamHandler(sys.stderr)
                stream_handler.setFormatter(fmt)
                cls._logger_obj.addHandler(stream_handler)

        return cls._logger_obj

    @classmethod
    def logger_exists(cls):
        return cls.LOGGER_NAME in logging.Logger.manager.loggerDict.keys()

    @classmethod
    def set_level(cls, level):
        lg = cls.logger_obj()
        lg.setLevel(level)

    @classmethod
    def set_propagate(cls, propagate):
        lg = cls.logger_obj()
        lg.propagate = propagate

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.critical(msg, *args, **kwargs)

    @classmethod
    def log(cls, level, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.log(level, msg, *args, **kwargs)

    @classmethod
    def exception(cls, msg, *args, **kwargs):
        lg = cls.logger_obj()
        lg.exception(msg, *args, **kwargs)

    @classmethod
    def write_to_file(cls, path, level=logging.WARNING):
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(level)

        fmt = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
        file_handler.setFormatter(fmt)

        lg = cls.logger_obj()
        lg.addHandler(file_handler)


class MayaLogger(Logger):
    LOGGER_NAME = "MayaLogger"
    PROPAGATE_DEFAULT = False


class EdenLogger(MayaLogger):
    LOGGER_NAME = "Eden"
    # FORMAT_DEFAULT = "%(name)s:\t [%(levelname)s]\t %(message)s"
    FORMAT_DEFAULT = "{:15}[{:10}]\t{}".format("%(name)s", "%(levelname)s", "%(message)s")


class QtSignaler(QtCore.QObject):
    message_logged = QtCore.Signal(str)


class QtSignalHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super(QtSignalHandler, self).__init__(*args, **kwargs)
        self.emitter = QtSignaler()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.message_logged.emit(msg)


class QtLogger(MayaLogger):
    LOGGER_NAME = "QtLogger"

    _signal_handler = None

    @classmethod
    def logger_obj(cls):
        if not cls.logger_exists():
            fmt = logging.Formatter("[%(levelname)s]\t %(message)s")

            cls._signal_handler = QtSignalHandler()
            cls._signal_handler.setFormatter(fmt)

            logger_obj = super(QtLogger, cls).logger_obj()
            logger_obj.addHandler(cls._signal_handler)

        return super(QtLogger, cls).logger_obj()

    @classmethod
    def signal_handler(cls):
        cls.logger_obj()
        return cls._signal_handler
