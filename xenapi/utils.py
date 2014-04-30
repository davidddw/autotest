#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Created on 2014-4-3
# @author: david_dong

import os
import logging
import traceback
from logging.handlers import RotatingFileHandler

__all__ = ['CloudLog']

DEBUG = 1
INFO = 2
WARN = 3
ERROR = 4
FATAL = 5

def get_parent_path():
    current_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(os.path.join(current_path, os.pardir))

# Singleton implements\

def read_conf_from_conf(filename, option, item):
    import ConfigParser 
    cf = ConfigParser.ConfigParser()    
    cf.read(filename)      
    return cf.get(option, item)    

class Singleton(object):
    _instance = None
    _name = 'Singleton'
  
    def __new__(cls, *args, **kwargs):
        if (not cls._instance):
            cls._instance = super(Singleton, cls).__new__(cls)
        else:
            cls.__init__ = cls.__doNothing
        return cls._instance

    def __doNothing(self, *args):
        '''
        This method do nothing. is used to override the __init__ method
        and then, do not re-declare values that may be declared at first
        use of __init__ (When no instance was made).
        '''
        pass

    def set_name(self, value='Singleton'):
        self._name = value

    # Returns name of the class
    def get_name(self):
        return self._name

    def get_id(self):
        """
        Returns singleton Id
        """
        return id(self)

class CloudLog(Singleton):

    def __init__(self, logger_name, filename, loglevel):
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
                    '%(asctime)s %(levelname)s - %(funcName)s - %(message)s')
        logFileName = os.path.join(check_dir_exist('logs'), filename)
        file_handler = RotatingFileHandler(logFileName,
                                     maxBytes=2000000, backupCount=9)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(loglevel)
        #formatter = logging.Formatter('%(name)-12s: %(levelname)
        #-8s %(message)s')
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def __fmtInfo(self, msg):
        if len(msg) == 0:
            msg = traceback.format_exc().strip()
            return '\n' + msg
        else:
            __tmp = [msg[0]]
            return '\n'.join([str(i) for i in __tmp])

    def critical(self, *msg):
        __info = self.__fmtInfo(msg)
        try:
            self._logger.critical(__info)
        except:
            print 'mylog critical:' + __info

    def error(self, *msg):
        __info = self.__fmtInfo(msg)

        try:
            self._logger.error(__info)
        except:
            print 'mylog error:' + __info

    def warning(self, *msg):
        __info = self.__fmtInfo(msg)
        try:
            self._logger.warning(__info)
        except:
            print 'mylog warning:' + __info

    def info(self, *msg):
        __info = self.__fmtInfo(msg)
        try:
            self._logger.info(__info)
        except:
            print 'mylog info:' + __info

    def debug(self, *msg):
        __info = self.__fmtInfo(msg)
        try:
            self._logger.debug(__info)
        except:
            print 'mylog debug:' + __info

    def exception(self, *msg):
        __info = self.__fmtInfo(msg)
        try:
            self._logger.exception(__info)
        except:
            print 'mylog debug:' + __info