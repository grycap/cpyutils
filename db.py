# coding: utf-8
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2015 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import logging
import hashlib
import re
import os

try:
    import sqlite3 as sqlite
    _sqlite_available=True
except:
    _sqlite_available=False
    
try:
    import MySQLdb as mdb
    _mysqldb_available=True
except:
    _mysqldb_available=False

_LOGGER=logging.getLogger("[DB]")
_LOGGER.disabled = True

class MalformedConnectionString(Exception): pass
class UnknownDBDriver(Exception): pass
class MissingDBName(Exception): pass
class DBConnectionError(Exception): pass
class InvalidDBFile(Exception): pass
class MissingLibrary(Exception): pass

connection_parameters = {
    'driver': 'mysql',
    'user': 'username',
    'password': 'passwd',
    'host': 'localhost',
    'path': '',
    'db': '',
}

class DB():
    def sql_query(self, query, commit = False):
        return False, 0, None
    
    def commit(self):
        pass

    @staticmethod
    def create_from_connection_parameters(conn_p):
        if conn_p['driver'] == 'mysql':
            return DB_mysql(conn_p['user'], conn_p['password'], conn_p['host'], int(conn_p['port']), conn_p['db'])
        if conn_p['driver'] == 'sqlite':
            return DB_sqlite(conn_p['path'])
        raise UnknownDBDriver(conn_p['driver'])

    @staticmethod
    def create_from_string(connection_string):
        connection_parameters = None
        
        r=re.match("mysql://(?:(?P<user>([^:]+|\"[^\"]*\"|'[^']*'))(?::(?P<passwd>(\"[^\"]*\"|'[^']*'|[^@]*))|)@|)(?P<host>[a-zA-Z0-9][a-zA-Z0-9\-\.]*)(?::(?P<port>[0-9]+)|)(?:/|/(?P<db>.+)|)$",connection_string)
        if r is not None:
            connection_parameters = { 'driver': 'mysql' }
            (connection_parameters['user'], connection_parameters['password'], connection_parameters['host'], connection_parameters['port'], connection_parameters['db'], ) = (r.group('user'), r.group('passwd'), r.group('host'), r.group('port'), r.group('db'))

            if connection_parameters['db'] is None or connection_parameters['db'] == "":
                raise MalformedConnectionString("Missing DB Name")

            if connection_parameters['port'] is None or connection_parameters['port'] == "":
                connection_parameters['port'] = 3306

            return DB.create_from_connection_parameters(connection_parameters)
        
        r=re.match("sqlite://(?P<path>[^\\\].+)$",connection_string)
        if r is not None:
            connection_parameters = {'driver': 'sqlite'}
            (connection_parameters['path']) = (r.group('path'))
        
        if connection_parameters is not None:
            return DB.create_from_connection_parameters(connection_parameters)
        
        raise MalformedConnectionString("Connection string format not recognised")
        return None

class DB_sqlite(DB):
    def __init__(self, path):
        if not _sqlite_available:
            raise MissingLibrary("sqlite python library is needed. Try apt-get install python-sqlite or similar.")
        
        self._path = os.path.expanduser(path)
        path = os.path.abspath(path)
        if os.path.isfile(path):
            return
        else:
            d = os.path.dirname(path)
            if os.path.isdir(d):
                return
        raise InvalidDBFile("file %s neither exist or contains a valid directory" % path)

    def connect(self):
        try:
            self._db = sqlite.connect(self._path)
        except Exception as e:
            raise DBConnectionError("error connecting to database (%s)" % str(e))

    def commit(self):
        try:
            connection = sqlite.connect(self._path)
            connection.commit()
        except Exception, e:
            raise e
            _LOGGER.debug("error")
            return False
        return True

    def sql_query(self, query, commit = False):
        _LOGGER.debug("executing query: %s " % query)
        connection = None
        try:
            connection = sqlite.connect(self._path)
            cursor = connection.cursor()
            cursor.execute(query)
            if commit:
                connection.commit()
            
            # rowcount = cursor.rowcount()
            rows = cursor.fetchall()
            rowcount = len(rows)
            
            return True, rowcount, rows
        except Exception, e:
            if connection is not None:
                connection.close()
            if commit:
                raise e
            _LOGGER.debug("error")
            return False, 0, None

class DB_mysql(DB):
    def __init__(self, user, passwd, host, port, db):
        if not _mysqldb_available:
            raise MissingLibrary("MySQLdb python library is needed. Try apt-get install python-mysqldb or similar.")

        self._user = user
        self._passwd = passwd
        if (host is None) or (host == ""): host = "localhost"
        self._host = host
        if (port is None) or (port == 0): port = 3306
        self._port = port
        self._dbname = db
        
    def connect(self):
        try:
            self._db = mdb.connect(host=self._host, port=self._port, user=self._user, passwd = self._passwd, db = self._dbname)
        except Exception as e:
            raise DBConnectionError("error connecting to database (%s)" % str(e))
    
    def sql_query(self, query, commit = False):
        # _LOGGER.debug("executing query: %s " % query)
        connection = None
        try:
            connection = mdb.connect(host=self._host, port=self._port, user=self._user, passwd = self._passwd, db = self._dbname)
            cursor = connection.cursor()
            cursor.execute(query)
            if commit:
                connection.commit()
                
            rowcount = cursor.rowcount
            
            rows = cursor.fetchall()
            return True, rowcount, rows
        except Exception, e:
            if connection is not None:
                connection.close()
            if commit:
                raise e

            return False, 0, None
